from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.database import init_db
from app.routes import auth, upload, files
from app.config import SECRET_KEY

app = FastAPI(title="AI Notes Organizer", version="1.0")

# CORS middleware must come before SessionMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(files.router)

@app.get("/")
def root():
    return {"message": "AI Notes Organizer Backend is running!"}