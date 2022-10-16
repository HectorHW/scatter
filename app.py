import datetime
import logging
from typing import Dict, List
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, status, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
import uvicorn
from fastapi.responses import RedirectResponse
from pydantic import UUID4, BaseModel
import random
import os
import asyncio

from asyncio import Lock
from asyncio.exceptions import TimeoutError, CancelledError
from freq import get_letter
from functools import reduce

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database = {}

game_state = {"question": "sample question", "letter": "a"}

sockets = {}

questions: List[str] = ["sample question"]

question_idx = 0


def reload_questions():
    global questions
    global question_idx

    def parse_entry(entry: str) -> List[str]:
        entry = entry.strip()
        if "*" not in entry:
            return [entry]
        items = entry.split("*")
        count, word = items[-1].strip(), items[:-1]
        try:
            count = int(count)
            return ["*".join(word)] * count
        except ValueError:
            return [entry]

    with open("questions.txt") as f:
        lines = f.read().strip().split("\n")
        questions = reduce(list.__add__,  map(parse_entry, lines))
        random.shuffle(questions)
        question_idx = 0
        return len(questions)


reload_questions()


def get_question():
    global question_idx
    global questions
    if question_idx >= len(questions):
        question_idx = 0
        random.shuffle(questions)
    q = questions[question_idx]
    question_idx += 1
    return q


@app.websocket("/ws")
async def ws_root(websocket: WebSocket):
    global sockets
    try:
        await websocket.accept()
        lock = asyncio.Lock()
        sock_id = uuid4()
        sockets[sock_id] = (websocket, lock)
        while True:
            await lock.acquire()
            await websocket.send_json("heartbeat")
            await asyncio.wait_for(websocket.receive_text(), timeout=2)
            #logging.info(f"heartbeat from {sock_id}")
            lock.release()
            await asyncio.sleep(4)
    except (ConnectionClosed, TimeoutError, CancelledError, WebSocketDisconnect) as _:
        del sockets[sock_id]


@app.get("/api/state")
async def state():
    return {**game_state, "cards_left": len(questions) - question_idx}


class LoginData(BaseModel):
    passphrase: str


sessions = {}


current_passphrase = os.environ["PASS"]


@app.post("/api/login")
async def log_as_admin(data: LoginData):
    if data.passphrase == current_passphrase:
        session = uuid4()
        valid_until = datetime.datetime.now() + datetime.timedelta(hours=24)
        sessions[session] = valid_until
        return {
            "session": session,
            "valid_unitl": valid_until
        }
    else:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


class SessionData(BaseModel):
    session: UUID4


@app.post("/api/logout")
def logout(data: SessionData):
    if data.session in sessions:
        del sessions[data.session]
        raise HTTPException(status_code=200)
    else:
        raise HTTPException(status_code=404)


def check_admin_auth(data: SessionData):
    if data.session not in sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    best_before = sessions[data.session]
    if datetime.datetime.now() > best_before:
        del sessions[data.session]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    sessions[data.session] = datetime.datetime.now() + \
        datetime.timedelta(hours=24)


async def send_update(sock_id: UUID4, msg: Dict):
    try:
        _, lock = sockets[sock_id]
        await lock.acquire()
        sock, _ = sockets[sock_id]
        await sock.send_json(msg)
        lock.release()
    except Exception:
        if sock_id in sockets:
            del sockets[sock_id]


async def update_all():
    tasks = [send_update(
        s, {**game_state, "cards_left": len(questions) - question_idx}) for s in sockets.keys()]
    await asyncio.gather(*tasks)


@app.post("/api/admin/next")
async def next_question(data: SessionData):
    check_admin_auth(data)
    new_state = {"question": get_question(), "letter": get_letter()}
    global game_state
    game_state = new_state
    await update_all()
    return new_state


@app.post("/api/admin/reload")
async def reload(data: SessionData):
    check_admin_auth(data)
    try:
        total = reload_questions()
        await update_all()
        return {"total": total}
    except Exception as e:
        return e


@app.get("/")
async def index():
    print("index")
    return RedirectResponse(url="index.html")

app.mount("/", StaticFiles(directory="./front/build/"), name="static")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8720,
                log_level="info")
