import httpx
import base64
import asyncio

async def main():
    headers = {
        "apikey": "MySuperSecretKey123!",
        "Content-Type": "application/json"
    }
    
    # Step 1: Create instance
    print("Creating instance 'callinggen_default'...")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "http://localhost:8080/instance/create",
                headers=headers,
                json={"instanceName": "callinggen_default", "qrcode": True, "integration": "WHATSAPP-BAILEYS"}
            )
            print("Create Response:", res.status_code)
    except Exception as e:
        print("Could not create instance (it might already exist):", e)

    # Step 2: Fetch QR code
    print("Fetching QR Code...")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                "http://localhost:8080/instance/connect/callinggen_default",
                headers=headers
            )
            
            data = res.json()
            if "base64" in data:
                # Remove the "data:image/png;base64," prefix
                b64_string = data["base64"].split(",")[1]
                
                # Save as an image file
                with open("whatsapp_qr.png", "wb") as fh:
                    fh.write(base64.b64decode(b64_string))
                print("\nSUCCESS! Saved QR code to 'whatsapp_qr.png' in the BACKEND folder.")
                print("Please open 'whatsapp_qr.png' and scan it with your phone to connect.")
            else:
                print("\nResponse did not contain a new QR Code. It might already be connected.")
                print("Status:", data)
    except Exception as e:
        print("Error fetching QR Code:", e)

if __name__ == "__main__":
    asyncio.run(main())
