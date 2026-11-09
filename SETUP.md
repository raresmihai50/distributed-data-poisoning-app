# 🛠️ Ghid de Instalare & Centralizator de Pachete

Acest document conține toate dependințele, versiunile software și comenzile necesare pentru a instala și rula proiectul **Distributed Data Poisoning App** de la zero pe un calculator nou.

---

## 📋 1. Cerințe de Sistem (Prerequisites)
Înainte de instalare, trebuie să ai instalate global pe mașină:
* **Java 21 LTS** (ex: Oracle JDK 21 sau Eclipse Adoptium Temurin 21)
* **Apache Maven 3.9+**
* **Python 3.11+ / 3.13**
* **Node.js v20+ / v24+** cu **npm 10+**

---

## 🐍 2. Componenta AI: Python Microservices (`worker-python/`)

### Comenzi de instalare de la zero:
```powershell
cd worker-python
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Pachete instalate (`requirements.txt`) și rolul lor:
* `torch>=2.4.0`: Motorul de Deep Learning (calcul tensorial, Autograd, Backpropagation).
* `torchvision>=0.19.0`: Arhitecturile CNN pre-antrenate pe ImageNet (ResNet-50, MobileNet-V3, DenseNet-121, EfficientNet-B0).
* `fastapi>=0.115.0`: Framework-ul REST modern și asincron pentru microservicii.
* `uvicorn[standard]>=0.32.0`: Serverul ASGI de producție care rulează FastAPI.
* `pillow>=10.4.0`: Prelucrarea și conversia imaginilor (JPEG/PNG).
* `python-multipart>=0.0.12`: Permite încărcarea de fișiere imagini prin cereri HTTP multipart/form-data.

---

## ☕ 3. Componenta de Orchestrare: Java 21 Backend (`backend-java/`)

### Comenzi de compilare de la zero:
```powershell
cd backend-java
mvn clean compile
```

### Pachete și dependințe Maven (`pom.xml`):
* `org.springframework.boot:spring-boot-starter-parent (3.3.5)`: Părintele oficial Spring Boot 3.
* `org.springframework.boot:spring-boot-starter-web`:
  * Include serverul **Tomcat** încorporat.
  * Oferă adnotările REST (`@RestController`, `@PostMapping`, `@CrossOrigin`).
  * Include noul client sincron modern **`RestClient`** (Spring 6) pentru apelurile către Python.
* **Caracteristici Java 21 activate:**
  * **Java Records (`dto/PoisonResponse.java`)**: DTO-uri imutabile și thread-safe.
  * **Virtual Threads (Project Loom)**: Activat prin `spring.threads.virtual.enabled=true`.

---

## 🌐 4. Componenta de Interfață: Frontend Svelte 5 (`frontend-svelte/`)

### Comenzi de instalare de la zero:
```powershell
cd frontend-svelte
npm install
```

### Pachete npm instalate (`package.json`) și rolul lor:
* `svelte (^5.57.3)`: Versiunea revoluționară Svelte 5 bazată pe **Runes** (`$state`, `$derived`, `$props`).
* `vite (^8.3.6)`: Bundler-ul și serverul de dezvoltare ultra-rapid.
* `@sveltejs/vite-plugin-svelte`: Plugin-ul oficial de integrare între Vite și Svelte 5.
* `tailwindcss (^4.3.5)`: Framework-ul modern de stilizare CSS (Tailwind v4).
* `@tailwindcss/vite`: Plugin-ul nativ de Vite pentru Tailwind v4 (fără fișiere vechi de configurare).

---

## 🚀 5. Comenzi de Rulare Rapidă

* **Pornire completă cu un singur click:** Rulează scriptul `start-all.bat`.
* **Oprire completă a tuturor celor 4 porturi (5173, 8080, 8000, 8001):** Rulează scriptul `stop-all.bat`.