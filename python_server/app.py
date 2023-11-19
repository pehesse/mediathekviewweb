from fastapi import FastAPI, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from mediathek import Mediathek
from fastapi.responses import JSONResponse

import json
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
    # yield dict(zip(metadata, json.loads(re.split(r'"X":', match.group())[1])))
    return JSONResponse(content=movies)


@app.get("/api/state")
async def get_state(mediathek: Mediathek = Depends(get_mediathek)):
    return JSONResponse(content={
        "entry_count": mediathek.entrycount,
        "state": mediathek.state.name
    })
