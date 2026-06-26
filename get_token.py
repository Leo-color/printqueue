"""
Run this ONCE on your PC to get your Bambu token.
Then save BAMBU_TOKEN and BAMBU_UID as Render env vars.
"""
import requests

email = input("Email Bambu: ").strip()
password = input("Password Bambu: ").strip()

r = requests.post("https://bambulab.com/api/sign-in/form", json={
    "account": email, "password": password, "apiError": ""
})
data = r.json()
print(f"\nRisposta: {data}\n")

token = data.get("accessToken") or data.get("token", "")
if not token:
    print("Login fallito — controlla email e password")
    exit(1)

r2 = requests.get("https://api.bambulab.com/v1/user-service/my/profile",
    headers={"Authorization": f"Bearer {token}"})
uid = str(r2.json().get("uid", ""))

print("=" * 50)
print(f"BAMBU_TOKEN = {token}")
print(f"BAMBU_UID   = {uid}")
print("=" * 50)
print("\nCopia questi valori nelle variabili d'ambiente di Render!")
