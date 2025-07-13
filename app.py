from flask import Flask, request, render_template, jsonify
import torch
import uuid
import os
import time
import scipy.io.wavfile
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, WhisperTokenizer, pipeline

app = Flask(__name__)

# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "openai/whisper-large-v3-turbo"
torch_dtype = torch.float16

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    MODEL_NAME, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
).to(device)

processor = AutoProcessor.from_pretrained(MODEL_NAME)
tokenizer = WhisperTokenizer.from_pretrained(MODEL_NAME, language="en")

pipe = pipeline(
    task="automatic-speech-recognition",
    model=model,
    tokenizer=tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=25,
    torch_dtype=torch_dtype,
    device=device,
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    filename = f"temp_{uuid.uuid4().hex}.wav"
    filepath = os.path.join("temp", filename)
    os.makedirs("temp", exist_ok=True)
    audio_file.save(filepath)

    try:
        start_time = time.time()
        result = pipe(filepath)["text"]
        latency = time.time() - start_time
        os.remove(filepath)
        return jsonify({
            "transcription": result,
            "latency": round(latency, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
