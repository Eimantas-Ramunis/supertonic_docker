import io
import os
import tempfile
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

# NOTE: Replace these imports/calls with the exact Supertonic Python API you installed.
# The official install instructions are on their docs.  [oai_citation:1‡supertonictts.com](https://supertonictts.com/installation?utm_source=chatgpt.com)
from supertonictts import TTS  # <-- adjust to real API

MODEL_DIR = os.getenv("MODEL_DIR", "/models")

app = FastAPI()

class TTSReq(BaseModel):
    text: str
    voice: str | None = None
    speed: float | None = 1.0
    format: str | None = "wav"  # "wav" or "ogg" (ogg uses ffmpeg below)

# Load model once at startup
tts = TTS(model_dir=MODEL_DIR)  # <-- adjust to real init

@app.post("/tts")
def tts_endpoint(req: TTSReq):
    # 1) synthesize WAV to a temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    tts.synthesize_to_file(
        text=req.text,
        out_path=wav_path,
        voice=req.voice,
        speed=req.speed,
    )  # <-- adjust to real call

    # 2) optionally convert to OGG/OPUS for smaller Discord-friendly files
    if (req.format or "wav").lower() == "ogg":
        ogg_path = wav_path.replace(".wav", ".ogg")
        # opus is ideal for Discord size; ffmpeg does the conversion
        os.system(f'ffmpeg -y -i "{wav_path}" -c:a libopus -b:a 48k "{ogg_path}"')
        return FileResponse(ogg_path, media_type="audio/ogg", filename="tts.ogg")

    return FileResponse(wav_path, media_type="audio/wav", filename="tts.wav")