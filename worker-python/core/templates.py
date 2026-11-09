"""
================================================================================
Modul: core.templates
Descriere: Șabloane HTML/CSS/JS pentru interfețele demonstrative interactive.
Rol în proiect:
  - ATTACKER_HTML: Interfața web pentru Atacatorul Ensemble PGD (servită pe portul 8000).
  - EVALUATOR_HTML: Interfața web pentru Evaluatorul Orb Black-Box (servită pe portul 8001).
Notă:
  - Paginile folosesc Tailwind CSS via CDN și JavaScript vanilie pentru apeluri asincrone fetch()
    fără a necesita un build-step de frontend în această fază.
================================================================================
"""

ATTACKER_HTML = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ensemble PGD - Universal Poisoning</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">
    <div class="max-w-4xl mx-auto space-y-8">
        <div class="text-center space-y-2">
            <span class="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-xs font-semibold rounded-full border border-indigo-500/20">
                Phase 1: Ensemble PGD + Momentum (Transferable)
            </span>
            <h1 class="text-3xl font-bold tracking-tight text-white">Universal Data Poisoning Engine</h1>
            <p class="text-slate-400 text-sm max-w-xl mx-auto">
                Atac pe ansamblu (ResNet-50 + MobileNet-V3) cu Momentum, proiectat să fie transferabil către modele Black-Box necunoscute.
            </p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                <div class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-6 text-center cursor-pointer transition"
                     onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" accept="image/*" class="hidden" onchange="previewFile(event)">
                    <div id="dropText" class="space-y-2">
                        <svg class="mx-auto h-10 w-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                        <p class="text-sm font-medium text-slate-300">Apasă pentru a alege o imagine</p>
                        <p class="text-xs text-slate-500">Păstrează proporțiile și calitatea nativă</p>
                    </div>
                    <img id="localPreview" class="hidden max-h-52 mx-auto rounded-lg shadow-md mt-2 object-contain" />
                </div>

                <div class="space-y-5">
                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="text-sm font-semibold text-slate-300">Perturbare Epsilon (&epsilon;):</label>
                            <span id="epsValue" class="text-sm font-mono text-indigo-400 font-bold">0.05</span>
                        </div>
                        <input type="range" id="epsInput" min="0.02" max="0.10" step="0.01" value="0.05"
                               class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                               oninput="document.getElementById('epsValue').innerText = this.value">
                        <p class="text-xs text-slate-500 mt-1">Recomandat 0.04 - 0.06 pentru transferabilitate maximă.</p>
                    </div>

                    <div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="text-sm font-semibold text-slate-300">Iterații PGD:</label>
                            <span id="stepsValue" class="text-sm font-mono text-indigo-400 font-bold">10 pași</span>
                        </div>
                        <input type="range" id="stepsInput" min="5" max="20" step="1" value="10"
                               class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                               oninput="document.getElementById('stepsValue').innerText = this.value + ' pași'">
                    </div>

                    <button id="btnSubmit" onclick="runPoisoning()" disabled
                            class="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 font-semibold rounded-xl transition shadow-lg text-white">
                        Alege o imagine mai întâi
                    </button>
                </div>
            </div>
        </div>

        <div id="resultsCard" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
            <h2 class="text-lg font-bold text-white border-b border-slate-800 pb-3 flex items-center justify-between">
                <span>⚡ Rezultat Atac Ansamblu</span>
                <span class="text-xs text-emerald-400 font-normal">Gata pentru testare în Evaluator (port 8001)</span>
            </h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-3 bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                    <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">Imagine Curată</span>
                    <img id="origImgDisplay" class="w-full h-64 object-contain rounded-lg bg-black/40" />
                    <div>
                        <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Predicție Corectă:</p>
                        <p id="origLabel" class="text-lg font-bold text-white capitalize">-</p>
                        <p id="origConf" class="text-sm text-emerald-400 font-medium">Confidență: -%</p>
                    </div>
                </div>

                <div class="space-y-3 bg-slate-950 p-4 rounded-xl border border-rose-500/40">
                    <span class="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-1 rounded">Imagine Protejată (Universal Poisoned)</span>
                    <img id="poisonedImgDisplay" class="w-full h-64 object-contain rounded-lg bg-black/40" />
                    <div>
                        <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Predicție ResNet-50:</p>
                        <p id="poisonedLabel" class="text-lg font-bold text-rose-400 capitalize">-</p>
                        <p id="poisonedConf" class="text-sm text-rose-300 font-medium">Confidență: -%</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;

        function previewFile(event) {
            const file = event.target.files[0];
            if (!file) return;
            selectedFile = file;
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById('localPreview');
                preview.src = e.target.result;
                preview.classList.remove('hidden');
                document.getElementById('dropText').classList.add('hidden');
                const btn = document.getElementById('btnSubmit');
                btn.disabled = false;
                btn.innerText = "⚡ Generează Zgomot Universal";
            }
            reader.readAsDataURL(file);
        }

        async function runPoisoning() {
            if (!selectedFile) return;
            const btn = document.getElementById('btnSubmit');
            btn.disabled = true;
            btn.innerText = "Optimizare pe ansamblu de rețele...";

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('epsilon', document.getElementById('epsInput').value);
            formData.append('steps', document.getElementById('stepsInput').value);

            try {
                const response = await fetch('/poison', { method: 'POST', body: formData });
                if (!response.ok) throw new Error("Eroare la procesare");
                const data = await response.json();

                document.getElementById('resultsCard').classList.remove('hidden');
                document.getElementById('origImgDisplay').src = document.getElementById('localPreview').src;
                document.getElementById('origLabel').innerText = data.original_label;
                document.getElementById('origConf').innerText = "Confidență: " + data.original_confidence + "%";

                document.getElementById('poisonedImgDisplay').src = data.poisoned_image_base64;
                document.getElementById('poisonedLabel').innerText = data.poisoned_label;
                document.getElementById('poisonedConf').innerText = "Confidență: " + data.poisoned_confidence + "%";

                document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth' });
            } catch (err) {
                alert("Eroare: " + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = "⚡ Generează Zgomot Universal";
            }
        }
    </script>
</body>
</html>
"""

EVALUATOR_HTML = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blind AI Evaluator - Multi-Architecture</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Inter', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-6">
    <div class="max-w-2xl mx-auto space-y-6">
        <div class="text-center space-y-2">
            <span class="px-3 py-1 bg-amber-500/10 text-amber-400 text-xs font-semibold rounded-full border border-amber-500/20">
                Blind Multi-Model Evaluator
            </span>
            <h1 class="text-2xl font-bold tracking-tight text-white">Testare Oarbă (Black-Box Testing)</h1>
            <p class="text-slate-400 text-sm">
                Testează imaginea otrăvită pe modele pe care atacatorul <b>nu le-a văzut niciodată</b> (DenseNet-121, EfficientNet-B0).
            </p>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
            <div class="border-2 border-dashed border-slate-700 hover:border-amber-500 rounded-xl p-6 text-center cursor-pointer transition"
                 onclick="document.getElementById('fileInput').click()">
                <input type="file" id="fileInput" accept="image/*" class="hidden" onchange="onFileSelected(event)">
                <div id="dropText" class="space-y-2">
                    <svg class="mx-auto h-10 w-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <p class="text-sm font-medium text-slate-300">Încarcă imaginea pentru identificare oarbă</p>
                    <p class="text-xs text-slate-500">Trage poza descărcată din generatorul de pe portul 8000</p>
                </div>
                <img id="preview" class="hidden max-h-56 mx-auto rounded-lg shadow-md mt-2 object-contain" />
            </div>

            <div>
                <label class="text-sm font-semibold text-slate-300 block mb-2">Alege Arhitectura Modelului:</label>
                <select id="modelSelect" class="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200">
                    <optgroup label="Modele din Ansamblu (White-Box Verification)">
                        <option value="resnet50">ResNet-50</option>
                        <option value="mobilenet">MobileNet-V3</option>
                    </optgroup>
                    <optgroup label="Modele Necunoscute (True Black-Box Testing)">
                        <option value="densenet" selected>DenseNet-121 (Dense Connections - Recomandat)</option>
                        <option value="efficientnet">EfficientNet-B0 (Compound Scaling)</option>
                    </optgroup>
                </select>
            </div>

            <button id="btnClassify" onclick="classifyImage()" disabled
                    class="w-full py-3 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-800 disabled:text-slate-600 font-semibold rounded-xl transition text-white">
                Selectează o imagine mai întâi
            </button>
        </div>

        <div id="resultsBox" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
            <h3 class="text-base font-bold text-white border-b border-slate-800 pb-2 flex justify-between items-center">
                <span>📊 Ce „vede” AI-ul (Top 5 Predicții):</span>
                <span id="modelBadge" class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-amber-400"></span>
            </h3>
            <div id="topList" class="space-y-2"></div>
        </div>
    </div>

    <script>
        let chosenFile = null;

        function onFileSelected(e) {
            const f = e.target.files[0];
            if (!f) return;
            chosenFile = f;
            const reader = new FileReader();
            reader.onload = function(evt) {
                const img = document.getElementById('preview');
                img.src = evt.target.result;
                img.classList.remove('hidden');
                document.getElementById('dropText').classList.add('hidden');
                const btn = document.getElementById('btnClassify');
                btn.disabled = false;
                btn.innerText = "🔍 Rulează Identificarea Oarbă";
            }
            reader.readAsDataURL(f);
        }

        async function classifyImage() {
            if (!chosenFile) return;
            const btn = document.getElementById('btnClassify');
            btn.disabled = true;
            btn.innerText = "Evaluare oarbă în curs...";

            const formData = new FormData();
            formData.append('file', chosenFile);
            const modelChoice = document.getElementById('modelSelect').value;

            try {
                const res = await fetch(`/classify?model_name=${modelChoice}`, { method: 'POST', body: formData });
                const data = await res.json();

                document.getElementById('modelBadge').innerText = "Model: " + data.model_used.toUpperCase();
                const list = document.getElementById('topList');
                list.innerHTML = "";

                data.top_predictions.forEach((item, index) => {
                    const isTop1 = index === 0;
                    const row = document.createElement('div');
                    row.className = `p-3 rounded-lg border ${isTop1 ? 'bg-amber-500/10 border-amber-500/30' : 'bg-slate-950 border-slate-800'} flex justify-between items-center`;
                    row.innerHTML = `
                        <div class="flex items-center gap-3">
                            <span class="text-xs font-mono px-2 py-0.5 rounded ${isTop1 ? 'bg-amber-500 text-black font-bold' : 'bg-slate-800 text-slate-400'}">#${index + 1}</span>
                            <span class="capitalize text-sm font-semibold ${isTop1 ? 'text-amber-300 text-base' : 'text-slate-300'}">${item.class_name}</span>
                        </div>
                        <span class="font-mono text-sm ${isTop1 ? 'text-amber-400 font-bold' : 'text-slate-400'}">${item.confidence}%</span>
                    `;
                    list.appendChild(row);
                });

                document.getElementById('resultsBox').classList.remove('hidden');
            } catch (err) {
                alert("Eroare: " + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = "🔍 Rulează Identificarea Oarbă";
            }
        }
    </script>
</body>
</html>
"""