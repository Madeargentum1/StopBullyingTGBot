from fastapi import FastAPI
from fastapi.responses import FileResponse
import threading
import uvicorn
import os

CSV_PATH = "moderation_results.csv"

web_app = FastAPI()


@web_app.get("/")
def root():
    return {"status": "ok", "message": "Use /download to get the moderation CSV file."}


@web_app.get("/download")
def download_csv():
    if os.path.exists(CSV_PATH):
        return FileResponse(CSV_PATH, filename="moderation_results.csv", media_type="text/csv")
    return {"error": "File not found"}


def run_web_server():
    uvicorn.run(web_app, host="0.0.0.0", port=8081)
