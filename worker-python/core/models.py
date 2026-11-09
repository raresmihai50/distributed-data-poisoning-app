"""
================================================================================
Modul: core.models
Descriere: Încărcarea și gestionarea centralizată a modelelor de viziune computerizată.
Rol în proiect:
  - Încarcă cele 4 arhitecturi de rețele neurale convoluționale (CNN) pre-antrenate pe ImageNet (1000 clase).
  - Modele pentru atac (Ensemble): ResNet-50 și MobileNet-V3.
  - Modele pentru testare oarbă (Black-Box): DenseNet-121 și EfficientNet-B0.
  - Pune toate modelele în mod `.eval()` (înghețarea statisticilor de BatchNorm și Dropout).
================================================================================
"""

from torchvision.models import (
    resnet50, ResNet50_Weights,
    mobilenet_v3_large, MobileNet_V3_Large_Weights,
    densenet121, DenseNet121_Weights,
    efficientnet_b0, EfficientNet_B0_Weights
)

print("Se încarcă modelele PyTorch pre-antrenate...")

# ------------------------------------------------------------------------------
# 1. ResNet-50 (Residual Networks - He et al., 2015)
# Arhitectură clasică bazată pe conexiuni reziduale de tip "skip-connection" (50 straturi).
# Este modelul principal folosit ca țintă de referință în atac.
# ------------------------------------------------------------------------------
resnet_weights = ResNet50_Weights.DEFAULT
model_resnet = resnet50(weights=resnet_weights).eval()

# Lista oficială cu cele 1000 de denumiri textuale ale claselor ImageNet (comună tuturor celor 4 modele)
categories = resnet_weights.meta["categories"]

# ------------------------------------------------------------------------------
# 2. MobileNet-V3-Large (Howard et al., 2019)
# Arhitectură optimizată pentru dispozitive mobile și boți rapizi de scraping,
# folosind convoluții separabile în adâncime (Depthwise Separable Convolutions).
# Este al doilea model din ansamblul de atac pentru a preveni supra-adaptarea la ResNet.
# ------------------------------------------------------------------------------
mobilenet_weights = MobileNet_V3_Large_Weights.DEFAULT
model_mobilenet = mobilenet_v3_large(weights=mobilenet_weights).eval()

# ------------------------------------------------------------------------------
# 3. DenseNet-121 (Densely Connected Convolutional Networks - Huang et al., 2017)
# Arhitectură în care fiecare strat primește intrări de la toate straturile anterioare.
# Folosit exclusiv în evaluator.py pentru Black-Box Testing (atacatorul NU calculează gradiente pe el).
# ------------------------------------------------------------------------------
densenet_weights = DenseNet121_Weights.DEFAULT
model_densenet = densenet121(weights=densenet_weights).eval()

# ------------------------------------------------------------------------------
# 4. EfficientNet-B0 (Tan & Le, 2019)
# Arhitectură modernă bazată pe scalare compusă a adâncimii, lățimii și rezoluției.
# Al doilea model de testare Black-Box complet independent de procesul de otrăvire.
# ------------------------------------------------------------------------------
efficientnet_weights = EfficientNet_B0_Weights.DEFAULT
model_efficientnet = efficientnet_b0(weights=efficientnet_weights).eval()

print("Toate cele 4 modele au fost încărcate cu succes în mod inferență (.eval())!")
