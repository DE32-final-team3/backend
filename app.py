from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def home():
    return {"Test": "Done"}


@app.get("/get")
def read_root():
    return {"Hello": "World"}
