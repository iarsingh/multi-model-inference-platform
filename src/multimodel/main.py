from multimodel.ops import router as ops_router
from fastapi import FastAPI, HTTPException
from multimodel.registry import InputError, champion, promote, register

app = FastAPI()
app.include_router(ops_router, prefix="/v1")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/champion")
def get_champion():
    return champion()


@app.post("/models")
def post_model(body: dict):
    try:
        return register(body.get("name"), body.get("version"), body.get("metrics"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/promote")
def post_promote(body: dict):
    try:
        return promote(body.get("name"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
