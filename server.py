from flask import Flask, Response, request, jsonify, send_from_directory, make_response, render_template
from flask_cors import CORS, cross_origin
import requests
import os
from dotenv import load_dotenv
from QuickAgent import LanguageModelProcessor  # Import your LLM class

load_dotenv()
app = Flask(__name__)
CORS(app)

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
MODEL_NAME = "aura-2-thalia-en"
llm = LanguageModelProcessor()


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_text = data.get("text", "")
    llm_response = llm.process(user_text)
    return jsonify({"response": llm_response})


@app.route("/tts")
@cross_origin(origins="*")
def tts():
    text = request.args.get("text", "")
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    dg_url = f"https://api.deepgram.com/v1/speak?model={MODEL_NAME}"

    def generate():
        with requests.post(dg_url, stream=True, headers=headers, json=payload) as r:
            if r.status_code != 200:
                print("Deepgram error:", r.status_code, r.text)
                yield b''
                return
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk

    return Response(generate(), mimetype="audio/mpeg")


@app.route("/clear", methods=["POST"])
def clear():
    global llm
    llm = LanguageModelProcessor()  # re-initialize your LLM instance
    return jsonify({"status": "cleared"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
