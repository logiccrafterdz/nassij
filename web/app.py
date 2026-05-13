import os
import time
import shutil
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.append(str(Path(__file__).parent.parent))
from cli import convert_pdf_to_docx

app = FastAPI(title="Nassij API", description="PDF to DOCX Arabic Converter API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for frontend
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Temporary upload and download directories
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# In-memory status store
conversion_status = {}

def get_job_id():
    return str(int(time.time() * 1000))

def run_conversion(job_id: str, input_path: str, output_path: str, mode: str, font: str):
    try:
        def progress_cb(current, total, phase):
            conversion_status[job_id] = {
                "status": "processing",
                "progress": int((current / total) * 100),
                "message": f"Processing page {current}/{total} ({phase})..."
            }

        conversion_status[job_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting conversion..."
        }
        
        success = convert_pdf_to_docx(
            input_pdf=str(input_path),
            output_docx=str(output_path),
            mode=mode,
            preserve_diacritics=True,
            font_name=font,
            dpi=300,
            progress_callback=progress_cb
        )
        
        if success:
            conversion_status[job_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Conversion successful!",
                "download_url": f"/download/{job_id}"
            }
        else:
            conversion_status[job_id] = {
                "status": "failed",
                "progress": 0,
                "message": "Conversion failed internally."
            }
    except Exception as e:
        conversion_status[job_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main Web UI"""
    with open(static_dir / "index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/convert")
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form("balanced"),
    font: str = Form("Arial")
):
    """Upload a PDF and start conversion job"""
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"detail": "Only PDF files are supported."})
        
    job_id = get_job_id()
    input_path = TEMP_DIR / f"{job_id}_input.pdf"
    output_path = TEMP_DIR / f"{job_id}_output.docx"
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Start the conversion in the background
    background_tasks.add_task(run_conversion, job_id, input_path, output_path, mode, font)
    
    conversion_status[job_id] = {
        "status": "queued",
        "progress": 0,
        "message": "Queued for conversion..."
    }
    
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a conversion job"""
    status = conversion_status.get(job_id)
    if not status:
        return JSONResponse(status_code=404, content={"detail": "Job not found"})
    return status

@app.get("/download/{job_id}")
async def download_file(job_id: str):
    """Download the converted DOCX file"""
    output_path = TEMP_DIR / f"{job_id}_output.docx"
    if not output_path.exists():
        return JSONResponse(status_code=404, content={"detail": "File not found or expired"})
        
    return FileResponse(
        path=output_path,
        filename="nassij_converted.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting Nassij Web UI on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
