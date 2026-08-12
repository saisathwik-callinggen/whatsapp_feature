import asyncio
from whatsapp.service import _send_text, send_missed_call_followup

async def main():
    # Replace this with your actual phone number in international format (e.g., 919876543210)
    test_number = input("Enter your phone number with country code (e.g., 919876543210): ")
    
    print(f"\nSending test message to {test_number}...")
    result = await _send_text(test_number, "Hello! This is a test message from CallingGen WhatsApp Integration.")
    print("Result 1:", result)

    print(f"\nSending mock missed call follow-up...")
    result2 = await send_missed_call_followup(test_number, "Test User", "CallingGen")
    print("Result 2:", result2)

if __name__ == "__main__":
    asyncio.run(main())
