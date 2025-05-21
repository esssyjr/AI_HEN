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

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Hen Feces Chatbot API")

# List of allowed frontend domains
allowed_origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.onrender.com",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history per session
conversation_history = []

# Request model for chat input
class ChatRequest(BaseModel):
    message: str = ""
    lang: str = "english"

def chat_with_vet(message: str, image: Image.Image | None, lang: str):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            error_msg = "No valid API key provided." if lang == "english" else "Ba a bayar da maɓallin API mai inganci ba."
            logger.error(error_msg)
            return {"error": error_msg}

        # Build conversation history
        messages = [{"role": "system", "content": (
            f"You are an intelligent veterinary chatbot specializing in poultry. You will receive images of hen feces or hen physical body conditions (if provided), along with user inputs. "
            f"Analyze the provided images (if any) and text inputs to diagnose potential diseases and recommend appropriate medications, including organic treatment options. "
            f"Provide brief, clear responses in a natural, conversational tone in {lang} ('english' or 'hausa'). "
            f"If additional information is necessary for an accurate diagnosis, ask one concise, relevant follow-up question at a time, limiting to a maximum of three questions. Do not preemptively mention or list subsequent questions; ask only one question at a time, and wait for the user's response before asking another if needed. "
            f"Once sufficient information is gathered, provide a concise prediction that lists only the likely disease(s) and specific medication(s) in {lang}. "
            f"When recommending treatments (both conventional and organic), suggest checking our marketplaces in the application for availability. Ensure recommendations are simple and beginner-friendly, with precise medication suggestions. "
            f"If the suggested treatments prove ineffective or the condition worsens, advise the user to consult a professional veterinary doctor. "
            f"Understand that your diagnoses and recommendations are based on high probability and are for a prototype system, not a definitive professional diagnosis."
        )}]

        # Add conversation history
        for i, msg in enumerate(conversation_history):
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["parts"][0]})

        # Add current message if provided
        if message:
            messages.append({"role": "user", "content": message})
            conversation_history.append({"role": "user", "parts": [message]})

        # Add image if provided
        if image:
            if not isinstance(image, Image.Image):
                error_msg = "Please upload a valid image of hen feces." if lang == "english" else "Da fatan za a loda hoton kaza mai inganci."
                logger.error(error_msg)
                return {"error": error_msg}
            
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image of hen feces:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_str}"
                        },
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

        # Append assistant response to history
        conversation_history.append({"role": "assistant", "parts": [response_text]})
        
        # Limit conversation history to prevent excessive growth (e.g., last 10 messages)
        if len(conversation_history) > 10:
            conversation_history[:] = conversation_history[-10:]

        return {"response": response_text}

    except Exception as e:
        error_msg = f"Error: {str(e)}" if lang == "english" else f"Kuskure: {str(e)}"
        logger.error(f"Exception in chat_with_vet: {str(e)}")
        return {"error": error_msg}

def clear_conversation(lang: str):
    conversation_history.clear()
    message = "Conversation history cleared. Ready for a new case." if lang == "english" else "An share tarihin tattaunawa. A shirye don sabon shari'a."
    return {"response": message}

@app.post("/chat")
async def chat_endpoint(
    message: str = Form(default=""),
    lang: str = Form(default="english"),
    image: UploadFile | None = File(default=None),  # Explicitly allow None
):
    try:
        if lang.lower() not in ["english", "hausa"]:
            error_msg = "Invalid language. Use 'english' or 'hausa'." if lang.lower() == "english" else "Harshen da ba daidai ba. Yi amfani da 'english' ko 'hausa'."
            raise HTTPException(status_code=400, detail=error_msg)

        # Process image only if a valid file is provided
        image_obj = None
        if image and image.filename:  # Check if a file is actually uploaded
            image_data = await image.read()
            try:
                image_obj = Image.open(io.BytesIO(image_data))
            except Exception as e:
                error_msg = f"Error processing image: {str(e)}" if lang.lower() == "english" else f"Kuskure wajen sarrafa hoto: {str(e)}"
                raise HTTPException(status_code=400, detail=error_msg)

            if image_obj.format not in ["JPEG", "PNG"]:
                error_msg = "Only JPEG or PNG images are supported." if lang.lower() == "english" else "Hotunan JPEG ko PNG kawai ake tallafawa."
                raise HTTPException(status_code=400, detail=error_msg)

        result = chat_with_vet(message, image_obj, lang.lower())
        return result

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}" if lang.lower() == "english" else f"Kuskure wajen sarrafa buƙata: {str(e)}"
        logger.error(f"Exception in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/clear")
async def clear_endpoint(lang: str = Form(default="english")):
    if lang.lower() not in ["english", "hausa"]:
        error_msg = "Invalid language. Use 'english' or 'hausa'." if lang.lower() == "english" else "Harshen da ba daidai ba. Yi amfani da 'english' ko 'hausa'."
        raise HTTPException(status_code=400, detail=error_msg)
    result = clear_conversation(lang.lower())
    return result

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Hen Feces Chatbot API! Use POST /chat with an optional image, 'message', and 'lang' ('english' or 'hausa'). Use POST /clear to reset conversation history.",
        "hausa_message": "Barka da zuwa API na Chatbot na Kaza! Yi amfani da POST /chat tare da hoto na zaɓi, 'message', da 'lang' ('english' ko 'hausa'). Yi amfani da POST /clear don sake saita tarihin tattaunawa."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)