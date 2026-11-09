"""
================================================================================
Microserviciu: evaluator.py (Blind AI Evaluator / Scraper Bot Simulator)
Port implicit: 8001 (Rulare: uvicorn evaluator:app --reload --port 8001)
Rol în proiect:
  - Simulează un bot de web scraping sau un clasificator terț complet independent.
  - Primește imagini „în orb” (fără să știe că au fost modificate sau ce clasă aveau inițial).
  - Permite testarea pe 4 arhitecturi:
      1. ResNet-50 (White-Box verification)
      2. MobileNet-V3 (White-Box verification)
      3. DenseNet-121 (True Black-Box - arhitectură neatinsă de atacator)
      4. EfficientNet-B0 (True Black-Box - arhitectură neatinsă de atacator)
  - Returnează Top-5 predicții cu procente de confidență.
================================================================================
"""

import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.transforms as T

# Importăm constantele și modelele pre-încărcate
from core.config import IMAGENET_MEAN, IMAGENET_STD
from core.models import model_resnet, model_mobilenet, model_densenet, model_efficientnet, categories
from core.templates import EVALUATOR_HTML

app = FastAPI(
    title="Blind AI Evaluator (Multi-Model Scraper Simulator)",
    description="Microserviciu de testare oarbă pe arhitecturi necunoscute de atacator",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dicționar de rutare pentru selectarea dinamică a modelului ales de utilizator
MODELS_MAP = {
    "resnet50": model_resnet,
    "mobilenet": model_mobilenet,
    "densenet": model_densenet,
    "efficientnet": model_efficientnet
}


@app.get("/", response_class=HTMLResponse)
def index():
    """
    Rădăcina serviciului (http://localhost:8001/):
    Returnează interfața de testare oarbă unde utilizatorul poate încărca poza
    otrăvită și selecta arhitectura dorită.
    """
    return EVALUATOR_HTML


@app.post("/classify")
async def classify(file: UploadFile = File(...), model_name: str = "densenet"):
    """
    Endpoint de clasificare oarbă:
      - file: imaginea primită pentru evaluare.
      - model_name: modelul de clasificare ales (ex: "densenet", "efficientnet", "resnet50", "mobilenet").
      - Returnează top 1 și top 5 etichete prezise cu scorurile de confidență aferente.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Fișierul trebuie să fie o imagine.")

    try:
        # Citire și conversie în tensor [1, 3, H, W]
        image_bytes = await file.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor_img = T.ToTensor()(pil_image).unsqueeze(0)

        # Selectăm modelul corespunzător (default: DenseNet-121)
        selected_model = MODELS_MAP.get(model_name, model_densenet)

        # Redimensionare la 224x224 și normalizare ImageNet
        resized = F.interpolate(tensor_img, size=(224, 224), mode="bilinear", align_corners=False)
        norm = (resized - IMAGENET_MEAN) / IMAGENET_STD

        # Inferență oarbă în mod no_grad
        with torch.no_grad():
            outputs = selected_model(norm)
            probs = F.softmax(outputs, dim=1)
            # Extragem primele 5 probabilități cele mai mari și indicii lor
            top_probs, top_indices = torch.topk(probs, k=5, dim=1)

        # Mapăm indicii la denumirile categoriilor ImageNet
        predictions = [
            {"class_name": categories[idx.item()], "confidence": round(p.item() * 100, 2)}
            for p, idx in zip(top_probs[0], top_indices[0])
        ]

        return {
            "model_used": model_name,
            "top1_label": predictions[0]["class_name"],
            "top1_confidence": predictions[0]["confidence"],
            "top_predictions": predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la clasificare: {str(e)}")
