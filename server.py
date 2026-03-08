# server.py
import os
import uuid
import subprocess
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder for HLS segments
STREAM_DIR = "streams"
os.makedirs(STREAM_DIR, exist_ok=True)

@app.post("/start")
async def start_stream(data: dict):
    url = data["url"]

    # Unique ID per stream
    stream_id = str(uuid.uuid4())
    folder = f"{STREAM_DIR}/{stream_id}"
    os.makedirs(folder, exist_ok=True)
    playlist = f"{folder}/playlist.m3u8"

    # Get direct video URL from yt-dlp
    ytdlp = subprocess.run(["yt-dlp", "-g", url], capture_output=True, text=True)
    direct_url = ytdlp.stdout.strip()

    # ffmpeg HLS streaming with segment auto-delete
    command = [
        "ffmpeg",
        "-i", direct_url,
        "-codec", "copy",
        "-f", "hls",
        "-hls_time", "4",
        "-hls_list_size", "6",
        "-hls_flags", "delete_segments",
        "-hls_segment_filename", f"{folder}/seg_%03d.ts",
        playlist
    ]

    subprocess.Popen(command)

    return {"stream": f"/streams/{stream_id}/playlist.m3u8"}

# Mount streams folder
app.mount("/streams", StaticFiles(directory="streams"), name="streams")

# Serve static frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
