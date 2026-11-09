"""
================================================================================
Microserviciu: main.py (Atacatorul Adversarial / AI Poisoning Worker)
Port implicit: 8000 (Rulare: uvicorn main:app --reload --port 8000)
Rol în proiect:
  - Reprezintă motorul de otrăvire a datelor în Phase 1 (și worker-ul din spatele
    cozilor Kafka în Phase 2).
  - Expune endpoint-ul REST `POST /poison` apelat de Spring Boot (Java 21).
  - Servește interfața grafică demonstrativă la `GET /` (http://localhost:8000/).
  - Deleagă calculele matematice către modulul `core.attacks.run_ensemble_pgd`.
================================================================================
"""

import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Importăm logica decuplată din pachetul 'core'
from core.attacks import run_ensemble_pgd
from core.templates import ATTACKER_HTML

# Inițializarea instanței FastAPI
app = FastAPI(
    title="Distributed Data Poisoning App - Ensemble PGD Worker",
    description="Motor Adversarial bazat pe Ensemble Loss (ResNet50 + MobileNetV3) și Momentum",
    version="1.2.0"
)

# Handler pentru afișarea detaliată în consolă a oricărei erori 422 de validare
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("❌ EROARE VALIDARE 422 DETALIATĂ:", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Activăm CORS (Cross-Origin Resource Sharing)
# Permite apelurile HTTP din frontend-ul Svelte 5 (port 5173) și din orchestratorul Java (port 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def index_page():
    """
    Rădăcina serviciului (http://localhost:8000/):
    Returnează direct pagina web interactivă (HTML/Tailwind) pentru testare vizuală rapidă.
    """
    return ATTACKER_HTML


@app.post("/poison")
async def poison_image(
    file: UploadFile = File(...),
    epsilon: float = Form(0.05),
    steps: int = Form(10)
):
    """
    Endpoint-ul principal de otrăvire adversarială:
      - Primește fișierul imagine multipart/form-data.
      - epsilon: intensitatea zgomotului (default 0.05).
      - steps: numărul de iterații PGD (default 10).
      - Execută atacul pe ansamblu și returnează etichetele și imaginea Base64.
    """
    # Validare simplă a tipului MIME
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Fișierul încărcat trebuie să fie o imagine.")

    try:
        # Citim fluxul de octeți și deschidem imaginea ca obiect PIL RGB
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Delegăm calculul matematic către motorul specializat din core.attacks
        return run_ensemble_pgd(pil_image, epsilon=epsilon, steps=steps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare internă la procesare: {str(e)}")
