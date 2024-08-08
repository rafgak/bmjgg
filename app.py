import requests
import time
import json

# URL API BMKG dan Webhook Discord
BMKG_API_URL = "https://data.bmkg.go.id/DataMKG/TEWS/{endpoint}"
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1242098982780403713/HOmEm3GthCvj37EQl5Jdf6TMYC6PdRwraq3GRuNE8NmLV3hujsJxbBrED-LKAYvx0HO-'

# ID gempa terakhir yang dikirim
last_gempa_id = '1271017318620729385'

def fetch_data(endpoint):
    try:
        response = requests.get(BMKG_API_URL.format(endpoint=endpoint))
        response.raise_for_status()
        data = response.json()

        print(f"Data fetched: {json.dumps(data, indent=2)}")

        if isinstance(data.get('Infogempa', {}).get('gempa'), list):
            gempa_data = data['Infogempa']['gempa']
        elif data.get('Infogempa', {}).get('gempa'):
            gempa_data = [data['Infogempa']['gempa']]
        else:
            print("Data tidak sesuai dengan format yang diharapkan")
            return None

        return gempa_data

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def send_discord_notification(gempa, shakemap_url):
    message = {
        "embeds": [
            {
                "title": "🚨 Peringatan Gempa Terbaru 🚨",
                "fields": [
                    {"name": "Tanggal", "value": gempa.get('Tanggal', 'Tidak Diketahui'), "inline": True},
                    {"name": "Waktu", "value": gempa.get('Jam', 'Tidak Diketahui'), "inline": True},
                    {"name": "Magnitude", "value": gempa.get('Magnitude', 'Tidak Diketahui'), "inline": True},
                    {"name": "Kedalaman", "value": f"{gempa.get('Kedalaman', 'Tidak Diketahui')} km", "inline": True},
                    {"name": "Koordinat", "value": f"{gempa.get('Lintang', 'Tidak Diketahui')}, {gempa.get('Bujur', 'Tidak Diketahui')}", "inline": True},
                    {"name": "Wilayah", "value": gempa.get('Wilayah', 'Tidak Diketahui'), "inline": True},
                    {"name": "Potensi Tsunami", "value": gempa.get('Potensi', 'Tidak Diketahui'), "inline": True},
                ],
                "image": {"url": shakemap_url or ''},
                "color": 0xFF0000  # Red color
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        response.raise_for_status()
        print("Notification sent to Discord")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def check_and_notify(endpoint='autogempa.json'):
    global last_gempa_id

    gempa_data = fetch_data(endpoint)
    if not gempa_data:
        return

    latest_gempa = gempa_data[0]

    shakemap_url = None
    if latest_gempa.get('Shakemap'):
        shakemap_url = f"https://data.bmkg.go.id/DataMKG/TEWS/{latest_gempa['Shakemap']}"

    if latest_gempa.get('Id') != last_gempa_id:
        send_discord_notification(latest_gempa, shakemap_url)
        last_gempa_id = latest_gempa.get('Id')

if __name__ == "__main__":
    while True:
        check_and_notify()
        time.sleep(60)  # Tunggu 60 detik sebelum cek lagi
