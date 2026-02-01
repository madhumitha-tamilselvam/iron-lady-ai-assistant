import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from flask import Flask, render_template, request, jsonify, session
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

app = Flask(__name__)
app.secret_key = "ironlady_ai_secret"

# Load data
with open("knowledge_base.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
faq_qs = [f["question"] for f in knowledge["faqs"]]
faq_emb = model.encode(faq_qs)

def get_faq_answer(query):
    q_emb = model.encode([query])
    sim = cosine_similarity(q_emb, faq_emb)
    idx = np.argmax(sim)
    if sim[0][idx] < 0.45:
        return None
    return knowledge["faqs"][idx]["answer"]

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    
    msg = request.json.get("message", "").strip()
         # Initial greeting
    if msg == "__start__":
      session.clear()
      session["step"] = "ask_name"
      return jsonify({
        "reply": "🌸 Welcome to Iron Lady!\nI’m Ila, your AI assistant.\nMay I know your name?"
    })


    # STEP 1: ASK NAME
    if "step" not in session:
        session["step"] = "ask_name"
        return jsonify({"reply": "Hi 👋 I’m Ila, Iron Lady’s AI Assistant.\nMay I know your name?"})

    # STEP 2: SAVE NAME → ASK MOBILE
    if session["step"] == "ask_name":
        session["name"] = msg
        session["step"] = "ask_mobile"
        return jsonify({"reply": f"Nice to meet you, {msg} 😊\nPlease share your mobile number so we can assist you better."})

    # STEP 3: SAVE MOBILE → SHOW OPTIONS
    if session["step"] == "ask_mobile":
        if not re.match(r"^\+?\d{10,13}$", msg):
            return jsonify({"reply": "Please enter a valid mobile number (10–13 digits)."})
        session["mobile"] = msg
        session["step"] = "menu"
        return jsonify({
            "reply": "Thank you 😊 How can I help you today?",
            "showMenu": True
        })

    # MENU OPTIONS
    lower = msg.lower()

    if "coaching" in lower:
        c = knowledge["coaching"]
        reply = f"{c['title']}\n\n{c['description']}\n\nIncludes:\n"
        reply += "\n".join([f"- {i}" for i in c["includes"]])
        reply += "\n\nYou can ask about:\n• Pricing\n• Duration\n• Who this is for"
        return jsonify({"reply": reply})

    if "program" in lower or "course" in lower:
        reply = "Programs offered by Iron Lady:\n\n"
        for p in knowledge["programs"]:
            reply += f"{p['name']}\nFor: {p['for']}\n{p['details']}\n\n"
        reply += "Ask me which program suits you best."
        return jsonify({"reply": reply})

    if "faq" in lower:
        faq_list = "Frequently Asked Questions:\n\n"
        for f in knowledge["faqs"]:
            faq_list += f"- {f['question']}\n"
        faq_list += "\nYou can click or type any question."
        return jsonify({"reply": faq_list})

    if "contact" in lower or "team" in lower:
        return jsonify({
            "reply": "You can connect with the Iron Lady team through the official website:\nhttps://www.iamironlady.com\n\nOur team will be happy to assist you 🌸"
        })

    # FREE QUESTION (AI FAQ MATCH)
    answer = get_faq_answer(msg)
    if answer:
        return jsonify({"reply": answer})

    # FALLBACK
    return jsonify({
        "reply": "I’m here to help 😊 You can ask about Coaching, Programs, FAQs, or Contact.\nIf you need personal support, our team will be happy to guide you."
    })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
