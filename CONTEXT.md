# Project Context & Architecture Guide (CONTEXT.md)

## 1. Project Overview
**App Name:** Distributed Data Poisoning App
**Academic Thesis Title:** Arhitectură distribuită poliglotă pentru protecția datelor digitale și mitigarea proceselor de Web Scraping automatizat prin tehnici de Adversarial Machine Learning.
**Goal:** A distributed, polyglot system (Java 21 + Python + Svelte 5) that protects visual digital assets from unauthorized AI scraping through a dual shield:
1. **API-level Anti-Scraping Shield:** Rate limiting, honeypots, and HTTP Tarpits.
2. **Adversarial Machine Learning Engine:** Invisible pixel-level mathematical perturbations (**PGD - Projected Gradient Descent / Iterative-FGSM**, evolved from baseline **FGSM**) and EXIF metadata poisoning to fool AI classifiers (e.g., ResNet-50) while preserving native aspect ratio and visual quality for humans.

---

## 2. CRITICAL INTERACTION RULE: MENTOR & PAIR-PROGRAMMER MODE
**READ THIS BEFORE TAKING ANY ACTION:**
* **DO NOT automatically write, create, or edit files in the workspace** (do not auto-apply changes or run agentic file edits) unless the user explicitly commands you to do so (e.g., *"scrie tu codul în fișier"*, *"aplică modificarea"*, *"modifică în..."*).
* **Default Behavior:** Act as a mentor and pair-programming guide. Explain the architectural logic step-by-step and **only display the suggested code snippets inside the chat window**.
* **Why:** The user wants to learn the architecture deeply for their Master's Dissertation defense by typing the code themselves or manually copying and pasting from the chat window.
* **Exception:** If the user explicitly asks you to write/generate the code directly into the project files, you are then allowed to create or modify the files automatically.

---

## 3. Current Project Status & Progress Tracker
* ✅ **Git & Environment Setup:** Repository initialized, connected to GitHub (`main` branch), `.gitignore` configured for Java & Python, upgraded to **Java 21 LTS**.
* ✅ **Phase 1 - Step 1 (`worker-python/`): COMPLETED & VERIFIED**
  * Python `venv` configured with `fastapi`, `uvicorn`, `torch`, `torchvision`, `pillow`, `python-multipart`.
  * **Research & Experimental Evolution (Important for Thesis):**
    * *Initial Baseline (FGSM):* Tested classic 1-step Fast Gradient Sign Method (Goodfellow et al., 2014) with `CenterCrop(224)`. Discovered two limitations: (1) cropping altered the original image aspect ratio, and (2) single-step linear perturbation on a non-linear 50-layer network only caused minor semantic shifts to neighboring classes (e.g., *Giant Panda* $\rightarrow$ *Lesser Panda*).
    * *Upgraded Engine (PGD / I-FGSM):* Implemented iterative **Projected Gradient Descent** (Madry et al., 2018) with $L_\infty$ $\epsilon$-ball projection and differentiable bilinear interpolation (`F.interpolate` to $224 \times 224$). This preserves the full native resolution/aspect ratio of the original image while reliably crossing the ResNet-50 decision boundary into completely unrelated classes at imperceptible noise levels ($\epsilon \approx 0.03$, $7$ steps).
  * Includes both the `POST /poison` REST endpoint and a built-in dark-mode test UI at `GET /` (`http://localhost:8000/`).
* ⏳ **Phase 1 - Step 2 (`backend-java/`): NEXT UP**
  * Java 21 + Spring Boot 3 Orchestrator (`POST /api/demo/protect`) using Virtual Threads, `RestClient`, and Strategy Pattern (`PoisoningStrategy` $\rightarrow$ `PgdStrategy`).
* ⏳ **Phase 1 - Step 3 (`frontend/`): PENDING**
  * Svelte 5 (Runes) + Tailwind CSS interactive dashboard (`http://localhost:5173`).

---

## 4. Development Phases (CRITICAL FOR CODE GENERATION)

We are building **Distributed Data Poisoning App** in **two phases**. Always check which phase the user is currently asking about:

### PHASE 1: Bare-Minimum MVP / Demo (CURRENT FOCUS)
* **Goal:** Prove the end-to-end polyglot flow (`Svelte 5 -> Spring Boot 3 -> FastAPI/PyTorch`) and demonstrate live AI model deception using PGD (Iterative-FGSM).
* **No Databases / No Docker / No Message Brokers yet:** Everything runs **in-memory** via synchronous REST APIs.
* **Flow:**
  1. **Svelte 5 (`localhost:5173`)**: User uploads an image and selects `epsilon` (noise intensity, e.g., `0.01` to `0.08`) and optionally `steps` (PGD iterations, default `7`).
  2. **Java 21 + Spring Boot 3 (`localhost:8080`)**: Receives `MultipartFile` at `POST /api/demo/protect`. Uses **Strategy Pattern** skeleton (`PoisoningStrategy` -> `PgdStrategy`) and `RestClient` to forward the image synchronously to Python.
  3. **Python FastAPI + PyTorch (`localhost:8000`)**: Receives the image at `POST /poison`, runs initial inference on pre-trained `ResNet-50` (ImageNet weights), computes iterative gradients and applies **PGD** while preserving original dimensions via differentiable interpolation, runs post-poisoning inference, and returns a JSON containing:
     * `original_label` & `original_confidence`
     * `poisoned_label` & `poisoned_confidence`
     * `epsilon` & `steps`
     * `poisoned_image_base64`
  4. **Svelte 5**: Renders a Before/After visual comparison showing the identical-looking images alongside the fooled AI predictions.

### PHASE 2: Full Distributed Architecture (FINAL DISSERTATION)
* **Containerization:** Fully orchestrated via `docker-compose.yml`.
* **Anti-Scraping Shield (Java):** Chain of Responsibility Pattern, Bucket4j + Redis (distributed rate limiting), Honeypot links, and HTTP Tarpit leveraging **Java 21 Virtual Threads** (`spring.threads.virtual.enabled=true`).
* **Resilience & Orchestration (Java):** Resilience4j (Circuit Breaker) + Strategy Pattern (`PgdStrategy`, `FgsmStrategy`, `ExifStrategy`).
* **Claim Check Pattern (Kafka + MinIO):** Spring Boot stores raw images in **MinIO** (S3-compatible object storage) and publishes only a lightweight claim-check ticket (file ID/path + strategy metadata) to **Apache Kafka (KRaft mode - NO ZooKeeper)**.
* **Competing Consumers (Python Workers):** Scalable Docker containers consuming from Kafka, downloading from MinIO, applying PyTorch PGD/FGSM or EXIF Prompt Injection, uploading back to MinIO, and handling Fault Tolerance + Dead Letter Queues (DLQ).
* **Real-time Monitoring:** WebSockets pushing live worker progress and tarpit bot metrics to the Svelte 5 dashboard.

---

## 5. Tech Stack & Strict Coding Conventions

### A. Frontend (`frontend/`)
* **Framework:** Svelte 5 (SvelteKit / Vite).
* **CRITICAL SVELTE 5 RULE:** Always use **Svelte 5 Runes** (`$state`, `$derived`, `$effect`, `$props`). **NEVER** use legacy Svelte 3/4 syntax (`export let`, `$:`, `on:click` -> use `onclick` instead).
* **Styling & UI:** Tailwind CSS + `shadcn-svelte` (Svelte 5 / Bits UI compatible) + Dark Mode UI.
* **Port:** `5173` (Configure CORS in Spring Boot to allow `http://localhost:5173`).

### B. Orchestrator & Security Shield (`backend-java/` or `app/`)
* **Language & Framework:** Java 21 + Spring Boot 3.3+.
* **Conventions:**
  * Application Name: `distributed-data-poisoning-app`
  * Enable Java 21 Virtual Threads: `spring.threads.virtual.enabled=true`.
  * Use modern Spring 6 / Boot 3 `RestClient` (not the deprecated `RestTemplate`) for synchronous HTTP calls to Python in Phase 1.
  * Use Java `record` for DTOs (`PoisonRequest`, `PoisonResponse`).
  * Keep the `PoisoningStrategy` interface clean so we can seamlessly swap synchronous REST calls (Phase 1) with Kafka + MinIO Claim Check publishing (Phase 2).
* **Port:** `8080`.

### C. AI Worker Microservice (`worker-python/`)
* **Language & Libraries:** Python 3.11+ (3.13), `fastapi`, `uvicorn`, `torch`, `torchvision`, `pillow`, `python-multipart`.
* **AI Model:** `torchvision.models.resnet50(weights=ResNet50_Weights.DEFAULT)` set to `.eval()` mode.
* **PGD (Iterative-FGSM) Mathematical Implementation:**
  * Preserve full image aspect ratio; use differentiable `F.interpolate(x, size=(224, 224), mode="bilinear")` for model forward/backward passes.
  * Use standard ImageNet normalization (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
  * Iteratively compute `CrossEntropyLoss` against the initial top-1 predicted class over `steps` iterations with step size $\alpha = \frac{\epsilon}{\text{steps}} \times 1.5$.
  * Apply gradient ascent step (`x_adv = x_adv + alpha * grad.sign()`), project perturbation into the $L_\infty$ $\epsilon$-ball (`clamp(x_adv - x_clean, -epsilon, epsilon)`), and clamp pixel values to `[0, 1]` before encoding back to Base64 PNG.
* **Port:** `8000`.

---

## 6. Monorepo Directory Structure
```text
distributed-data-poisoning-app/
├── CONTEXT.md                 # This file (AI Context, Architecture & Progress)
├── GIT_CHEAT_SHEET.md         # Quick Git command reference
├── docker-compose.yml         # Phase 2 (Kafka KRaft, MinIO, Redis, Kafka-UI)
├── frontend/                  # Svelte 5 + Tailwind + shadcn-svelte (Port 5173)
├── backend-java/ (or app/)    # Java 21 + Spring Boot 3 Orchestrator (Port 8080)
└── worker-python/             # Python + FastAPI + PyTorch PGD Worker (Port 8000)
```
