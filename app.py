from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Netease Checker API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
