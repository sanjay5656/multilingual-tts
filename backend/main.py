import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import tempfile

from tts_engine import synthesize
from utils import validate_text, validate_language, convert_wav_to_mp3

app = FastAPI(title="VaakAI - Multilingual TTS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"
outputs_path  = Path(__file__).parent.parent / "outputs"

app.mount("/ui",      StaticFiles(directory=str(frontend_path), html=True), name="frontend")
app.mount("/outputs", StaticFiles(directory=str(outputs_path)),              name="outputs")


@app.get("/")
def root():
    return {"message": "VaakAI TTS API running", "status": "ok"}


@app.post("/synthesize")
async def synthesize_speech(
    text:         str        = Form(...),
    language:     str        = Form(...),
    speed:        float      = Form(1.0),
    voice_type:   str        = Form("young_female"),
    speaker_wav:  UploadFile = File(None),
):
    text_valid, text_msg = validate_text(text)
    if not text_valid:
        raise HTTPException(status_code=400, detail=text_msg)

    lang_valid, lang_msg = validate_language(language)
    if not lang_valid:
        raise HTTPException(status_code=400, detail=lang_msg)

    # Handle uploaded voice clone file
    speaker_wav_path = None
    if speaker_wav and speaker_wav.filename:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        shutil.copyfileobj(speaker_wav.file, tmp)
        speaker_wav_path = tmp.name

    try:
        output_path = synthesize(
            text=text,
            language=language,
            voice_type=voice_type,
            speaker_wav=speaker_wav_path,
            speed=speed,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

    filename = Path(output_path).name
    return JSONResponse({
        "status":     "success",
        "audio_url":  f"/outputs/{filename}",
        "language":   language,
        "voice_type": voice_type,
    })


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = outputs_path / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path), media_type="audio/wav", filename=filename)


@app.get("/health")
def health():
    import torch
    return {
        "status": "healthy",
        "gpu": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
