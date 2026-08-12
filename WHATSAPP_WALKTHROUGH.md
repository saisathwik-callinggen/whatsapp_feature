# WhatsApp Integration & Setup Walkthrough

This document provides complete step-by-step instructions to get the **WhatsApp Integration & AI Voice Calling** system running end-to-end after pulling this codebase.

---

## 1. Environment Configuration & API Keys

Before starting the services, ensure your `.env` files are configured properly across all three locations:
- Root directory: `.env`
- Backend directory: `BACKEND/.env`
- Backend app directory: `BACKEND/app/.env`

> **IMPORTANT**:
> - **DEEPSEEK_API_KEY**: Ensure `DEEPSEEK_API_KEY` is uncommented and set with a valid key.
> - **GROQ_API_KEY**: Comment out `GROQ_API_KEY` (or set it as fallback) so DeepSeek API is used as the primary LLM provider in every `.env` file.

### Example `.env` Configuration:

```env
# LiveKit Server Settings
LIVEKIT_URL=ws://13.232.26.174:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret123456789012345678901234567890

# SIP Trunk ID (Vobiz registered trunk)
SIP_TRUNK_ID=ST_3yaCewggPpAs

# Primary LLM API Key (DeepSeek)
DEEPSEEK_API_KEY=sk-your_valid_deepseek_api_key_here

# Alternative LLM API Key (Commented out)
# GROQ_API_KEY=gsk_your_groq_api_key_here

# Speech-to-Text & Text-to-Speech (Sarvam AI)
SARVAM_API_KEY=sk_your_sarvam_api_key_here

# Evolution WhatsApp API Settings
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=MySuperSecretKey123!
EVOLUTION_INSTANCE_NAME=callinggen_default

# Backend URL
BACKEND_URL=http://localhost:8000
```

---

## 2. Step-by-Step Service Startup Guide

Follow this sequence to launch all backend components in order:

### **Step 1: Ensure WhatsApp Evolution API is Running**
Evolution API runs via Docker on port `8080`. Verify it is accessible:
```bash
curl http://localhost:8080
```

---

### **Step 2: Connect / Verify WhatsApp Instance**
To connect your WhatsApp phone number (or check status), navigate to the `BACKEND` directory:

```powershell
cd BACKEND
```

Run the connection check script:
```powershell
python connect_whatsapp.py
```
- If connected: Output will show `State: open` and display your connected phone number.
- If disconnected: A QR code `whatsapp_qr.png` will be generated in `BACKEND/`. Scan it using WhatsApp on your mobile device (**Settings > Linked Devices > Link a Device**).

---

### **Step 3: Start the FastAPI Backend Server**
In a new terminal window inside `BACKEND/`:
```powershell
cd BACKEND
uvicorn app.main:app --reload
```
- Serves API routes at `http://localhost:8000`.
- Exposes WhatsApp dashboard endpoints at `/api/whatsapp/info`, `/api/whatsapp/chats`, `/api/whatsapp/status`, etc.

---

### **Step 4: Start the Background Queue Worker**
In another terminal window inside `BACKEND/`:
```powershell
cd BACKEND
python -m app.worker
```
- Processes campaign batch jobs from `callinggen.db`.
- Triggers outbound SIP calls via LiveKit.

---

### **Step 5: Start the LiveKit Voice Agent**
In another terminal window inside `BACKEND/`:
```powershell
cd BACKEND
python agent.py start
```
- Registers `callinggen-agent-dev` worker with LiveKit.
- Listens for answered calls, transcribes voice via Sarvam STT, generates AI responses via DeepSeek LLM, and speaks via Sarvam TTS (`shreya`).

---

### **Step 6: Start the Frontend Application**
In a new terminal window inside `livekit-frontend-main1/`:
```powershell
cd livekit-frontend-main1
npm run dev
```
- Open `http://localhost:3000` in your browser.
- Navigate to **WhatsApp Settings** (`/settings/whatsapp`) to view live connection status, profile details, and full WhatsApp chat logs.

---

## 3. How WhatsApp Integration Works Under the Hood

1. **Automatic Phone Number Formatting (`_clean_phone`)**:
   - Any 10-digit Indian phone number (e.g. `7656807447`) is automatically formatted to international standard `917656807447` before calling Evolution API.

2. **In-Conversation AI Triggers**:
   - When a user asks the AI agent for a brochure, pricing, catalogue, website link, or contact info during a live phone call:
   - The agent invokes the `send_whatsapp_material` tool.
   - Evolution API dispatches the PDF document / text message to the caller's WhatsApp instantly.

3. **Post-Call Follow-ups**:
   - If a call is declined or busy, `call_service.py` automatically triggers a WhatsApp missed call follow-up message.

---

## 4. Troubleshooting Checklist

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **WhatsApp Status "Disconnected" on Frontend** | FastAPI server not running or `/api/whatsapp` endpoint blocked | Ensure `uvicorn app.main:app --reload` is running on port `8000`. |
| **Agent is Silent on Call** | Invalid `DEEPSEEK_API_KEY` | Verify `DEEPSEEK_API_KEY` in `.env` is valid and active. |
| **SIP Call 404 Error** | Wrong trunk ID in `.env` | Ensure `SIP_TRUNK_ID=ST_3yaCewggPpAs` in all `.env` files. |
| **WhatsApp 400 Bad Request** | Missing country code in phone number | Fixed automatically via `_clean_phone()`. |
