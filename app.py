from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import uuid
import os

app = Flask(__name__)

OUTPUT_DIR = "audio_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Edge TTS server is running"})


@app.route("/tts", methods=["POST"])
def tts():
    """
    Body (JSON):
    {
        "text": "النص المطلوب تحويله لصوت",
        "voice": "ar-EG-SalmaNeural"   (اختياري، الافتراضي صوت مصري أنثى)
    }
    """
    data = request.get_json(force=True)
    text = data.get("text")
    voice = data.get("voice", "ar-EG-SalmaNeural")

    if not text:
        return jsonify({"error": "text field is required"}), 400

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)

    async def generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)

    try:
        asyncio.run(generate())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return send_file(filepath, mimetype="audio/mpeg", as_attachment=True, download_name=filename)


@app.route("/voices", methods=["GET"])
def list_voices():
    """يرجع قائمة بالأصوات العربية المتاحة"""
    async def get_voices():
        voices = await edge_tts.list_voices()
        return [v for v in voices if v["Locale"].startswith("ar")]

    arabic_voices = asyncio.run(get_voices())
    return jsonify(arabic_voices)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
