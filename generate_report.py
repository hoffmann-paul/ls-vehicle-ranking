import os
import requests
from bs4 import BeautifulSoup

# Zugangsdaten kommen aus Umgebungsvariablen (als GitHub Secrets gesetzt),
# NIEMALS Passwort direkt in den Code schreiben!
USERNAME = os.environ["LSP_USERNAME"]
PASSWORD = os.environ["LSP_PASSWORD"]

session = requests.Session()

# 1. Login-Seite holen, Token extrahieren
login_page = session.get("https://www.leitstellenspiel.de/users/sign_in")
soup = BeautifulSoup(login_page.text, "html.parser")
csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]

# 2. Einloggen mit Token
session.post("https://www.leitstellenspiel.de/users/sign_in", data={
    "user[email]": USERNAME,
    "user[password]": PASSWORD,
    "authenticity_token": csrf_token
})

# 3. API-Endpoint abrufen
response = session.get("https://www.leitstellenspiel.de/api/vehicles/")
missons = session.get("https://www.leitstellenspiel.de/api/v1/vehicle_distances")
vehicles_response = session.get("https://www.leitstellenspiel.de/api/vehicle_states")
distances = missons.json()
vehicles = response.json()
vehicle_fms_summary = vehicles_response.json()

stats = []

for i in vehicles:
    for a in distances["result"]:
        if a["vehicle_id"] == i["id"]:
            entry = {
                "caption": i["caption"],
                "distance": round(a["distance_km"], 2)
            }
            stats.append(entry)

stats_sorted = sorted(stats, key=lambda x: x["distance"], reverse=True)

fms_summary = "\n".join(
    f"""<p>FMS 1: {str(vehicle_fms_summary["1"])}</p>
    <p>FMS 2: {str(vehicle_fms_summary["2"])}</p>
    <p>FMS 3: {str(vehicle_fms_summary["3"])}</p>
    <p>FMS 4: {str(vehicle_fms_summary["4"])}</p>
    <p>FMS 5: {str(vehicle_fms_summary["5"])}</p>
    <p>FMS 6: {str(vehicle_fms_summary["6"])}</p>
    <p>FMS 7: {str(vehicle_fms_summary["7"])}</p>
    """
)

# 4. HTML statt print() erzeugen, damit GitHub Pages es anzeigen kann
rows = "\n".join(
    f"<tr><td>{idx + 1}</td><td>{s['caption']}</td><td>{s['distance']} km</td></tr>"
    for idx, s in enumerate(stats_sorted)
)

html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fahrzeug-Rangliste</title>
<style>
  body {{ font-family: sans-serif; margin: 0; padding: 1rem; background: #f5f5f5; }}
  h1 {{ font-size: 1.3rem; }}
  table {{ width: 100%; border-collapse: collapse; background: white; }}
  th, td {{ padding: 0.5rem; text-align: left; border-bottom: 1px solid #ddd; }}
  th {{ background: #333; color: white; }}
  tr:nth-child(even) {{ background: #fafafa; }}
</style>
</head>
<body>
<h1>FMS-Status Zusammenfassung</h1>
{fms_summary}
<h1>Fahrzeug-Rangliste (nach gefahrenen km)</h1>
<table>
<tr><th>#</th><th>Fahrzeug</th><th>Distanz</th></tr>
{rows}
</table>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
