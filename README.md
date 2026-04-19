# Multilingual TTS System

A fully offline, open-source Text-to-Speech web application supporting
English, Hindi, Kannada, and Telugu with a clean modern UI.

## Models Used
- **Coqui XTTS v2** — English, Hindi (natural, expressive, voice cloning)
- **Facebook MMS** — Kannada, Telugu (best open-source Dravidian language support)

## Features
- Natural speech synthesis in 4 Indian languages
- Voice cloning from 3–5 second audio sample
- Speed control slider
- Download as WAV or MP3
- Fully offline after setup

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/sanjay5656/multilingual-tts.git
cd multilingual-tts
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install PyTorch with CUDA
```bash
pip install torch==2.3.0 torchaudio==2.3.0 --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the server
```bash
cd backend
python main.py
```

### 6. Open the UI
Open your browser and go to: http://localhost:8000/ui

## System Requirements
- Python 3.10+
- 8GB RAM minimum
- NVIDIA GPU recommended (4GB+ VRAM)
- 10GB free disk space (for model weights)