import httpx
from typing import Dict, Any, Optional
from .config import EVOLUTION_API_URL, EVOLUTION_API_KEY

def get_headers() -> Dict[str, str]:
    if not EVOLUTION_API_KEY:
        raise ValueError("EVOLUTION_API_KEY is not set")
    return {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

async def create_instance(instance_name: str) -> Dict[str, Any]:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/instance/create"
    payload = {
        "instanceName": instance_name,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=get_headers())
        # If it already exists, Evolution API might return 400 or a specific error.
        # We pass the raw response up to the router to handle.
        response.raise_for_status()
        return response.json()

async def get_qr_code(instance_name: str) -> Dict[str, Any]:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/instance/connect/{instance_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()

async def get_connection_status(instance_name: str) -> Dict[str, Any]:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/instance/connectionState/{instance_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()

async def get_connection_info(instance_name: str) -> Dict[str, Any]:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/instance/fetchInstances"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=get_headers())
        response.raise_for_status()
        instances = response.json()
        for inst in instances:
            if inst.get("name") == instance_name:
                owner = inst.get("ownerJid", "").split("@")[0] if inst.get("ownerJid") else ""
                status = inst.get("connectionStatus", "disconnected")
                return {
                    "success": True,
                    "data": {
                        "status": "open" if status == "open" else status,
                        "connected_phone": owner,
                        "profile_name": inst.get("profileName", ""),
                        "last_connected": inst.get("updatedAt", "")
                    }
                }
        return {"success": True, "data": {"status": "disconnected"}}

async def disconnect_instance(instance_name: str) -> Dict[str, Any]:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/instance/logout/{instance_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=get_headers())
        response.raise_for_status()
        return response.json()

async def get_chats(instance_name: str) -> list:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/chat/findChats/{instance_name}"
    
    async with httpx.AsyncClient() as client:
        # Some versions use GET, some use POST for findChats. Testing showed POST with empty JSON works, but usually it's POST if we pass filters. 
        # Actually in test script I used POST with empty json and it worked.
        response = await client.post(url, headers=get_headers(), json={})
        response.raise_for_status()
        return response.json()

async def get_messages(instance_name: str, remote_jid: str) -> dict:
    if not EVOLUTION_API_URL:
        raise ValueError("EVOLUTION_API_URL is not set")
        
    url = f"{EVOLUTION_API_URL}/chat/findMessages/{instance_name}"
    
    async with httpx.AsyncClient() as client:
        # We request a higher limit since Evolution API sometimes ignores the where clause
        # and returns a mixed feed, which we filter on the frontend.
        payload = {"limit": 500, "where": {"remoteJid": remote_jid}}
        response = await client.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()

# =====================================================================
# OUTBOUND MESSAGING (PHASE 1)
# =====================================================================
# IMPORTANT NOTE: The exact Evolution API endpoint structures for 
# outbound messages (e.g. /message/sendText) and their JSON payload 
# structures could not be verified from the repository.
# Do not assume these endpoints are correct. They are implemented here
# based on standard Evolution v1/v2 conventions as placeholders.
# If they fail, this service layer must be updated with the correct
# Evolution API documentation for the active instance.
# =====================================================================

from .config import (
    EVOLUTION_INSTANCE_NAME, WA_BROCHURE_URL, WA_PRICING_URL,
    WA_CATALOGUE_URL, WA_WEBSITE_URL, WA_BOOKING_URL, WA_CONTACT_DETAILS
)
import os
import mimetypes
from urllib.parse import urlparse

def _clean_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"91{digits}"
    return digits

async def _send_text(phone: str, text: str) -> str:
    """Helper to send a text message via Evolution API."""
    if not EVOLUTION_API_URL or not EVOLUTION_INSTANCE_NAME:
        return "FAILURE: WhatsApp API URL or Instance Name not configured."
        
    clean_num = _clean_phone(phone)
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
    payload = {
        "number": clean_num,
        "text": text,
        "delay": 1200,
        "linkPreview": False,
        "mentionsEveryOne": False
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=get_headers())
            response.raise_for_status()
            return f"SUCCESS: Message sent to {phone}"
    except Exception as e:
        print(f"[whatsapp.service] Error sending text to {phone}: {e}")
        return f"FAILURE: Could not send message to {phone}. {str(e)}"

async def _send_media(phone: str, media_url: str, caption: str = "", media_type: str = "document") -> str:
    """Helper to send a media message via Evolution API."""
    if not EVOLUTION_API_URL or not EVOLUTION_INSTANCE_NAME:
        return "FAILURE: WhatsApp API URL or Instance Name not configured."
        
    url = f"{EVOLUTION_API_URL}/message/sendMedia/{EVOLUTION_INSTANCE_NAME}"
    
    parsed_url = urlparse(media_url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        filename = "document.pdf" if media_type == "document" else "media"
        
    mime_type, _ = mimetypes.guess_type(media_url)
    if not mime_type:
        mime_type = "application/pdf" if media_type == "document" else "application/octet-stream"
        
    clean_num = _clean_phone(phone)
    payload = {
        "number": clean_num,
        "mediatype": media_type,
        "mimetype": mime_type,
        "caption": caption,
        "media": media_url,
        "fileName": filename
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=get_headers())
            response.raise_for_status()
            return f"SUCCESS: Media sent to {phone}"
    except Exception as e:
        print(f"[whatsapp.service] Error sending media to {phone}: {e}")
        return f"FAILURE: Could not send media to {phone}. {str(e)}"

async def send_brochure(phone: str) -> str:
    if not WA_BROCHURE_URL:
        return "FAILURE: Brochure URL not configured."
    return await _send_media(phone, WA_BROCHURE_URL, caption="Here is our brochure as requested.")

async def send_pricing(phone: str) -> str:
    if not WA_PRICING_URL:
        return "FAILURE: Pricing URL not configured."
    return await _send_media(phone, WA_PRICING_URL, caption="Here is our pricing information.")

async def send_catalogue(phone: str) -> str:
    if not WA_CATALOGUE_URL:
        return "FAILURE: Catalogue URL not configured."
    return await _send_media(phone, WA_CATALOGUE_URL, caption="Here is our product catalogue.")

async def send_website(phone: str) -> str:
    if not WA_WEBSITE_URL:
        return "FAILURE: Website URL not configured."
    text = f"You can visit our website here: {WA_WEBSITE_URL}"
    return await _send_text(phone, text)

async def send_booking_link(phone: str) -> str:
    if not WA_BOOKING_URL:
        return "FAILURE: Booking URL not configured."
    text = f"You can book an appointment using this link: {WA_BOOKING_URL}"
    return await _send_text(phone, text)

async def send_contact_details(phone: str) -> str:
    if not WA_CONTACT_DETAILS:
        return "FAILURE: Contact details not configured."
    text = f"Here are our contact details:\n{WA_CONTACT_DETAILS}"
    return await _send_text(phone, text)

async def send_callback_message(phone: str, customer_name: str, company_name: str) -> str:
    name = customer_name if customer_name else "there"
    text = f"Hi {name},\n\nIt looks like you were busy. Let us know a convenient time and we'll call you back."
    return await _send_text(phone, text)

async def send_missed_call_followup(phone: str, customer_name: str, company_name: str) -> str:
    name = customer_name if customer_name else "there"
    company = company_name if company_name else "us"
    text = f"Hi {name},\n\nWe tried reaching you regarding {company}.\n\nPlease reply whenever you're available or let us know a convenient time to call."
    return await _send_text(phone, text)
