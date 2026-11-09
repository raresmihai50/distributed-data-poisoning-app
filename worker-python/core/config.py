"""
================================================================================
Modul: core.config
Descriere: Configurații matematice și constante standard pentru rețele neurale.
Rol în proiect:
  - Definește mediile (mean) și deviațiile standard (std) oficiale ale setului ImageNet.
  - Oferă funcția de normalizare diferențiabilă pe batch-uri de tensori PyTorch.
================================================================================
"""

import torch

# Constantele oficiale ImageNet pentru canalele [R, G, B]:
# Orice model antrenat pe ImageNet așteaptă ca pixelii [0.0, 1.0] să fie centrați în jurul
# acestor valori medii și împărțiți la deviația standard corespunzătoare.
# Dimensiunea [1, 3, 1, 1] permite aplicarea directă pe tensori de forma [Batch, Channels, Height, Width].
IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def normalize_batch(tensor: torch.Tensor) -> torch.Tensor:
    """
    Normalizează un tensor de imagine aflat în intervalul [0.0, 1.0] conform distribuției ImageNet.
    
    Formula aplicată per-canal:
        z = (x - mean) / std
        
    De ce ținem normalizarea ca o funcție separată?
      - Imaginea perturbată este stocată și manipulată în spațiul nativ [0.0, 1.0], astfel încât
        parametrul epsilon (ex: 0.05) să aibă o semnificație fizică directă (maxim 5% variație per pixel).
      - Normalizarea se aplică doar în momentul transmiterii tensorului către straturile rețelei.
    """
    return (tensor - IMAGENET_MEAN.to(tensor.device)) / IMAGENET_STD.to(tensor.device)
