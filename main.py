from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import time

import os
from pytube import YouTube

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def delete_old_video_files():
    folder_path = os.getcwd() + '/static'
    current_time = datetime.now()
    threshold_time = current_time - timedelta(minutes=1)

    for filename in os.listdir(folder_path):
        if filename.endswith('.mp4') or filename.endswith('.avi') or filename.endswith('.mov'):
            file_path = os.path.join(folder_path, filename)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < threshold_time:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(background_tasks: BackgroundTasks, request: Request, url: str = Form(...)):

    youtubeObject = YouTube(url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    file_name = youtubeObject.default_filename
    
    try:
        youtubeObject.download(os.getcwd() + '/static')
        print("Download is completed successfully")
    except:
        print("An error has occurred")

    background_tasks.add_task(delete_old_video_files)
    response = {"request": request, "file_name": file_name}
    return templates.TemplateResponse("result.html", response)

 