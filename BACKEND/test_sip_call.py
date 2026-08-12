import asyncio
from dotenv import load_dotenv
load_dotenv()
from app.services.livekit_service import make_livekit_call

async def main():
    print("Attempting to make a SIP call via LiveKit...")
    result = await make_livekit_call(phone="+919876543210", room_name="test-call-123")
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
