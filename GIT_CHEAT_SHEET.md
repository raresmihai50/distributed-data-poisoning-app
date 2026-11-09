# 🚀 Ghid Rapid de Comenzi Git & GitHub

Un cheat sheet scurt și practic cu comenzile esențiale pentru un proiect individual / de facultate.

---

## 1. 🔄 Fluxul Zilnic (Cel mai des folosit)
După ce ai scris sau modificat cod și vrei să îl salvezi pe GitHub:

```bash
# 1. Vezi fișierele modificate (opțional, dar recomandat)
git status

# 2. Pregătește toate modificările pentru salvare
git add .

# 3. Creează un punct de salvare (commit) cu un mesaj descriptiv
git commit -m "Descriere scurta a modificarilor facute"

# 4. Trimite modificările pe GitHub
git push
```

---

## 2. 📥 Sincronizare (dacă lucrezi de pe două dispozitive)
Dacă ai modificat ceva direct de pe GitHub sau ai lucrat de pe alt laptop:

```bash
# Descarcă cele mai noi modificări de pe GitHub în proiectul tău local
git pull
```

---

## 3. 🔍 Istoric și Verificare
```bash
# Vezi istoricul scurt al ultimelor commit-uri
git log --oneline -n 10

# Vezi exact ce rânduri s-au modificat înainte de a da "git add"
git diff
```

---

## 4. ⏪ Butonul de Panică (Anulări & Modificări)

```bash
# Ai stricat un fișier și vrei să revii la ultima versiune salvată
git restore cale/catre/fisier.java

# Ai dat "git add ." din greșeală și vrei să scoți fișierele din pregătire
git restore --staged .

# Ai dat commit din greșeală, dar vrei să păstrezi codul scris
git reset --soft HEAD~1
```

---

## 5. 🌿 Branch-uri (Dacă vrei să testezi o idee fără să strici `main`)

```bash
# Creează și mută-te pe un branch nou de experiment
git checkout -b experiment-nou

# Întoarce-te pe branch-ul principal
git checkout main

# Integrează modificările din branch-ul de test în main
git merge experiment-nou

# Șterge branch-ul de test după ce ai terminat cu el
git branch -d experiment-nou
```

