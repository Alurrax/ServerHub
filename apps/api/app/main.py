from fastapi import FastAPI

app = FastAPI(
    title="ServerHub API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "ServerHub",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
