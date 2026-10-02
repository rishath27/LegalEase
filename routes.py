from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
generator = GeminiDocumentGenerator()

class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    parties: str = Field(min_length=3, max_length=4000)
    terms: str = Field(min_length=3, max_length=10000)
    effective_date: str = Field(min_length=2, max_length=100)
    jurisdiction: str = Field(default="Not specified", max_length=200)
    additional_instructions: str = Field(default="", max_length=4000)

@router.post("/generate")
def generate_document(request: DocumentRequest):
    try:
        content = generator.generate_document(
            document_type=request.document_type, parties=request.parties,
            terms=request.terms, effective_date=request.effective_date,
            jurisdiction=request.jurisdiction,
            additional_instructions=request.additional_instructions
        )
        return {"document": content}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")
