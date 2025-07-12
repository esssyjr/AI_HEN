# 🐔 Hen Feces Chatbot API 🧠  
### AI-powered Poultry Health Diagnosis Assistant  
**Built for the HACK4LIVESTOCK Hackathon 2025**  

---

## 📌 Overview

Rural poultry farmers in low-resource communities often struggle to detect poultry illnesses early due to lack of veterinary access, limited digital tools, and language barriers. Traditional veterinary services are often unavailable, delayed, or unaffordable.

To address this, we developed the **Hen Feces Chatbot API** — a lightweight, AI-powered veterinary assistant that:
- Analyzes images of chicken feces or physical symptoms,
- Understands questions in **English or Hausa**,
- Gives intelligent, accessible health guidance on poultry diseases, 
- Suggests **organic and conventional treatment options**,
- And prompts **follow-up diagnostic questions** when image or text is insufficient.

This chatbot is tailored for mobile and rural use cases — enabling farmers to **detect diseases early**, improve **treatment outcomes**, and **reduce flock mortality**.

---

## 🌟 Features

- 🧠 GPT-4o-powered Veterinary Assistant (via OpenAI)
- 🗣️ Language Support: English & Hausa
- 📷 Accepts images of chicken droppings (feces)
- 📄 Provides diagnoses and treatment suggestions
- 🌱 Supports both **organic and conventional medicine**
- 🔄 Keeps short, relevant conversation history for accurate context
- 🌍 Can integrate with mobile apps and low-bandwidth clients
- 🛡️ Recommends professional vet help if case is complex or unclear

---

## 🔌 API Endpoints

### 🚀 `POST /chat`

Send a message (and optional image) to the veterinary assistant.

**Form Fields:**
| Field     | Type       | Description                                         |
|-----------|------------|-----------------------------------------------------|
| `message` | `string`   | Text query (symptom or question)                   |
| `lang`    | `string`   | Language: `"english"` or `"hausa"`                 |
| `image`   | `file`     | Optional image of chicken feces or physical signs  |

**Example (Text Only):**
```bash
curl -X POST http://localhost:8000/chat \
  -F "message=My chicken has diarrhea" \
  -F "lang=english"
```
---

### 📦 Example (With Image)

```bash
curl -X POST http://localhost:8000/chat \
  -F "message=Gashi nan" \
  -F "lang=hausa" \
  -F "image=@hen_feces.jpg"
```
---

## 🔄 POST `/clear`

Clears the chatbot's memory for a fresh conversation.

### Form Fields:

| Field | Type   | Description                      |
|-------|--------|----------------------------------|
| lang  | string | `"english"` or `"hausa"`         |

---

## 📡 GET `/`

Returns welcome information and usage guide in both **English** and **Hausa**.

---

## 🛠️ How It Works

- 🖼️ **Image Upload (Optional):** Converts image to base64 → sends to OpenAI API.
- 🧠 **Message Context:** Maintains recent interactions for smart follow-up.
- 🌐 **Multi-Language Reasoning:** Responds in Hausa or English depending on user input.
- ❓ **Follow-up Prompts:** If input is incomplete, bot asks one concise question at a time.
- 💊 **Treatment Guidance:** Suggests medication (both conventional and organic).

---

## 📂 Project Structure

```bash
📁 app/
├── main.py            # FastAPI backend logic
├── .env               # API key for OpenAI (secure)
└── README.md          # Project documentation
```
---

## 📈 Why It Matters

- 🐣 **Early Diagnosis:** Prevents the spread of diseases, saving poultry and protecting farmers' income.
- 🧑‍🌾 **Empowers Farmers:** Offers localized veterinary support in native languages such as English and Hausa.
- 🌾 **Supports Organic Farming:** Recommends non-antibiotic treatment alternatives when applicable.
- 🤖 **Scalable Tool:** Designed to be deployable in rural, low-resource environments.
- 📱 **Mobile Friendly:** Suitable for mobile apps or offline-first platforms with limited internet.

---

## 🧪 Tech Stack

- **FastAPI** – Lightweight, high-performance Python web framework for APIs
- **Pillow (PIL)** – Image handling and preprocessing
- **OpenAI GPT-4o** – AI model for diagnosis, reasoning, and conversational flow
- **dotenv** – Secure handling of environment variables and API keys
- **Base64 Encoding** – Encodes uploaded images for OpenAI compatibility

---

## ⚠️ Limitations

- 🧪 **Prototype Phase:** Not a replacement for a licensed veterinary diagnosis
- 🌐 **Requires Internet Access:** Relies on OpenAI API for processing (online-only for now)
- 📸 **Image Quality Sensitive:** Results depend on clarity and detail of uploaded images

---

## 🔮 Future Improvements

- 🛰️ **Offline Version:** Deploy AI logic with quantized LLMs for areas without internet
- 📱 **Frontend Integration:** Add a user-friendly interface via Streamlit, React, or mobile app
- 🌍 **Multilingual Support:** Expand to Yoruba, Igbo, Fulfulde, and more
- 📊 **Health Dashboard:** Aggregate disease cases for trend and outbreak analysis
- 🧬 **Disease Database Linkage:** Integrate structured poultry disease records (e.g., NDV, Coccidiosis)

---

## 👨‍💻 Developers

- 🧪 **Project By:** [EJAZTECH.AI](https://ejaztech.ai)
- 👨‍🔬 **Lead Developer:** Ismail Ismail Tijjani
- 🏫 **Institution:** Bayero University, Kano
- 🏁 **Hackathon:** Built as part of the **Hack4Livestock Hackathon 2025**

---

## 📜 License

This project is licensed under the **MIT License**.  
Feel free to use, distribute, and build upon it with proper attribution.

---

## 🤝 Contributing

We welcome all kinds of collaboration and community effort!

- 📬 **Fork this repository**
- ✅ **Open a pull request**
- 💡 **Propose features, ideas, or enhancements**

**Together, we can build intelligent veterinary tools for the future of farming!** 🌿

---
