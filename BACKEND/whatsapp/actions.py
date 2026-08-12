from typing import Dict, Any, Optional
from . import service

async def dispatch_whatsapp_action(phone: str, action_type: str, customer_name: str = "", company_name: str = "") -> str:
    """
    Central dispatcher to map business intents to WhatsApp service logic.
    Returns a structured string (e.g. "SUCCESS: ..." or "FAILURE: ...").
    """
    if not phone:
        return "FAILURE: No phone number provided."

    action_type = action_type.strip().lower()
    
    try:
        if action_type == "brochure":
            return await service.send_brochure(phone)
        elif action_type == "pricing":
            return await service.send_pricing(phone)
        elif action_type == "catalogue":
            return await service.send_catalogue(phone)
        elif action_type == "website":
            return await service.send_website(phone)
        elif action_type == "booking":
            return await service.send_booking_link(phone)
        elif action_type == "contact_details":
            return await service.send_contact_details(phone)
        elif action_type == "missed_call":
            return await service.send_missed_call_followup(phone, customer_name, company_name)
        elif action_type == "busy":
            return await service.send_callback_message(phone, customer_name, company_name)
        else:
            return f"FAILURE: Unknown action type '{action_type}'"
    except Exception as e:
        import traceback
        print(f"[whatsapp.actions] ERROR dispatching {action_type}: {e}\n{traceback.format_exc()}")
        return f"FAILURE: Internal error occurred while sending {action_type}."
