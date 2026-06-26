"""
Bambu Lab cloud communication via MQTT.
Authentication via Bambu account (email + password).
Works from anywhere — no local network required.
"""

import json
import ssl
import time
import threading
import requests
import paho.mqtt.client as mqtt

# Cloud endpoints
AUTH_URL = "https://bambulab.com/api/sign-in/form"
PROFILE_URL = "https://api.bambulab.com/v1/user-service/my/profile"
CLOUD_MQTT_HOST = "us.mqtt.bambulab.com"
CLOUD_MQTT_PORT = 8883

MQTT_TOPIC_REPORT = "device/{serial}/report"
MQTT_TOPIC_REQUEST = "device/{serial}/request"

# G-code injected at end of every print to eject the piece
# Sequence:
#   1. Wait cooldown (cooling)
#   2. Raise Z above piece
#   3. Move nozzle center-back of plate
#   4. Lower nozzle just below piece top
#   5. Slowly push piece toward front edge (falls off)
#   6. Home
EJECT_GCODE = """; === AUTO EJECT SEQUENCE ===
M400
M104 S0
M140 S0
G4 P{cooldown_ms}
G28 Z
G1 Z15 F600
G1 X{center_x} Y{back_y} F6000
G1 Z{push_z} F300
G1 Y{front_y} F300
G1 Y{back_y} F6000
G28 X Y
; === END EJECT ===
"""


class BambuCloud:
    def __init__(self, email: str, password: str, serial: str):
        self.email = email
        self.password = password
        self.serial = serial
        self.token = None
        self.uid = None
        self._client = None
        self.connected = False
        self.status = {}
        self._lock = threading.Lock()
        self._on_status_change = None

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self) -> tuple[bool, str]:
        """Login to Bambu cloud. Returns (success, error_message)."""
        try:
            r = requests.post(AUTH_URL, json={
                "account": self.email,
                "password": self.password,
                "apiError": ""
            }, timeout=15)
            print(f"Auth response: {r.status_code} — {r.text[:300]}")

            if r.status_code != 200:
                return False, f"Auth HTTP {r.status_code}: {r.text[:200]}"

            data = r.json()

            # Bambu sometimes returns loginType=verifyCode (needs 2FA)
            if data.get("loginType") == "verifyCode":
                return False, "Bambu richiede verifica email (2FA) — disabilita 2FA su bambulab.com"

            self.token = data.get("accessToken") or data.get("token")
            if not self.token:
                return False, f"Token non trovato nella risposta: {list(data.keys())}"

            r2 = requests.get(PROFILE_URL, headers={
                "Authorization": f"Bearer {self.token}"
            }, timeout=10)
            print(f"Profile response: {r2.status_code} — {r2.text[:200]}")
            profile = r2.json()
            self.uid = str(profile.get("uid", ""))
            if not self.uid:
                return False, f"UID non trovato nel profilo: {list(profile.keys())}"
            return True, "ok"
        except Exception as e:
            return False, str(e)

    # ── MQTT ──────────────────────────────────────────────────────────────────

    def connect_mqtt(self) -> bool:
        if not self.token or not self.uid:
            ok, err = self.login()
            if not ok:
                print(f"MQTT login failed: {err}")
                return False

        client = mqtt.Client(client_id=f"printqueue_{self.uid}", protocol=mqtt.MQTTv311)
        client.username_pw_set(f"u_{self.uid}", self.token)

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        client.tls_set_context(ctx)

        topic = MQTT_TOPIC_REPORT.format(serial=self.serial)
        client.on_connect = lambda c, u, f, rc: (
            c.subscribe(topic) if rc == 0 else print(f"MQTT connect failed: {rc}")
        )
        client.on_message = self._on_message
        client.on_disconnect = lambda c, u, rc: setattr(self, "connected", False)

        client.connect(CLOUD_MQTT_HOST, CLOUD_MQTT_PORT, keepalive=60)
        client.loop_start()
        self._client = client
        self.connected = True
        return True

    def disconnect(self):
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
        self.connected = False

    def _on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
            with self._lock:
                if "print" in data:
                    self.status.update(data["print"])
                    if self._on_status_change:
                        self._on_status_change(dict(self.status))
        except Exception:
            pass

    def _publish(self, payload: dict):
        topic = MQTT_TOPIC_REQUEST.format(serial=self.serial)
        self._client.publish(topic, json.dumps(payload))

    def get_status(self) -> dict:
        with self._lock:
            return dict(self.status)

    def send_gcode(self, lines: list[str]):
        for line in lines:
            line = line.strip()
            if line and not line.startswith(";"):
                self._publish({"print": {"command": "gcode_line", "param": line, "sequence_id": "0"}})
                time.sleep(0.1)

    def start_print_from_url(self, gcode_url: str):
        """Tell printer to download and print a gcode file from a URL."""
        self._publish({
            "print": {
                "command": "project_file",
                "param": "Metadata/plate_1.gcode",
                "url": gcode_url,
                "bed_type": "auto",
                "timelapse": False,
                "bed_leveling": True,
                "flow_cali": False,
                "vibration_cali": False,
                "layer_inspect": False,
                "use_ams": False,
                "sequence_id": "0",
            }
        })

    # ── G-code modification ────────────────────────────────────────────────────

    @staticmethod
    def inject_eject_gcode(
        gcode_path: str,
        plate_x_mm: float = 256.0,
        plate_y_mm: float = 256.0,
        cooldown_seconds: int = 300,
        piece_height_mm: float = 5.0,
    ) -> str:
        from pathlib import Path

        center_x = plate_x_mm / 2
        back_y = plate_y_mm - 2
        front_y = 2
        push_z = max(piece_height_mm - 2, 1)
        cooldown_ms = cooldown_seconds * 1000

        eject = EJECT_GCODE.format(
            cooldown_ms=int(cooldown_ms),
            center_x=center_x,
            back_y=back_y,
            push_z=push_z,
            front_y=front_y,
        )

        path = Path(gcode_path)
        out_path = path.parent / (path.stem + "_autoqueue" + path.suffix)

        with open(gcode_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if "M84" in content:
            content = content.replace("M84", eject + "\nM84", 1)
        else:
            content += "\n" + eject

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(out_path)

    @staticmethod
    def extract_piece_height(gcode_path: str) -> float:
        max_z = 5.0
        try:
            with open(gcode_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.startswith("G1") and "Z" in line:
                        for p in line.split():
                            if p.startswith("Z"):
                                try:
                                    max_z = max(max_z, float(p[1:]))
                                except ValueError:
                                    pass
        except Exception:
            pass
        return max_z
