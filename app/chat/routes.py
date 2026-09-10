from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.analysis.engine import analyze_documents
from app.chat.response_formatter import format_results
from app.config import MAX_UPLOAD_MB
from app.documents.classifier import ClassificationError, classify_documents
from app.documents.text_extractor import DocumentExtractionError, extract_text

router = APIRouter(prefix="/api")


@router.post("/analyze")
async def analyze(files: list[UploadFile] = File(...)) -> JSONResponse:
    if len(files) < 2:
        return JSONResponse({"error": "Upload one JD and at least one resume."}, status_code=400)
    documents = []
    errors = []
    for upload in files:
        try:
                content = await upload.read()
                if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
                    raise DocumentExtractionError(f"{upload.filename or 'unnamed'} exceeds the {MAX_UPLOAD_MB} MB limit")
                documents.append((upload.filename or "unnamed", extract_text(upload.filename or "unnamed", content)))
        except DocumentExtractionError as exc:
            errors.append(str(exc))
    if len(documents) < 2:
        return JSONResponse({"error": "Not enough readable documents.", "details": errors}, status_code=400)
    try:
        classified = classify_documents(documents)
    except ClassificationError as exc:
        return JSONResponse({"error": str(exc), "details": errors}, status_code=400)
    result = format_results(analyze_documents(classified.jd[1], classified.resumes))
    result["identified_jd"] = classified.jd[0]
    result["warnings"] = errors
    return JSONResponse(result)
