# ANIMAtiZE Director Console — Audyt UI/UX i Strategia Modernizacji

**Data:** 2026-07-02
**Wersja:** 1.0
**Zakres:** `src/web/static/` (index.html, styles.css, app.js — 1413 linii), `src/web/app.py` (FastAPI)
**Rola:** Principal UI/UX Analyst / Product Designer

---

## 1. PODSUMOWANIE OCENY OBECNEGO STANU

### 1.1 Co działa dobrze (zachować)

| Obszar | Ocena | Uzasadnienie |
|--------|-------|--------------|
| **Spójna metafora kinowa** | ⭐⭐⭐⭐⭐ | "Roll Camera", "Take review", "Pull focus", film grain, sprockets — język domeny reżysera konsekwentnie przenika UI. To realny differentiator. |
| **Dostępność (a11y) — fundament** | ⭐⭐⭐⭐ | Skip-link, `aria-live`, `prefers-reduced-motion`, focus-ring, `sr-only`, toggle "Reduced motion" w ustawieniach. Ponad standard rynkowy. |
| **Design tokens (CSS custom properties)** | ⭐⭐⭐⭐ | Pełna parametryzacja: akcenty (amber/teal/crimson), grain, kontrast. Gotowe pod theming. |
| **Intent chips** | ⭐⭐⭐⭐ | Snippety promptów ("Amber push-in", "Orbit discipline") skracają time-to-first-value. |
| **Settings z wersjonowaniem i sync** | ⭐⭐⭐⭐ | Auto-save z historią wersji — rzadkość w narzędziach tej klasy. |

### 1.2 Zidentyfikowane problemy i pain points

| # | Problem | Dotkliwość | Dowód w kodzie |
|---|---------|------------|----------------|
| **P1** | **Brak progresu generacji** — po "Roll Camera" użytkownik widzi tylko skeleton + "Projector spinning...". Generacja wideo trwa 30–120s; brak ETA, brak etapów (analiza → kompilacja promptu → provider → render). | 🔴 Krytyczna | `app.js:863` — jeden statyczny tekst na cały czas oczekiwania |
| **P2** | **Fetch bez timeoutu i bez anulowania** — użytkownik nie może przerwać złej generacji; przy zawieszonym providerze UI wisi w nieskończoność. | 🔴 Krytyczna | `app.js:879` — brak `AbortController` |
| **P3** | **Monolityczny app.js (1413 linii)** — brak modułów, jeden globalny `state`, refs do 40+ elementów. Każda zmiana ryzykuje regresję; brak testów frontendu. | 🔴 Krytyczna (dla rozwoju) | `app.js:36-140` |
| **P4** | **Provider select bez kontekstu** — użytkownik wybiera "sora"/"veo" bez informacji o koszcie, czasie, możliwościach (audio? max duration?). Przy 18 modelach na rynku (patrz `STRATEGIC_ANALYSIS_REPORT.md`) to ślepy wybór. | 🟠 Wysoka | `index.html:151-153` — pusty `<select>` |
| **P5** | **Motion intensity 1–10 bez podglądu** — slider abstrakcyjny; użytkownik nie wie, co znaczy "6". Reżyser myśli w kategoriach "subtle drift" vs "dynamic push". | 🟠 Wysoka | `index.html:181-184` |
| **P6** | **Compare strip ukryty i pasywny** — `openCompareButton` disabled do momentu selekcji, ale nic nie komunikuje JAK wybrać warianty do porównania. | 🟠 Wysoka | `index.html:128-131` |
| **P7** | **Timeline bez miniatur** — lista tekstowa; reżyser pracuje wzrokowo. | 🟡 Średnia | `app.js` renderTimeline |
| **P8** | **Brak trybu jasnego** — "darkroom" jest jedynym trybem; praca przy dziennym świetle na laptopie = niski kontrast odbicia. | 🟡 Średnia | `styles.css:1-27` |
| **P9** | **Error state = czerwony alert z surowym message** — `error.message` z API prosto do UI; brak recovery path ("Retry", "Zmień provider", "Sprawdź klucz API"). | 🟠 Wysoka | `app.js:906-908` |
| **P10** | **Mobile: control-rack `order: -1`** — na <1120px panel kontrolek wskakuje NAD upload, odsuwając główną akcję poza fold. | 🟡 Średnia | `styles.css:1122-1124` |
| **P11** | **Google-only auth + guest** — brak magic link/passkey; guest nie wie, co traci (sync? historia?). | 🟡 Średnia | `index.html:22-49` |
| **P12** | **Font "35MM" countdown-reel** — dekoracja zajmuje 176px wysokości na ekranie logowania, nie komunikuje nic funkcjonalnego. | ⚪ Niska | `index.html:30-39` |

### 1.3 Mapa podróży użytkownika (Content Creator — pierwsza sesja)

```
WEJŚCIE          ONBOARDING        TWORZENIE           OCZEKIWANIE        REVIEW              WYJŚCIE
   │                 │                 │                   │                │                    │
Auth view ──▶ Guest/Google ──▶ Upload + Intent ──▶ "Roll Camera" ──▶ Take review ──▶ Favorite/Export
   │                 │                 │                   │                │
 [OK]           [P11: brak         [P4: ślepy wybór   [P1,P2: czarna   [P6: compare
              wyjaśnienia          providera]          dziura 30-120s]   niewidoczny]
              różnic]              [P5: abstrakcyjny
                                   slider]
```

**Krytyczny wniosek:** Najsłabszy moment podróży to **oczekiwanie na generację** — dokładnie tam, gdzie użytkownik jest najbardziej zaangażowany emocjonalnie ("czy mój shot wyjdzie?"). To jak kino bez zwiastuna przed filmem: pusta sala i cisza.

---

## 2. PROPOZYCJE MODERNIZACJI UI

### 2.1 "Dailies Room" — ekran oczekiwania jako feature (rozwiązuje P1)

Zamiast skeletonów — **pipeline visualizer** w estetyce taśmy filmowej:

```
┌─────────────────────────────────────────────────────────────┐
│  ● SCENE ANALYSIS   ● PROMPT COMPILE   ◐ RENDERING   ○ QC   │
│  ────────────────────────────────────▶                      │
│                                                             │
│  ┌─────────┐   "Detected: low-key lighting, single subject, │
│  │ source  │    shallow DoF. Compiling dolly-in with        │
│  │ thumb   │    parallax preservation..."                   │
│  └─────────┘                                                │
│                                                             │
│  Provider: Kling 3.0  •  Est. 45–70s  •  [ CUT (cancel) ]   │
└─────────────────────────────────────────────────────────────┘
```

- Etapy pipeline'u mapują się 1:1 na realne moduły backendu (`scene_analyzer` → `prompt_expander` → adapter → `quality_assurance`).
- Streaming statusów przez **SSE/WebSocket** (backend FastAPI już to umożliwia).
- Przycisk **"CUT"** = anulowanie (`AbortController` + endpoint cancel).
- Wyświetlanie skompilowanego promptu podczas oczekiwania = edukacja użytkownika + transparencja ("dlaczego wyszło tak, a nie inaczej").

### 2.2 Provider picker jako "Camera Cards" (rozwiązuje P4)

Zamiast `<select>` — karty w stylu specyfikacji kamer:

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ KLING 3.0    │ │ VEO 3.1      │ │ SEEDANCE 2.0 │
│ ★ ELO #1     │ │ 4K • Audio   │ │ 12-ref multi │
│ 15s • 4K     │ │ 8s max       │ │ 15s • 2K     │
│ ~$0.15/s     │ │ ~$0.35/s     │ │ ~$0.14/s     │
│ ⏱ ~60s       │ │ ⏱ ~40s       │ │ ⏱ ~50s       │
└──────────────┘ └──────────────┘ └──────────────┘
```

- Dane zasilane z `ModelCapabilities` (już istnieje w `src/adapters/contracts.py`!) — zero nowego backendu, tylko ekspozycja.
- Badge "recommended for this intent" — prosty scoring intencji vs capabilities (np. intent zawiera "audio" → wyróżnij Veo/Kling/Seedance).
- Deprecation warnings inline: "⚠️ Sora — EOL Sep 2026" (dane z raportu strategicznego).

### 2.3 Motion intensity → "Movement Vocabulary" (rozwiązuje P5)

Slider 1–10 zastąpić segmentowaną skalą z językiem filmowym i mikro-animacją podglądu:

```
LOCKED ── DRIFT ── GLIDE ── TRACK ── PUSH ── KINETIC
  ○────────○────────●────────○────────○────────○
        "Steadicam glide — smooth, intentional"
        [pole 3×2 z animowanym wektorem ruchu na miniaturze]
```

- Każdy poziom = predefiniowany zestaw parametrów w `film_grammar.py` (moduł już istnieje).
- Hover/focus = 1-sekundowa CSS-animacja wektora ruchu na załadowanej miniaturze.
- Analogia: to jak pierścień ostrości z oznaczeniami odległości zamiast potencjometru bez skali.

### 2.4 Compare jako "Light Table" (rozwiązuje P6)

- Po ukończeniu runu z ≥2 wariantami — **auto-otwarcie** trybu porównania (z opcją wyłączenia w Settings).
- Synchroniczne odtwarzanie wariantów (jeden scrubber steruje wszystkimi).
- Klawiszologia recenzenta: `1/2/3` = wybór wariantu, `F` = favorite, `Space` = play/pause — jak w Avid/Premiere.
- Overlay diff: heatmapa różnic klatek między wariantami (istniejący `consistency_engine` liczy to po stronie backendu).

### 2.5 Timeline → "Contact Sheet" (rozwiązuje P7)

Pozioma taśma miniatur zamiast listy tekstowej:

```
┌──┬──────────────────────────────────────────────┐
│▐▌│ [thumb] [thumb] [thumb] [thumb] [thumb]  ►   │
│▐▌│  Take 5  Take 4  Take 3  Take 2  Take 1      │
└──┴──────────────────────────────────────────────┘
```

- Sprocket holes jako ramka — wzmacnia istniejącą metaforę.
- Drag & drop miniatur do drop-zone = rerun z tej klatki.

### 2.6 Tryb "Daylight" (rozwiązuje P8)

- Drugi motyw o wysokiej jasności: `--bg-0: #faf7f0` (ciepła biel papieru scenopisu), akcent bez zmian.
- Przełącznik w headerze (ikona przysłony), nie tylko w Settings.
- `prefers-color-scheme` jako default przy pierwszej wizycie.
- Grain w daylight = 0 (domyślnie) — grain na jasnym tle wygląda jak brud.

### 2.7 Error states → "Recovery Cards" (rozwiązuje P9)

Mapowanie `ErrorCode` (już istnieje w `contracts.py`!) na akcje:

| ErrorCode | Komunikat | CTA |
|-----------|-----------|-----|
| `RATE_LIMIT_EXCEEDED` | "Provider przeciążony" | [Retry za 30s] [Zmień na Veo] |
| `AUTHENTICATION_FAILED` | "Klucz API odrzucony" | [Otwórz Settings → API] |
| `INSUFFICIENT_CREDITS` | "Brak kredytów u providera" | [Doładuj ↗] [Zmień provider] |
| `CONTENT_POLICY_VIOLATION` | "Prompt odrzucony przez filtr" | [Pokaż problematyczny fragment] [Edytuj intent] |

Zasada: **każdy błąd ma następny krok**. Dead-end = porzucenie sesji.

### 2.8 Mobile: przywrócić hierarchię (rozwiązuje P10)

- Usunąć `order: -1` z `.control-rack`; zamiast tego **sticky bottom sheet** z uchwytem (wzorzec znany z map/muzyki).
- Upload + intent zawsze above the fold; kontrolki wysuwane gestem.

---

## 3. REKOMENDACJE UX (uzasadnienia w teorii użyteczności)

| # | Rekomendacja | Zasada / Uzasadnienie |
|---|--------------|----------------------|
| U1 | **Pipeline visualizer podczas generacji** | *Nielsen #1: Visibility of system status.* Postrzegany czas oczekiwania maleje ~36% gdy pokazujemy postęp etapowy (badania Nielsen Norman Group nt. progress indicators). |
| U2 | **Anulowanie zawsze dostępne** | *Nielsen #3: User control and freedom.* Koszt psychiczny kliknięcia "generate" spada, gdy wiadomo, że można przerwać → więcej eksperymentów → więcej wartości z produktu. |
| U3 | **Camera Cards zamiast select** | *Hick's Law + informed choice.* Decyzja z widocznymi trade-offami (koszt/czas/jakość) jest szybsza niż decyzja wymagająca wiedzy zewnętrznej. |
| U4 | **Movement Vocabulary zamiast liczb** | *Match between system and real world (Nielsen #2).* Reżyser mówi "glide", nie "6/10". Redukcja cognitive load przez język domeny. |
| U5 | **Auto-open compare + klawiszologia** | *Flow state.* Recenzja wariantów to pętla core loop; każde zbędne kliknięcie w pętli × liczba iteracji = zmierzalna frustracja. Analogia: montażysta nie klika menu, żeby przejść do następnego ujęcia. |
| U6 | **Recovery Cards** | *Error prevention → error recovery (Nielsen #9).* Błąd z akcją naprawczą to moment budowania zaufania, nie utraty. |
| U7 | **Onboarding: pierwszy run na przykładowym obrazie** | *Time-to-value.* Przycisk "Try with sample frame" na pustym drop-zone — użytkownik widzi pełną pętlę wartości bez własnego assetu. |
| U8 | **Cost preview przed generacją** | *No surprises.* "3 warianty × 6s × Kling 3.0 ≈ $2.70" pod przyciskiem Roll Camera. Zaufanie = retencja przy narzędziach pay-per-use. |
| U9 | **Guest→Account upsell kontekstowy** | Zamiast bariery przy wejściu — moment konwersji przy pierwszej wartości: "Zapisz ten take na zawsze → załóż konto" po pierwszym favorite. |

---

## 4. SUGESTIE TECHNOLOGICZNE

| Technologia | Zastosowanie | Uzasadnienie | Ryzyko |
|-------------|--------------|--------------|--------|
| **Lit (Web Components)** | Dekompozycja app.js na `<take-card>`, `<camera-picker>`, `<pipeline-status>` | Zero build-step (opcjonalny), 5KB, przyrostowa adopcja — komponenty wpinane w istniejący HTML bez przepisywania. Uczciwsza ścieżka niż skok w React dla zespołu backend-first. | Niskie |
| **SSE (Server-Sent Events)** | Streaming etapów pipeline'u | Natywnie w FastAPI (`StreamingResponse`), prostsze niż WebSocket dla ruchu jednokierunkowego, auto-reconnect w standardzie. | Niskie |
| **@starting-style + View Transitions API** | Płynne przejścia widoków Create↔Library, morph miniatur | Natywny CSS/JS 2025+, zero bibliotek; degraduje się gracefully. Wzmacnia "cinematic feel" bez kosztów JS. | Niskie |
| **Zod-like walidacja (Valibot)** | Kontrakty API po stronie klienta | 1KB; łapie rozjazdy backend/frontend zanim zobaczy je użytkownik (dziś: surowy `payload.detail` w UI). | Niskie |
| **Playwright component testing** | Testy pętli create→generate→review | Chromium już jest w środowisku projektu; pierwsze testy E2E dla frontendu, który dziś ma zero pokrycia. | Niskie |
| **LCM/SDXL-Turbo preview** (backlog: "Real-time preview") | 1-sekundowy podgląd ruchu przed pełną generacją | Zamyka JTBD "Animator: <2s preview" z raportu strategicznego; radykalnie tnie koszt iteracji (tanie preview → droga finalna generacja tylko dla zwycięzcy). | Średnie (GPU) |
| **transformers.js (opcjonalnie)** | Lokalny scoring intencji → sugestia providera | Prywatność (intent nie opuszcza przeglądarki dla samej rekomendacji), zero latencji API. | Średnie |

**Świadomie odradzam:** pełny framework SPA (React/Vue/Svelte) w tym momencie. Aplikacja ma 4 widoki i jeden core loop; koszt migracji > zysk. Lit + moduły ES = 80% korzyści przy 20% kosztu. Rewizja decyzji, gdy dojdą widoki multi-shot/storyboard.

---

## 5. ROADMAPA WDROŻENIA

### Faza 1 — Quick Wins (1–2 tygodnie)

| Zadanie | Rozwiązuje | Effort |
|---------|-----------|--------|
| `AbortController` + przycisk CUT | P2 | S |
| Recovery Cards (mapowanie ErrorCode → CTA) | P9 | S |
| Cost preview pod Roll Camera | U8 | S |
| Provider select: dodać metadane (koszt/czas/audio) jako `<option>` text + tooltip | P4 (interim) | S |
| Fix mobile order kontrolek → bottom sheet (etap 1: usunąć `order:-1`) | P10 | S |
| "Try with sample frame" na pustym drop-zone | U7 | S |

### Faza 2 — Core Experience (3–6 tygodni)

| Zadanie | Rozwiązuje | Effort |
|---------|-----------|--------|
| SSE pipeline streaming + Dailies Room UI | P1, U1 | M |
| Camera Cards (pełny picker z ModelCapabilities) | P4 | M |
| Movement Vocabulary (segmented control + film_grammar) | P5 | M |
| Light Table compare (auto-open, sync playback, klawisze) | P6, U5 | M |
| Dekompozycja app.js → moduły ES + Lit dla 3 komponentów | P3 | M |
| Playwright E2E dla core loop | P3 | M |

### Faza 3 — Strategiczne (2–3 miesiące)

| Zadanie | Rozwiązuje | Effort |
|---------|-----------|--------|
| Contact Sheet timeline z drag&drop rerun | P7 | M |
| Tryb Daylight + `prefers-color-scheme` | P8 | M |
| LCM real-time preview (wymaga backendu GPU) | JTBD Animator | L |
| Onboarding flow + kontekstowy upsell guest→account | P11, U9 | M |
| Storyboard/multi-shot view (przygotowanie pod Consistency Engine UI) | roadmap produktu | L |

**Kolejność uzasadniona:** Faza 1 usuwa punkty krwawienia (utrata użytkownika w czarnej dziurze generacji i na błędach). Faza 2 buduje differentiator (Dailies Room + Camera Cards to rzeczy, których nie ma Runway ani Pika). Faza 3 skaluje na nowe JTBD.

---

## 6. METRYKI SUKCESU

| Metryka | Baseline (est.) | Cel po Fazie 2 |
|---------|-----------------|----------------|
| Time-to-first-generation (nowy user) | ~4 min | < 90 s |
| Odsetek anulowanych sesji podczas oczekiwania | nieznany (brak trackingu!) | < 8% |
| Odsetek błędów zakończonych retry (vs porzuceniem) | ~0% (brak CTA) | > 50% |
| Liczba iteracji (runs) na sesję | nieznana | +40% |
| Użycie compare przy runach ≥2 wariantów | niskie (ukryte) | > 70% |

**Uwaga:** przed Fazą 1 dodać minimalną telemetrię zdarzeń (privacy-first, bez zewnętrznych trackerów — endpoint `/api/events` już w duchu istniejącej architektury).

---

*Raport przygotowany na podstawie pełnej analizy kodu frontendu i backendu web. Odwołania do plików: `src/web/static/index.html`, `src/web/static/styles.css`, `src/web/static/app.js`, `src/web/app.py`, `src/adapters/contracts.py`, `src/wedge_features/film_grammar.py`.*
