from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import shutil
import json
import os

# ✅ Load .env file
load_dotenv()

# ✅ Read values from .env
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

app = FastAPI()

# ✅ CORS setup using env
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Folder setup
BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "videos"
FLOWS_DIR = BASE_DIR / "flows"

VIDEO_DIR.mkdir(exist_ok=True)
FLOWS_DIR.mkdir(exist_ok=True)

# ✅ Serve static videos
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")

# 📥 Upload video
@app.post("/upload_video/")
async def upload_video(
    flow_id: str = Form(...),
    node_id: str = Form(...),
    file: UploadFile = File(...)
):
    filename = f"{flow_id}_{node_id}.webm"
    file_path = VIDEO_DIR / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    video_url = f"{BACKEND_URL}/videos/{filename}"
    return {"message": "Upload successful", "videoUrl": video_url}

# 💾 Save flow JSON
@app.post("/save_flow/{flow_id}")
async def save_flow(flow_id: str, file: UploadFile = File(...)):
    file_path = FLOWS_DIR / f"{flow_id}.json"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Flow saved", "flow_id": flow_id}

# 📤 Load flow JSON
@app.get("/load_flow/{flow_id}")
async def load_flow(flow_id: str):
    file_path = FLOWS_DIR / f"{flow_id}.json"
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "Flow not found"})

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# 📃 List flows
@app.get("/list_flows")
async def list_flows():
    files = list(FLOWS_DIR.glob("*.json"))
    return [f.stem for f in files]
