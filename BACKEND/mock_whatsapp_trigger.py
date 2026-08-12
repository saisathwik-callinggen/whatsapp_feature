import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.call_service import CallService
from app.models.call import Call
from app.models.contact import Contact
from app.models.job import Job

async def mock_failed_call():
    print("Testing WhatsApp Trigger (Simulating a failed SIP Call)...")
    
    async with AsyncSessionLocal() as db:
        # Create a dummy contact for testing
        contact = Contact(
            campaign_id=1,  # Assuming a campaign exists
            name="Test User",
            phone="+919876543210", # Make sure this is a real number you can check WhatsApp on
            status="calling",
            customer_name="Test User",
            company_name="CallingGen"
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)

        # Create a dummy job
        job = Job(
            campaign_id=1,
            total_contacts=1,
            status="running"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Create a dummy call
        call = Call(
            job_id=job.id,
            contact_id=contact.id,
            phone=contact.phone,
            status="dialing",
            room_name="test-room-fail"
        )
        db.add(call)
        await db.commit()
        await db.refresh(call)

        print(f"Created dummy Contact ID: {contact.id}, Call ID: {call.id}")
        print("Simulating SIP trunk failure (Call No Answer / Declined)...")

        # This is exactly what queue_service.py does when make_livekit_call fails!
        await CallService.fail_call(db=db, call_id=call.id)
        
        print("Done! If your Evolution API is running, you should receive a WhatsApp message shortly on +919876543210.")

if __name__ == "__main__":
    asyncio.run(mock_failed_call())
