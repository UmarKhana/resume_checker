from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from app.features import process_resume
from app.shortlist import shortlist
import os

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze_resumes(job_role: str, files: list[UploadFile] = File(...)):
    resumes = []
    
    # Use absolute path
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    for f in files:
        file_path = os.path.join(upload_dir, f.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await f.read())

        text = process_resume(file_path)
        resumes.append((f.filename, text))

    results = shortlist(resumes, job_role, top_k=10)
    return {"shortlisted": results}


@app.get("/download/{filename}")
async def download_cv(filename: str):
    # Use absolute path
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    file_path = os.path.join(upload_dir, filename)
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    return {"error": "File not found"}

