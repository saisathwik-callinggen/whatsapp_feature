from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, Dict, Any
from whatsapp import service

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

@router.post("/instance")
async def create_instance(payload: Dict[str, Any] = Body(...)):
    instance_name = payload.get("instance_name", "callinggen_default")
    try:
        res = await service.create_instance(instance_name)
        return {"success": True, "data": res}
    except Exception as e:
        # If instance already exists, return success
        return {"success": True, "message": str(e)}

@router.get("/qr")
async def get_qr_code(instance_name: str = Query("callinggen_default")):
    try:
        res = await service.get_qr_code(instance_name)
        # Evolution API returns { code: ..., base64: ... } or pairingCode
        base64_str = res.get("base64") or res.get("code") or ""
        return {"success": True, "data": {"base64": base64_str, "raw": res}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def get_status(instance_name: str = Query("callinggen_default")):
    try:
        res = await service.get_connection_status(instance_name)
        state = res.get("instance", {}).get("state", "disconnected")
        return {"success": True, "data": {"status": state, "raw": res}}
    except Exception as e:
        return {"success": False, "data": {"status": "disconnected"}, "error": str(e)}

@router.get("/info")
async def get_info(instance_name: str = Query("callinggen_default")):
    try:
        res = await service.get_connection_info(instance_name)
        return res
    except Exception as e:
        return {"success": False, "data": {"status": "disconnected"}, "error": str(e)}

@router.delete("/logout")
async def logout_instance(instance_name: str = Query("callinggen_default")):
    try:
        res = await service.disconnect_instance(instance_name)
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chats")
async def get_chats(instance_name: str = Query("callinggen_default")):
    try:
        res = await service.get_chats(instance_name)
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@router.get("/messages")
async def get_messages(
    instance_name: str = Query("callinggen_default"),
    remote_jid: str = Query(...)
):
    try:
        res = await service.get_messages(instance_name, remote_jid)
        return {"success": True, "data": res}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}
