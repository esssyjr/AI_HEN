from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import io
import base64
import logging
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from starlette.datastructures import UploadFile as StarletteUploadFile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Hen Feces Chatbot API")

# Allowed CORS origins
allowed_origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.onrender.com",
]

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory conversation history
conversation_history = []

# Pydantic model for chat request
class ChatRequest(BaseModel):
    message: str = ""
    lang: str = "english"

# Main chatbot logic
def chat_with_vet(message: str, image: Image.Image | None, lang: str):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            error_msg = "No valid API key provided." if lang == "english" else "Ba a bayar da maɓallin API mai inganci ba."
            logger.error(error_msg)
            return {"error": error_msg}

        # Base system prompt
        messages = [{
            "role": "system",
            "content": (
                f"You are an intelligent veterinary chatbot specializing in poultry health. You will receive images of hen feces or hen physical conditions (if provided) and user inputs in {lang} ('english' or 'hausa'). "
                f"Analyze any provided images and text inputs to identify potential poultry diseases and recommend appropriate treatments, including organic options. "
                f"Provide brief, clear, and conversational responses in {lang}, matching the user's language (English or Hausa). "
                f"If critical information is missing for an accurate diagnosis, ask one concise, relevant follow-up question at a time in {lang}, even if the user inputs in Hausa. Do not list multiple questions; ask only one and wait for the user's response before asking another, up to a maximum of three questions. "
                f"Once sufficient information is gathered, provide a concise diagnosis in {lang}, listing the likely disease(s) and specific conventional and organic treatment options. "
                f"For all treatments, suggest checking availability on our in-app marketplaces and ensure recommendations are simple, beginner-friendly, and precise. "
                f"If treatments are ineffective or the condition worsens, advise consulting a professional veterinary doctor. "
                f"Note that your diagnoses and recommendations are based on high probability for a prototype system and are not definitive professional diagnoses. Response any language you are spoken with either english, hausa, yoruba or igbo. Make follow up question mandatory, especially when inages are uploaded. . "
            )
        }]
        
        # Add past conversation
        for msg in conversation_history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["parts"][0]})

        # Add user message
        if message:
            messages.append({"role": "user", "content": message})
            conversation_history.append({"role": "user", "parts": [message]})

        # Process image if provided
        if image:
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image of hen feces:"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
                    },
                ],
            })
            conversation_history.append({"role": "user", "parts": ["Image provided for analysis"]})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        response_text = response.choices[0].message.content.strip()

        # Save assistant response
        conversation_history.append({"role": "assistant", "parts": [response_text]})

        # Limit history
        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]

        return {"response": response_text}

    except Exception as e:
        logger.error(f"Exception in chat_with_vet: {str(e)}")
        return {"error": f"Error: {str(e)}" if lang == "english" else f"Kuskure: {str(e)}"}

# Clear chat history
def clear_conversation(lang: str):
    conversation_history.clear()
    return {
        "response": "Conversation history cleared. Ready for a new case." if lang == "english"
        else "An share tarihin tattaunawa. A shirye don sabon shari'a."
    }

# Endpoint: Chat
@app.post("/chat")
async def chat_endpoint(
    message: str = Form(default=""),
    lang: str = Form(default="english"),
    image: UploadFile | None = File(default=None),
):
    try:
        if lang.lower() not in ["english", "hausa"]:
            error_msg = "Invalid language. Use 'english' or 'hausa'." if lang.lower() == "english" else "Harshen da ba daidai ba. Yi amfani da 'english' ko 'hausa'."
            raise HTTPException(status_code=400, detail=error_msg)

        image_obj = None

        # ✅ Handle image if a valid file is uploaded
        if isinstance(image, StarletteUploadFile) and image.filename:
            image_data = await image.read()
            try:
                image_obj = Image.open(io.BytesIO(image_data))
                if image_obj.format not in ["JPEG", "PNG"]:
                    error_msg = "Only JPEG or PNG images are supported." if lang.lower() == "english" else "Hotunan JPEG ko PNG kawai ake tallafawa."
                    raise HTTPException(status_code=400, detail=error_msg)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

        result = chat_with_vet(message, image_obj, lang.lower())
        return result

    except Exception as e:
        logger.error(f"Exception in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# Endpoint: Clear conversation
@app.post("/clear")
async def clear_endpoint(lang: str = Form(default="english")):
    if lang.lower() not in ["english", "hausa"]:
        error_msg = "Invalid language. Use 'english' or 'hausa'." if lang.lower() == "english" else "Harshen da ba daidai ba. Yi amfani da 'english' ko 'hausa'."
        raise HTTPException(status_code=400, detail=error_msg)
    return clear_conversation(lang.lower())

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Hen Feces Chatbot API! Use POST /chat with an optional image, 'message', and 'lang' ('english' or 'hausa'). Use POST /clear to reset conversation history.",
        "hausa_message": "Barka da zuwa API na Chatbot na Kaza! Yi amfani da POST /chat tare da hoto na zaɓi, 'message', da 'lang' ('english' ko 'hausa'). Yi amfani da POST /clear don sake saita tarihin tattaunawa."
    }

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)