import json
import base64
import requests

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}

def safe_json(resp):
    txt = (resp.text or "").strip()
    if not txt or txt.startswith("<"):
        return {}
    try:
        return resp.json()
    except Exception:
        return {}

def token_from(resp, jdata, sess):
    """Token can be in JSON body OR in Set-Cookie."""
    t = jdata.get("accessToken", "")
    if t:
        return t
    for name in ("token", "accessToken"):
        if name in sess.cookies:
            return sess.cookies.get(name)
    return ""

email = input("Email Bambu: ").strip()
password = input("Password Bambu: ").strip()

s = requests.Session()
s.headers.update(HEADERS)

# Step 1 — login con password.
# Se l'account ha la verifica, QUESTA chiamata invia gia' il codice via email.
r = s.post("https://bambulab.com/api/sign-in/form",
    json={"account": email, "password": password, "apiError": ""}, timeout=20)
data = safe_json(r)
print(f"\n[login] status={r.status_code} -> {data if data else r.text[:160]}")

token = token_from(r, data, s)

# Step 2 — verifica con il codice arrivato da QUELLA email (la piu' recente)
if not token and data.get("loginType") == "verifyCode":
    print("\n>>> Apri l'email Bambu arrivata ADESSO (dopo aver messo la password).")
    print(">>> Usa SOLO quel codice, ignora le email vecchie. <<<")
    code = input("\nInserisci il codice: ").strip()

    rv = s.post("https://bambulab.com/api/sign-in/form",
        json={"account": email, "code": code, "apiError": ""}, timeout=20)
    vdata = safe_json(rv)
    print(f"[verify] status={rv.status_code} -> {vdata if vdata else rv.text[:160]}")
    token = token_from(rv, vdata, s)

if not token:
    print("\n[FALLITO] Nessun token. Rilancia e usa il codice PIU' RECENTE, subito.")
    input("Premi Invio per uscire...")
    raise SystemExit(1)

# Step 3 — UID dal JWT
uid = ""
try:
    p = token.split(".")[1]
    p += "=" * (-len(p) % 4)
    payload = json.loads(base64.urlsafe_b64decode(p))
    username = payload.get("username", "")
    uid = username[2:] if username.startswith("u_") else str(payload.get("uid", ""))
except Exception as e:
    print(f"[warn] decode JWT: {e}")

if not uid:
    rp = s.get("https://api.bambulab.com/v1/user-service/my/profile",
        headers={"Authorization": f"Bearer {token}"})
    uid = str(safe_json(rp).get("uid", ""))

print("\n" + "=" * 60)
print(f"BAMBU_TOKEN = {token}")
print(f"BAMBU_UID   = {uid}")
print("=" * 60)
print("\nCopia questi DUE valori su Render -> Environment, poi redeploy.")
input("Premi Invio per uscire...")
