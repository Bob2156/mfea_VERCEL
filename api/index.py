from fastapi import FastAPI, Request, HTTPException
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
import requests

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")  # Add this in Vercel Environment Variables
DISCORD_APP_ID = os.getenv("DISCORD_APP_ID")  # Add this in Vercel Environment Variables

app = FastAPI()

# Verify Discord request signature
async def verify_signature(request: Request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()

    if not signature or not timestamp:
        raise HTTPException(status_code=401, detail="Missing signature or timestamp")

    verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
    try:
        verify_key.verify(f"{timestamp}{body.decode()}".encode(), bytes.fromhex(signature))
    except BadSignatureError:
        raise HTTPException(status_code=401, detail="Invalid request signature")

# Route to handle Discord interactions
@app.post("/")
async def handle_interaction(request: Request):
    await verify_signature(request)
    data = await request.json()

    if data["type"] == 1:  # Ping from Discord
        return {"type": 1}

    if data["type"] == 2:  # Slash commands
        command = data["data"]["name"]

        if command == "check":
            return {"type": 4, "data": {"content": "working"}}

        if command == "joke":
            joke = requests.get("https://official-joke-api.appspot.com/random_joke").json()
            return {
                "type": 4,
                "data": {"content": f"{joke['setup']} - {joke['punchline']}"}
            }

    return {"type": 1}
