# Final Walkthrough: Running the WhatsApp + AI Calling Platform

This guide walks anyone through running the **CallingGen WhatsApp & AI Calling Platform** end-to-end after pulling the repository.

---

## 🔑 1. Environment Configuration & API Keys

After cloning/pulling the repository, create `.env` files in all three environment locations:
1. Root directory: `.env`
2. Backend directory: `BACKEND/.env`
3. Backend app directory: `BACKEND/app/.env`

> **IMPORTANT**:
> - **Use DEEPSEEK_API_KEY**: Ensure `DEEPSEEK_API_KEY` is uncommented and set with a valid DeepSeek API key in every `.env` file.
> - **DO NOT USE GROQ_API_KEY**: Leave `GROQ_API_KEY` commented out (`# GROQ_API_KEY=...`) or omitted so DeepSeek remains the primary active LLM.

### Complete `.env` Template:

```env
# ── LiveKit Server Configuration ──────────────────────────────────
LIVEKIT_URL=ws://13.232.26.174:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret123456789012345678901234567890

# ── SIP Trunk ID (Vobiz Registered Trunk) ────────────────────────
SIP_TRUNK_ID=ST_3yaCewggPpAs

# ── Primary LLM Provider (DeepSeek API Key) ───────────────────────
DEEPSEEK_API_KEY=sk-your_valid_deepseek_api_key_here

# ── Secondary LLM Provider (Commented Out) ───────────────────────
# GROQ_API_KEY=gsk_your_groq_api_key_here

# ── Sarvam AI (STT Speech-to-Text & TTS Text-to-Speech) ───────────
SARVAM_API_KEY=sk_your_sarvam_api_key_here

# ── Evolution WhatsApp API Settings ──────────────────────────────
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=MySuperSecretKey123!
EVOLUTION_INSTANCE_NAME=callinggen_default

# ── Backend Base URL ─────────────────────────────────────────────
BACKEND_URL=http://localhost:8000
```

---

## 🚀 2. Step-by-Step Execution Guide

Launch all services in the following order:

### **Step 1: Verify WhatsApp Evolution API Service**
Evolution API runs via Docker on port `8080`. Verify it is online:
```bash
curl http://localhost:8080
```

---

### **Step 2: Connect your WhatsApp Account**
Open your terminal and navigate to `BACKEND/`:
```powershell
cd BACKEND
python connect_whatsapp.py
```
- **If already connected**: Output will show `State: open` and display your connected phone number.
- **If disconnected**: It generates a QR code `whatsapp_qr.png` in `BACKEND/`. Open WhatsApp on your phone (**Settings > Linked Devices > Link a Device**) and scan the QR code.

---

### **Step 3: Start the FastAPI Backend Server**
In a new terminal window inside `BACKEND/`:
```powershell
cd BACKEND
uvicorn app.main:app --reload
```
- Listens on `http://localhost:8000`.
- Serves endpoints for campaigns, calls, and `/api/whatsapp` dashboard APIs (`/api/whatsapp/info`, `/api/whatsapp/chats`, `/api/whatsapp/messages`).

---

### **Step 4: Start the Background Queue Worker**
In a new terminal window inside `BACKEND/`:
```powershell
cd BACKEND
python -m app.worker
```
- Polls `callinggen.db` for campaign jobs.
- Dispatches outbound SIP calls through LiveKit.

---

### **Step 5: Start the LiveKit Voice Agent**
In a new terminal window inside `BACKEND/`:
```powershell
cd BACKEND
python agent.py start
```
- Registers `callinggen-agent-dev` with LiveKit.
- Listens for answered calls, transcribes voice using Sarvam STT, generates conversational AI responses using **DeepSeek LLM**, and synthesizes natural speech using Sarvam TTS (`shreya`).

---

### **Step 6: Start the Next.js Frontend Application**
In a new terminal window inside `livekit-frontend-main1/`:
```powershell
cd livekit-frontend-main1
npm run dev
```
- Access `http://localhost:3000` in your web browser.
- Open **WhatsApp Settings** (`/settings/whatsapp`) to view live connection status, profile details, and full WhatsApp chat logs.

---

## 📲 3. End-to-End Testing Flow

1. **Launch a Campaign**: Create a campaign on the dashboard targeting your test phone number.
2. **Answer the Phone Call**: As soon as you answer, the agent detects the answered audio track and greets you.
3. **Trigger WhatsApp Material**: Ask the agent on the call:
   > *"Can you please send me the brochure on WhatsApp?"*
4. **Instant WhatsApp Delivery**: The agent calls `send_whatsapp_material`, formats your phone number with country code `91`, and dispatches the document via Evolution API instantly.
5. **View Chat Logs**: Open the **WhatsApp** tab on the web dashboard to inspect the live message history.

---

## 🔧 4. Troubleshooting Guide

| Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| **Agent stays silent after call connects** | Invalid or expired `DEEPSEEK_API_KEY` | Verify `DEEPSEEK_API_KEY` in `.env` is valid and has active credit. |
| **WhatsApp status shows "Not Connected" on Frontend** | FastAPI server not running on port 8000 | Run `uvicorn app.main:app --reload` inside `BACKEND/`. |
| **`TwirpError 404: requested sip trunk does not exist`** | Invalid trunk ID | Check `.env` and verify `SIP_TRUNK_ID=ST_3yaCewggPpAs`. |
| **Evolution API `400 Bad Request`** | Unformatted phone number | Handled automatically via `_clean_phone()` (auto-adds country code `91`). |
