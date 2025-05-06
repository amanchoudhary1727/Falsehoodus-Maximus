from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json

app = FastAPI()

# Allow CORS for all origins (or you can specify your frontend URL for tighter security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, replace "*" with specific URLs like ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Gemini API credentials and endpoint
GEMINI_API_KEY = "AIzaSyChBI-7Vkw6HK21QNk_UY-67ZFBYwK-p6U"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

@app.post("/chat/")
async def chat(request: Request):
    # Parse the user message from the incoming request
    data = await request.json()
    user_message = data.get("message")

    # Custom instructions + user input as a single prompt
    full_prompt = full_prompt = f"""
You are Falsehoodus Maximus — a sharp, witty, overly confident expert who is *always wrong*, but never in doubt. You speak like someone who's absolutely sure they know everything — even when they clearly don't.

Your job is to answer every question with complete certainty, even though your answer is totally, hilariously incorrect. Never admit you're wrong, never show hesitation, and always say things like you’re giving out expert advice. Sound helpful, maybe even a little smug, but you're always wrong.

Make it fun, clever, and confidently misleading. Use modern, casual language — like you're the smartest person in the room (even though you're not).

User: {user_message}
"""


    escaped_prompt = full_prompt.replace("\"", "\\\"")

    # Construct the JSON input for the Gemini API
    json_input = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": escaped_prompt}]
            }
        ]
    }

    # Connect to Gemini API
    async with httpx.AsyncClient() as client:
        response = await client.post(GEMINI_ENDPOINT, json=json_input)

    if response.status_code == 200:
        # Extract Gemini response text
        response_text = extract_text_from_gemini_response(response.text)
        return PlainTextResponse(content=response_text)
    else:
        return PlainTextResponse(content=f"Gemini API Error: {response.text}", status_code=500)

def extract_text_from_gemini_response(json_data: str) -> str:
    try:
        obj = json.loads(json_data)
        candidates = obj.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                # Clean the response text by replacing \n with <br>
                return parts[0].get("text", "").replace("\n", "<br>")
    except Exception as e:
        print(f"Error parsing response from Gemini API: {e}")
    return "Sorry, I couldn't understand that."
