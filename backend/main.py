
from pathlib import Path
from zipfile import BadZipFile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pipeline import process_whatsapp_zip


app = FastAPI(
    title="CampusPilot API",
    description="Evidence-grounded campus announcement intelligence",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@app.get("/health")
def health():
    return {"status": "ok", "service": "CampusPilot"}


@app.post("/analyze")
async def analyze_chat(file: UploadFile = File(...)):
    filename = file.filename or ""

    if Path(filename).suffix.lower() != ".zip":
        raise HTTPException(
            status_code=400,
            detail="Upload a WhatsApp export ZIP file.",
        )

    content = await file.read(MAX_UPLOAD_BYTES + 1)

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="ZIP exceeds the 25 MB upload limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    # Process from a temporary path. Do not keep users' exports.
    import tempfile

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".zip", delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        return process_whatsapp_zip(temp_path)

    except (BadZipFile, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {type(exc).__name__}: {exc}",
        ) from exc

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

        await file.close()
