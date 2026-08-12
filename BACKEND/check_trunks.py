import asyncio
import os
from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import ListSIPOutboundTrunkRequest

load_dotenv()

async def main():
    lkapi = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )
    
    try:
        outbound_res = await lkapi.sip.list_outbound_trunk(ListSIPOutboundTrunkRequest())
        print("\n--- OUTBOUND SIP TRUNK DETAILS ---")
        for trunk in outbound_res.items:
            print(f"Trunk ID: {trunk.sip_trunk_id}")
            print(f"  Name: {trunk.name}")
            print(f"  Address: {trunk.address}")
            print(f"  Numbers: {trunk.numbers}")
            print(f"  Auth Username: {trunk.auth_username}")
            print("-" * 40)

    except Exception as e:
        print(f"Error checking SIP trunks: {e}")
    finally:
        await lkapi.aclose()

if __name__ == "__main__":
    asyncio.run(main())
