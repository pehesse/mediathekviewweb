from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from mediathek import Mediathek

import asyncio

app = FastAPI()

app.mediathek = Mediathek()


def get_mediathek():
    yield app.mediathek


@app.get("/")
async def root():
    return FileResponse("site/index.html")


@app.get("/api")
async def root():
    return {"message": "Hello World"}


@app.get("/api/movies")
async def get_movies(mediathek: Mediathek = Depends(get_mediathek)):
    movies = list(mediathek.get_movies())
    return {"halloe": "welt"}
