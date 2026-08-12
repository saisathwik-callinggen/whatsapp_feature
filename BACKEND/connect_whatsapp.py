import asyncio
import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "MySuperSecretKey123!")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "callinggen_default")

HEADERS = {
    "apikey": EVOLUTION_API_KEY,
    "Content-Type": "application/json"
}

async def create_and_connect():
    print(f"Checking Evolution API at {EVOLUTION_API_URL}...")
    
    # Check status
    try:
        async with httpx.AsyncClient() as client:
            status_url = f"{EVOLUTION_API_URL}/instance/connectionState/{EVOLUTION_INSTANCE_NAME}"
            res = await client.get(status_url, headers=HEADERS)
            
            if res.status_code == 200:
                data = res.json()
                state = data.get("instance", {}).get("state")
                if state == "open":
                    print(f"✅ Instance '{EVOLUTION_INSTANCE_NAME}' is already connected!")
                    return
                elif state == "connecting":
                    print(f"⚠️ Instance '{EVOLUTION_INSTANCE_NAME}' is currently connecting...")
            else:
                print(f"Instance '{EVOLUTION_INSTANCE_NAME}' not found or disconnected. Creating...")
                # Create instance
                create_url = f"{EVOLUTION_API_URL}/instance/create"
                payload = {
                    "instanceName": EVOLUTION_INSTANCE_NAME,
                    "qrcode": True,
                    "integration": "WHATSAPP-BAILEYS"
                }
                res = await client.post(create_url, json=payload, headers=HEADERS)
                if res.status_code not in [200, 201]:
                    if "already exists" not in res.text:
                        print(f"Failed to create instance: {res.text}")
                        return
    except Exception as e:
        print(f"Error checking/creating instance: {e}")
        print(f"Is Evolution API running on {EVOLUTION_API_URL}?")
        return

    print("Fetching QR Code...")
    try:
        async with httpx.AsyncClient() as client:
            connect_url = f"{EVOLUTION_API_URL}/instance/connect/{EVOLUTION_INSTANCE_NAME}"
            res = await client.get(connect_url, headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                base64_qr = data.get("base64")
                if base64_qr:
                    # Remove the data:image/png;base64, prefix if present
                    if "," in base64_qr:
                        base64_qr = base64_qr.split(",")[1]
                    
                    img_data = base64.b64decode(base64_qr)
                    with open("whatsapp_qr.png", "wb") as f:
                        f.write(img_data)
                    print(f"✅ QR Code saved to 'whatsapp_qr.png'. Open this file and scan it with WhatsApp!")
                else:
                    print(f"No QR code returned. Current state: {data.get('instance', {}).get('state')}")
            else:
                print(f"Failed to get QR code: {res.text}")
    except Exception as e:
        print(f"Error fetching QR code: {e}")

if __name__ == "__main__":
    asyncio.run(create_and_connect())
