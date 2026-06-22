from fastapi import FastAPI

app = FastAPI(title="Netease Checker API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Netease Checker API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}