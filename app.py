# backend/app.py

import os
import time
import sqlite3
import base64
import numpy as np
import cv2

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import google.generativeai as genai
from dotenv import load_dotenv

import alert_utils
from db import init_db, insert_event, get_recent_events

# Load env variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# FastAPI app
app = FastAPI(title="Campus Safety AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB setup
DB_PATH = "events.db"
init_db(DB_PATH)

# STORE LATEST CAMERA FRAME
latest_frame = None


# ------------------------------
# 📌 Event Receiver
# ------------------------------
class EventIn(BaseModel):
    event_type: str
    confidence: float
    bbox: list
    frame_id: int = None
    source: str = "camera1"
    meta: dict = {}


@app.post("/event")
async def receive_event(ev: EventIn):
    timestamp = int(time.time())
    event_id = insert_event(DB_PATH, ev.event_type, ev.confidence, ev.bbox, timestamp, ev.source, ev.meta)

    try:
        alert_utils.send_whatsapp_alert(f"[{ev.source}] {ev.event_type} detected.")
    except:
        pass

    return {"status": "ok", "event_id": event_id}


# ------------------------------
# 📌 Store Frame From Detector
# ------------------------------
class FrameIn(BaseModel):
    image: str


@app.post("/frame")
async def receive_frame(data: FrameIn):
    global latest_frame
    img_bytes = base64.b64decode(data.image)
    jpg_np = np.frombuffer(img_bytes, dtype=np.uint8)
    latest_frame = cv2.imdecode(jpg_np, cv2.IMREAD_COLOR)
    return {"status": "ok"}


# ------------------------------
# 📌 Video Stream
# ------------------------------
def generate_stream():
    global latest_frame
    while True:
        if latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        else:
            continue


@app.get("/video")
def video_feed():
    return StreamingResponse(generate_stream(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


# ------------------------------
# 📌 Recent Events API
# ------------------------------
@app.get("/events/recent")
def recent(limit: int = 50):
    return {"events": get_recent_events(DB_PATH, limit)}


# ------------------------------
# 📌 Chatbot (Gemini)
# ------------------------------
class ChatIn(BaseModel):
    text: str


@app.post("/chat")
def chat_endpoint(msg: ChatIn):
    try:
        response = model.generate_content(msg.text)
        reply = response.text
    except Exception as e:
        reply = f"Gemini Error: {e}"

    return {"reply": reply}
