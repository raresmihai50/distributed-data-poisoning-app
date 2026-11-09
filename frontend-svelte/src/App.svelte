<script>
  // --- SVELTE 5 RUNES (Fără sintaxa veche export let sau $:) ---
  let selectedFile = $state(null);
  let previewUrl = $state(null);
  let epsilon = $state(0.05);
  let steps = $state(10);
  let isLoading = $state(false);
  let errorMessage = $state(null);
  let result = $state(null);

  // Stare pentru verificarea oarbă pe portul 8001
  let isEvaluating = $state(false);
  let evaluationResult = $state(null);

  function handleFileSelect(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    selectedFile = file;
    previewUrl = URL.createObjectURL(file);
    result = null;
    evaluationResult = null;
    errorMessage = null;
  }

  async function protectImage() {
    if (!selectedFile) return;

    isLoading = true;
    errorMessage = null;
    result = null;
    evaluationResult = null;

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("epsilon", epsilon.toString());
    formData.append("steps", steps.toString());

    try {
      // Apelăm orchestratorul Spring Boot din Java (port 8080)
      const res = await fetch("http://localhost:8080/api/demo/protect", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Eroare de la serverul Java (${res.status}): ${res.statusText}`);
      }

      result = await res.json();
    } catch (err) {
      errorMessage = err.message || "A apărut o problemă la comunicarea cu serverul Java.";
    } finally {
      isLoading = false;
    }
  }

  async function runBlindEvaluation(modelName = "densenet") {
    if (!result?.poisoned_image_base64) return;

    isEvaluating = true;
    try {
      // Convertim imaginea base64 în fișier Blob pentru a o trimite la evaluatorul din Python (port 8001)
      const base64Data = result.poisoned_image_base64.split(",")[1];
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "image/png" });

      const formData = new FormData();
      formData.append("file", blob, "poisoned.png");

      const res = await fetch(`http://localhost:8001/classify?model_name=${modelName}`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Evaluatorul de pe portul 8001 nu răspunde.");
      evaluationResult = await res.json();
    } catch (err) {
      alert("Eroare la testarea oarbă: " + err.message);
    } finally {
      isEvaluating = false;
    }
  }
</script>

<main class="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 font-sans">
  <div class="max-w-5xl mx-auto space-y-8">
    <!-- Header -->
    <header class="text-center space-y-3">
      <div class="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-indigo-400 text-xs font-semibold">
        <span>● Svelte 5</span>
        <span>→</span>
        <span>☕ Java 21 (8080)</span>
        <span>→</span>
        <span>🐍 PyTorch PGD (8000)</span>
      </div>
      <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight text-white">
        Distributed Data Poisoning App
      </h1>
      <p class="text-slate-400 text-sm max-w-2xl mx-auto">
        Protecția activă a imaginilor digitale împotriva proceselor automate de Web Scraping prin tehnici de 
        <span class="text-indigo-400 font-semibold">Adversarial Machine Learning (PGD + Momentum)</span>.
      </p>
    </header>

    <!-- Eroare Server -->
    {#if errorMessage}
      <div class="bg-rose-500/10 border border-rose-500/30 text-rose-300 px-4 py-3 rounded-xl text-sm flex items-center justify-between">
        <span>⚠️ {errorMessage}</span>
        <span class="text-xs text-rose-400">Asigură-te că serverul Java (8080) și Python (8000) sunt pornite.</span>
      </div>
    {/if}

    <!-- Panoul de Control -->
    <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
      <!-- Upload Box -->
      <label class="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-6 text-center cursor-pointer transition flex flex-col items-center justify-center min-h-[220px]">
        <input type="file" accept="image/*" class="hidden" onchange={handleFileSelect} />
        
        {#if previewUrl}
          <img src={previewUrl} alt="Preview" class="max-h-48 rounded-lg object-contain shadow-md" />
          <span class="text-xs text-slate-400 mt-2">Apasă pentru a alege altă poză</span>
        {:else}
          <div class="space-y-2">
            <svg class="mx-auto h-10 w-10 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <p class="text-sm font-medium text-slate-200">Apasă sau trage o imagine aici</p>
            <p class="text-xs text-slate-500">PNG, JPG, WebP</p>
          </div>
        {/if}
      </label>

      <!-- Sliders și Buton -->
      <div class="space-y-5">
        <div>
          <div class="flex justify-between items-center text-sm font-semibold mb-1">
            <span class="text-slate-300">Intensitate Zgomot (&epsilon;):</span>
            <span class="font-mono text-indigo-400 font-bold">{epsilon}</span>
          </div>
          <input type="range" min="0.01" max="0.08" step="0.005" bind:value={epsilon}
                 class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500" />
          <p class="text-xs text-slate-500 mt-1">Valoare recomandată: 0.04 - 0.05 (complet invizibil ochiului uman).</p>
        </div>

        <div>
          <div class="flex justify-between items-center text-sm font-semibold mb-1">
            <span class="text-slate-300">Iterații PGD:</span>
            <span class="font-mono text-indigo-400 font-bold">{steps} pași</span>
          </div>
          <input type="range" min="5" max="15" step="1" bind:value={steps}
                 class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500" />
        </div>

        <button onclick={protectImage} disabled={!selectedFile || isLoading}
                class="w-full py-3.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 font-semibold rounded-xl transition shadow-lg shadow-indigo-600/20 text-white flex items-center justify-center gap-2">
          {#if isLoading}
            <span class="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></span>
            <span>Orchestrare Java 21 ➔ Calcul PGD...</span>
          {:else}
            <span>⚡ Protejează Imaginea (Orchestrare Java 21)</span>
          {/if}
        </button>
      </div>
    </section>

    <!-- Rezultatele Comparatiei -->
    {#if result}
      <section class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>⚡ Rezultatul Atacului Adversarial</span>
          </h2>
          <span class="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 font-mono">
            Status: Succes (200 OK)
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Card Original -->
          <div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">1. Imagine Originală (Model Curat)</span>
            <img src={previewUrl} alt="Original" class="w-full h-64 object-contain rounded-lg bg-black/40" />
            <div class="border-t border-slate-800/80 pt-2">
              <p class="text-xs text-slate-400 uppercase font-semibold">Predicție Corectă:</p>
              <p class="text-lg font-bold text-white capitalize">{result.original_label}</p>
              <p class="text-sm text-emerald-400 font-medium">Confidență: {result.original_confidence}%</p>
            </div>
          </div>

          <!-- Card Poisoned -->
          <div class="bg-slate-950 p-4 rounded-xl border border-rose-500/30 space-y-3">
            <span class="text-xs font-bold text-rose-400 bg-rose-500/10 px-2 py-1 rounded">2. Imagine Protejată (Model Păcălit)</span>
            <img src={result.poisoned_image_base64} alt="Poisoned" class="w-full h-64 object-contain rounded-lg bg-black/40" />
            <div class="border-t border-slate-800/80 pt-2 flex items-start justify-between">
              <div>
                <p class="text-xs text-slate-400 uppercase font-semibold">Predicție Falsă (Păcălit):</p>
                <p class="text-lg font-bold text-rose-400 capitalize">{result.poisoned_label}</p>
                <p class="text-sm text-rose-300 font-medium">Confidență: {result.poisoned_confidence}%</p>
              </div>
              <a href={result.poisoned_image_base64} download="protected-asset.png"
                 class="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition">
                ⬇️ Salvează
              </a>
            </div>
          </div>
        </div>

        <!-- Butoane Test Scraper Bot (Toate cele 4 modele) -->
        <div class="border-t border-slate-800 pt-5 space-y-4">
          <div class="space-y-3">
            <div>
              <h3 class="text-sm font-bold text-white">Verificare Clasificatori AI (Simulare Scraper Bot - Port 8001):</h3>
              <p class="text-xs text-slate-400">Trimite imaginea otrăvită către oricare dintre cele 4 modele din evaluator pentru identificare oarbă:</p>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <button onclick={() => runBlindEvaluation('densenet')} disabled={isEvaluating}
                      class="py-2.5 px-3 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-semibold transition shadow">
                🔍 DenseNet-121 <span class="block text-[10px] font-normal opacity-80">(Black-Box)</span>
              </button>

              <button onclick={() => runBlindEvaluation('efficientnet')} disabled={isEvaluating}
                      class="py-2.5 px-3 bg-amber-600 hover:bg-amber-500 disabled:bg-slate-800 text-white rounded-xl text-xs font-semibold transition shadow">
                🔍 EfficientNet-B0 <span class="block text-[10px] font-normal opacity-80">(Black-Box)</span>
              </button>

              <button onclick={() => runBlindEvaluation('resnet50')} disabled={isEvaluating}
                      class="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 disabled:bg-slate-900 text-slate-200 rounded-xl text-xs font-semibold transition">
                🎯 ResNet-50 <span class="block text-[10px] font-normal text-slate-400">(White-Box)</span>
              </button>

              <button onclick={() => runBlindEvaluation('mobilenet')} disabled={isEvaluating}
                      class="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 disabled:bg-slate-900 text-slate-200 rounded-xl text-xs font-semibold transition">
                🎯 MobileNet-V3 <span class="block text-[10px] font-normal text-slate-400">(White-Box)</span>
              </button>
            </div>
          </div>

          {#if evaluationResult}
            <div class="bg-slate-950 p-4 rounded-xl border border-amber-500/30 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-amber-400 uppercase">Rezultat Scraper Bot (Top 5 Predicții):</span>
                <span class="text-xs font-mono px-2 py-0.5 bg-amber-500/10 text-amber-300 border border-amber-500/20 rounded">
                  Model testat: {evaluationResult.model_used.toUpperCase()}
                </span>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2 pt-1">
                {#each evaluationResult.top_predictions as pred, i}
                  <div class="p-2 rounded bg-slate-900 border {i === 0 ? 'border-amber-500/40 bg-amber-500/5' : 'border-slate-800'} text-center">
                    <span class="text-xs text-slate-500 block">#{i + 1}</span>
                    <span class="text-xs font-bold capitalize {i === 0 ? 'text-amber-400' : 'text-slate-300'}">{pred.class_name}</span>
                    <span class="text-xs text-slate-400 block">{pred.confidence}%</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      </section>
    {/if}
  </div>
</main>