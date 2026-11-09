"""
================================================================================
Modul: core.attacks
Descriere: Implementarea matematică a algoritmilor de Adversarial Machine Learning.
Rol în proiect:
  - Conține algoritmul principal de otrăvire: PGD (Projected Gradient Descent)
    combinat cu Momentum (MI-FGSM) și funcție de pierdere pe Ansamblu (Ensemble Loss).
  - Păstrează raportul de aspect și dimensiunile imaginii originale prin
    interpolare biliniară diferențiabilă (F.interpolate).
  - Optimizează zgomotul astfel încât să fie invizibil pentru ochiul uman (bila L-infinit),
    dar transferabil către modele Black-Box necunoscute (DenseNet, EfficientNet).
================================================================================
"""

import io
import base64
from PIL import Image
import torch
import torch.nn.functional as F
import torchvision.transforms as T

from core.config import normalize_batch
from core.models import model_resnet, model_mobilenet, categories


def run_ensemble_pgd(pil_image: Image.Image, epsilon: float = 0.05, steps: int = 10) -> dict:
    """
    Execută atacul iterativ PGD cu Momentum pe ansamblul format din ResNet-50 și MobileNet-V3.
    
    Parametri:
      - pil_image: Imaginea originală încărcată de utilizator (format PIL.Image).
      - epsilon: Magnitudinea maximă a zgomotului per pixel (bila L_inf, ex: 0.05 = max 5%).
      - steps: Numărul de iterații de optimizare adversarială (recomandat: 8 - 12).

    Returnează:
      - Dicționar cu eticheta inițială, confidența, eticheta falsă și imaginea perturbată în Base64 PNG.
    """
    orig_w, orig_h = pil_image.size

    # --------------------------------------------------------------------------
    # Pasul A: Redimensionare preventivă opțională
    # Dacă utilizatorul încarcă o fotografie foarte mare (> 1000px), o scalăm proporțional
    # pentru a asigura o viteză de calcul de sub 0.5 secunde pe CPU.
    # --------------------------------------------------------------------------
    max_dim = 1000
    if max(orig_w, orig_h) > max_dim:
        scale = max_dim / max(orig_w, orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        pil_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Conversie PIL [0..255] -> Tensor PyTorch [0.0..1.0] cu dimensiunea [Batch=1, C=3, H, W]
    x_clean = T.ToTensor()(pil_image).unsqueeze(0)

    # --------------------------------------------------------------------------
    # Pasul B: Inferență de referință pe imaginea curată (Ground Truth)
    # --------------------------------------------------------------------------
    # Interpolăm la 224x224 (ResNet-50), normalizăm și obținem predicția curată
    resized_clean = F.interpolate(x_clean, size=(224, 224), mode="bilinear", align_corners=False)
    with torch.no_grad():
        out_clean = model_resnet(normalize_batch(resized_clean))
        probs_clean = F.softmax(out_clean, dim=1)
        orig_conf, orig_idx = torch.max(probs_clean, dim=1)
        orig_label = categories[orig_idx.item()]

    # target_class este clasa adevărată pe care vrem să o "sabotăm" (maximizăm eroarea față de ea)
    target_class = torch.tensor([orig_idx.item()])

    # --------------------------------------------------------------------------
    # Pasul C: Inițializarea parametrilor PGD și a vectorului de Momentum
    # --------------------------------------------------------------------------
    # alpha: Pasul de învățare la fiecare iterație (step size)
    alpha = (epsilon / steps) * 1.5
    
    # decay: Factorul de atenuare a impulsului acumulat (Momentum = 1.0 păstrează viteza)
    decay = 1.0
    momentum = torch.zeros_like(x_clean)
    
    # x_adv începe ca o clonă a imaginii curate
    x_adv = x_clean.clone().detach()

    # --------------------------------------------------------------------------
    # Pasul D: Bucla de Optimizare Adversarială (The PGD Optimization Loop)
    # --------------------------------------------------------------------------
    for step in range(steps):
        # Activăm calculul de gradiente direct pe pixelii imaginii!
        x_adv.requires_grad = True

        # Redimensionare biliniară diferențiabilă și normalizare
        resized = F.interpolate(x_adv, size=(224, 224), mode="bilinear", align_corners=False)
        norm = normalize_batch(resized)

        # 1. Calculăm eroarea pe primul model (ResNet-50)
        out_resnet = model_resnet(norm)
        loss_resnet = F.cross_entropy(out_resnet, target_class)

        # 2. Calculăm eroarea pe al doilea model (MobileNet-V3)
        out_mobilenet = model_mobilenet(norm)
        loss_mobilenet = F.cross_entropy(out_mobilenet, target_class)

        # 3. Ensemble Loss: Suma erorilor forțează zgomotul să saboteze AMBELE rețele simultan,
        # eliminând dependența de o singură arhitectură (Adversarial Overfitting).
        total_loss = loss_resnet + loss_mobilenet

        # Curățăm gradientele anterioare și executăm Backpropagation
        model_resnet.zero_grad()
        model_mobilenet.zero_grad()
        total_loss.backward()

        with torch.no_grad():
            grad = x_adv.grad.data
            
            # Normalizăm gradientul prin norma L1 medie pentru a preveni explozia valorilor
            grad_norm = grad / (torch.mean(torch.abs(grad)) + 1e-8)
            
            # Acumulăm impulsul (Momentum - MI-FGSM): ajută la traversarea minimelor locale
            momentum = decay * momentum + grad_norm

            # Gradient Ascent (+ alpha): adăugăm zgomot în direcția creșterii erorii
            x_adv = x_adv + alpha * momentum.sign()

            # Proiecția în Bila L_infinit: ne asigurăm că |x_adv - x_clean| <= epsilon
            # Dacă un pixel a deviat prea mult, îl tragem înapoi la limita +/- epsilon
            eta = torch.clamp(x_adv - x_clean, min=-epsilon, max=epsilon)
            
            # Trunchiem pixelii în intervalul valid de culoare [0.0, 1.0]
            x_adv = torch.clamp(x_clean + eta, min=0.0, max=1.0)

    # --------------------------------------------------------------------------
    # Pasul E: Predicția finală pe imaginea perturbată (verificare cu ResNet-50)
    # --------------------------------------------------------------------------
    with torch.no_grad():
        resized_adv = F.interpolate(x_adv, size=(224, 224), mode="bilinear", align_corners=False)
        out_adv = model_resnet(normalize_batch(resized_adv))
        probs_adv = F.softmax(out_adv, dim=1)
        adv_conf, adv_idx = torch.max(probs_adv, dim=1)
        adv_label = categories[adv_idx.item()]

    # --------------------------------------------------------------------------
    # Pasul F: Exportul imaginii perturbate în format Base64 PNG (gata de afișat în web)
    # --------------------------------------------------------------------------
    perturbed_pil = T.ToPILImage()(x_adv.squeeze(0))
    buffered = io.BytesIO()
    perturbed_pil.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {
        "original_label": orig_label,
        "original_confidence": round(orig_conf.item() * 100, 2),
        "poisoned_label": adv_label,
        "poisoned_confidence": round(adv_conf.item() * 100, 2),
        "epsilon": epsilon,
        "steps": steps,
        "poisoned_image_base64": f"data:image/png;base64,{img_base64}"
    }
