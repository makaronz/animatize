# ANIMAtiZE - Raport Analizy Strategicznej

**Data:** 2026-02-07 | **Aktualizacja:** 2026-06-25
**Wersja:** 1.1
**Autor:** Principal R&D Analyst / Product Strategist

> ⚠️ **UWAGA:** Wersja 1.1 zawiera krytyczne aktualizacje dotyczące wycofania Sora i Runway Gen-3 Alpha.

---

## 0. BRAKUJĄCE WEJŚCIA

| Plik | Status | Uwagi |
|------|--------|-------|
| MOVEMENT_PREDICTION_GUIDE.md | ✓ Dostępny | W repozytorium GitHub |
| PROJECT_DOCUMENTATION.md | ✓ Dostępny | Kompletna dokumentacja |
| ai-video-prompting-guide_PL-EN.md | ✓ Dostępny | Dwujęzyczny przewodnik |
| FILM_GRAMMAR_NOTES.md | ✗ Brak | Zastąpiony przez `film_grammar.py` |
| API_REFERENCE.md | ✗ Brak | Częściowo w `docs/api/` |

---

## 1. ANALIZA CODEBASE

### 1.1 Inwentarz Modułów (408 plików)

| Moduł | Rola | Wejścia/Wyjścia | Format | Zależności | API/Model |
|-------|------|-----------------|--------|------------|-----------|
| `src/analyzers/movement_predictor.py` | Przewidywanie ruchu kinematycznego | Obraz → MovementPrediction | JSON | OpenCV, NumPy, PIL | - |
| `src/analyzers/scene_analyzer.py` | Analiza sceny CV | Obraz → SceneAnalysis | JSON | OpenCV, NumPy | - |
| `src/analyzers/motion_detector.py` | Wykrywanie ruchu | Obraz → MotionData | JSON | OpenCV | - |
| `src/analyzers/video_prompt_analyzer.py` | Analiza promptów wideo | Prompt → Analysis | JSON | - | - |
| `src/adapters/sora_adapter.py` | Adapter OpenAI Sora | UnifiedRequest → Video | MP4 | requests | OpenAI API |
| `src/adapters/veo_adapter.py` | Adapter Google Veo | UnifiedRequest → Video | MP4 | requests | Vertex AI |
| `src/adapters/runway_adapter.py` | Adapter Runway Gen-3 | UnifiedRequest → Video | MP4 | requests | Runway API |
| `src/adapters/flux_adapter.py` | Adapter Flux | UnifiedRequest → Image | PNG | requests | Flux API |
| `src/adapters/pika_adapter.py` | Adapter Pika | UnifiedRequest → Video | MP4 | requests | Pika API |
| `src/wedge_features/consistency_engine.py` | Silnik spójności cross-shot | Frames → ConsistencyReport | JSON | OpenCV, NumPy | - |
| `src/wedge_features/film_grammar.py` | Reguły gramatyki filmowej | Scene → CameraMovement | JSON | - | - |
| `src/wedge_features/evaluation_harness.py` | System ewaluacji | Results → Metrics | JSON | - | - |
| `src/wedge_features/identity_preservation.py` | Zachowanie tożsamości postaci | Character → Embedding | Vector | NumPy | - |
| `src/wedge_features/temporal_control.py` | Kontrola temporalna | Sequence → Timeline | JSON | - | - |
| `src/core/prompt_expander.py` | Rozszerzanie promptów | Prompt → ExpandedPrompt | Text | - | LLM |
| `src/core/video_pipeline.py` | Pipeline generacji wideo | Request → Video | MP4 | Adapters | Multi |
| `src/core/director_ux.py` | Interfejs reżysera | Input → Commands | JSON | - | - |
| `src/core/product_backlog.py` | Zarządzanie backlogiem | - → BacklogItems | JSON/MD | - | - |
| `src/evaluation/regression_system.py` | System regresji | Tests → Report | JSON | pytest | - |
| `src/evaluation/test_scenarios.py` | Scenariusze testowe | - → TestCases | JSON | - | - |

### 1.2 Architektura - Diagram Tekstowy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ANIMAtiZE FRAMEWORK                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐  │
│  │   IMAGE     │────▶│  SCENE ANALYZER  │────▶│   MOVEMENT PREDICTOR    │  │
│  │   INPUT     │     │  (OpenCV/CV2)    │     │   (47+ Cinematic Rules) │  │
│  └─────────────┘     └──────────────────┘     └───────────┬─────────────┘  │
│                                                           │                 │
│                      ┌────────────────────────────────────▼───────────────┐ │
│                      │              CONSISTENCY ENGINE                    │ │
│                      │  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐ │ │
│                      │  │ Character   │ │   Style     │ │    World     │ │ │
│                      │  │ Reference   │ │   Anchor    │ │  Reference   │ │ │
│                      │  └─────────────┘ └─────────────┘ └──────────────┘ │ │
│                      └────────────────────────────────────┬───────────────┘ │
│                                                           │                 │
│  ┌────────────────────────────────────────────────────────▼───────────────┐ │
│  │                        PROMPT COMPILER                                  │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │   │Film Grammar │  │ Prompt      │  │ Temporal    │  │ Shot List   │  │ │
│  │   │ Rules       │  │ Expander    │  │ Control     │  │ Compiler    │  │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └────────────────────────────────────────────────────────┬───────────────┘ │
│                                                           │                 │
│  ┌────────────────────────────────────────────────────────▼───────────────┐ │
│  │                         MODEL ADAPTERS                                  │ │
│  │   ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐   │ │
│  │   │ SORA  │  │  VEO  │  │RUNWAY │  │ KLING │  │ LUMA  │  │  WAN  │   │ │
│  │   │  ⛔   │  │ 3.1   │  │ 4.5   │  │  3.0  │  │ Ray3  │  │ 2.7   │   │ │
│  │   └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘   │ │
│  └────────────────────────────────────────────────────────┬───────────────┘ │
│                                                           │                 │
│  ┌────────────────────────────────────────────────────────▼───────────────┐ │
│  │                      EVALUATION HARNESS                                 │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │   │ Regression  │  │  Quality    │  │  Golden     │  │ Benchmark   │  │ │
│  │   │ System      │  │ Assurance   │  │  Prompts    │  │ Suite       │  │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  OUTPUT: Cinematic Video Prompts + Consistency Validation                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Kontrakty Między Modułami

```yaml
# UnifiedRequest Contract (src/adapters/contracts.py)
UnifiedRequest:
  schema_version: str          # "1.0"
  request_id: str              # UUID
  provider: str                # "sora" | "veo" | "runway" | "kling" | "luma" | "wan"
  model: str                   # Model specific identifier
  prompt: str                  # Natural language prompt
  parameters:
    size: str                  # "1280x720" | "1920x1080"
    duration: int              # 4 | 8 | 12 seconds
    quality: str               # "standard" | "high"
    style: Optional[str]       # Style reference
    seed: Optional[int]        # Reproducibility

# UnifiedResponse Contract
UnifiedResponse:
  schema_version: str
  request_id: str
  provider: str
  model: str
  status: str                  # "success" | "failed" | "pending"
  result:
    video_url: Optional[str]
    revised_prompt: Optional[str]
  error: Optional[ErrorDetails]
  metadata: Dict

# ConsistencyViolation Contract
ConsistencyViolation:
  violation_type: ConsistencyType
  severity: float              # 0.0 - 1.0
  description: str
  frame_a: str
  frame_b: str
  suggested_fix: str
  confidence: float
  details: Dict
```

### 1.4 Identyfikacja Wąskich Gardeł

| Obszar | Problem | Wpływ | Priorytet |
|--------|---------|-------|-----------|
| **Latencja** | Sekwencyjna analiza obrazu (2.3s/obraz) | Wolne multi-shot | Wysoki |
| **Determinizm** | Brak seed w niektórych adapterach | Niepowtarzalność | Średni |
| **Testy** | Brak testów integracyjnych dla adapterów | Regresje | Wysoki |
| **Cache** | Brak cache dla embeddings | Powtórne obliczenia | Średni |
| **Metryki** | Brak Prometheus/OpenTelemetry | Brak observability | Średni |
| **Multi-scene** | Brak pipeline multi-shot | Ograniczone narracje | Wysoki |
| **Temporal** | Brak synchronizacji audio | Brak lip-sync | Średni |
| **🔴 Sora EOL** | API wygasa 24 Sep 2026 | Utrata providera | **KRYTYCZNY** |
| **🟡 Runway EOL** | Gen-3 Alpha kończy 30 Jul 2026 | Migracja wymagana | Wysoki |

### 1.4.1 🚨 WYMAGANE AKCJE NA ADAPTERACH (Czerwiec 2026)

| Adapter | Obecny | Docelowy | Deadline | Priorytet | Effort |
|---------|--------|----------|----------|-----------|--------|
| `sora_adapter.py` | Sora 2 | **USUNĄĆ** lub zastąpić | 24 Sep 2026 | 🔴 P0 | S |
| `runway_adapter.py` | Gen-3 Alpha | Gen-4.5 | 30 Jul 2026 | 🟡 P1 | M |
| `kling_adapter.py` | Kling 2.6 | Kling 3.0 | ASAP | 🟢 P2 | M |
| `wan_adapter.py` | Wan 2.2 | Wan 2.7 | Q3 2026 | 🟢 P2 | S |
| `luma_adapter.py` | Ray3 | Ray3.14 | Q3 2026 | 🟢 P3 | S |
| `veo_adapter.py` | Veo 3.1 | + Veo 3.1 Lite | Q3 2026 | 🟢 P3 | S |
| `seedance_adapter.py` | **BRAK** | Seedance 2.0 | Q3 2026 | 🟢 P2 | M |
| `happyhorse_adapter.py` | **BRAK** | HappyHorse 1.1 | Q3 2026 | 🟢 P2 | M |

**Legenda:** S = Small (1-2 dni), M = Medium (3-5 dni), L = Large (1-2 tygodnie)

### 📊 Nowe Modele - Szczegółowa Analiza

#### Seedance 2.0 (ByteDance) - Luty 2026
| Cecha | Wartość |
|-------|---------|
| **Architektura** | Dual-Branch Diffusion Transformer |
| **Wejścia** | Text, Image, Video, Audio (do 12 assetów jednocześnie) |
| **Rozdzielczość** | do 2K |
| **Czas trwania** | 4-15s |
| **Proporcje** | 16:9, 9:16, 1:1 |
| **Audio** | ✅ Natywna synchronizacja audio-video |
| **Multi-shot** | ✅ Spójne postacie i logika wizualna między ujęciami |
| **API** | BytePlus (intl), Volcengine (China), fal.ai |
| **Cena** | ~1 CNY/s (~$0.14/s) lub ~$0.05/5s @720p via 3rd party |

#### HappyHorse 1.1 (Alibaba) - Kwiecień 2026
| Cecha | Wartość |
|-------|---------|
| **Architektura** | 15B Unified Transformer (40 warstw) |
| **Distillation** | DMD-2, 8 kroków, bez CFG |
| **Czas generacji** | ~10s (jeden z najszybszych) |
| **Rozdzielczość** | 720p / 1080p |
| **Czas trwania** | 3-15s |
| **Proporcje** | 16:9, 9:16, 1:1, 4:3, 3:4, 4:5, 5:4, 9:21, 21:9 |
| **Audio** | ✅ Natywna synchronizacja |
| **Lip-sync** | ✅ 7 języków (EN, ZH, JA, KO, DE, FR, Cantonese) |
| **Reference Images** | do 9 obrazów |
| **Open Source** | ✅ Apache 2.0 |
| **API** | fal.ai, Alibaba Cloud, happyhorse.com |
| **Cena** | $0.14/s @720p, $0.18/s @1080p |

### 1.5 JTBD (Jobs To Be Done)

| Użytkownik | Chce | Aby | Metryka Sukcesu | Status |
|------------|------|-----|-----------------|--------|
| Content Creator | Przekształcić statyczny obraz w wideo | Tworzyć dynamiczny content | <30s do pierwszego wyniku | ✓ Pokryty |
| Filmowiec | Wygenerować cinematic prompts | Pre-wizualizować ujęcia | 90% zgodność z intencją | ~ Częściowo |
| Marketer | Batch processing wielu obrazów | Skalować produkcję | 100+ obrazów/godzinę | ~ Częściowo |
| Reżyser | Kontrolować ruch kamery | Osiągnąć precyzyjną wizję | 95% kontrola nad ruchem | ~ Częściowo |
| Studio | Multi-shot consistency | Utrzymać spójność postaci | >95% identity match | ✓ Pokryty |
| Developer | API do integracji | Zbudować własne narzędzia | <500ms API latency | ✓ Pokryty |
| Enterprise | Multi-tenant isolation | Bezpieczna separacja | 100% isolation | × Brak |
| Animator | Real-time preview | Szybka iteracja | <2s preview | × Brak |

### 1.6 Maturity Scoring Modułów

| Moduł | Poprawność | Rozszerzalność | Obserwowalność | Testowalność | Wydajność | Bezpieczeństwo | Średnia | Refactor |
|-------|------------|----------------|----------------|--------------|-----------|----------------|---------|----------|
| movement_predictor.py | 4 | 4 | 3 | 4 | 3 | 4 | 3.7 | Later |
| scene_analyzer.py | 4 | 4 | 3 | 4 | 3 | 4 | 3.7 | Later |
| consistency_engine.py | 5 | 5 | 4 | 4 | 3 | 4 | 4.2 | - |
| sora_adapter.py | 4 | 4 | 3 | 3 | 4 | 4 | 3.7 | Later |
| veo_adapter.py | 4 | 4 | 3 | 3 | 4 | 4 | 3.7 | Later |
| prompt_expander.py | 3 | 4 | 2 | 3 | 4 | 3 | 3.2 | **Must-Do** |
| video_pipeline.py | 3 | 3 | 2 | 3 | 3 | 3 | 2.8 | **Must-Do** |
| film_grammar.py | 4 | 4 | 3 | 4 | 4 | 4 | 3.8 | Later |

**So what?** Architektura jest solidna, ale wymaga refaktoryzacji `prompt_expander.py` i `video_pipeline.py` przed skalowaniem. Consistency Engine jest najdojrzalszym modułem - to kluczowy asset.

---

## 2. BADANIA: STAN KONTROLOWANEGO GENEROWANIA WIDEO

### 2.1 Mapa Modeli (A)

| Model | Firma | Max Duration | Max Resolution | Kontrola Kamery | I2V | Audio | API | Data | Status |
|-------|-------|--------------|----------------|-----------------|-----|-------|-----|------|--------|
| **Sora 2** | OpenAI | 25s | 1920x1080 | Prompt-based | ✓ | ✓ | ⚠️ | Sep 2025 | **⛔ DEPRECATED** |
| **Veo 3.1** | Google | 8s | 4K | JSON Schema | ✓ | ✓ | ✓ | Oct 2025 | ✅ Aktywny |
| **Veo 3.1 Lite** | Google | 8s | 1080p | JSON Schema | ✓ | ✓ | ✓ | Apr 2026 | ✅ Aktywny |
| **Runway Gen-4.5** | Runway | 10s+ | 4K | Advanced Controls | ✓ | × | ✓ | Dec 2025 | ✅ Aktywny |
| **Runway Gen-3 Alpha** | Runway | 10s | 1080p | Camera Controls | ✓ | × | ⚠️ | Nov 2024 | **⚠️ EOL Jul 2026** |
| **Kling 3.0** | Kuaishou | 15s | 4K | Motion Brush | ✓ | ✓ | ✓ | Feb 2026 | ✅ Aktywny |
| **Kling 2.6** | Kuaishou | 10s | 1080p | Motion Brush | ✓ | ✓ | ✓ | Dec 2025 | ✅ Aktywny |
| **Luma Ray 3.2** | Luma AI | - | 1080p | Multi-Keyframe | ✓ | × | ✓ | Mar 2026 | ✅ Aktywny |
| **Luma Ray3.14** | Luma AI | - | Native 1080p | Full Control | ✓ | × | ✓ | 2026 | ✅ Aktywny |
| **Wan 2.7** | Alibaba | - | 1080p | First/Last Frame | ✓ | × | OSS | 2026 | ✅ Aktywny |
| **Pika 2.5** | Pika Labs | 25s | 1080p | Pikaframes | ✓ | × | ✓ | Early 2026 | ✅ Aktywny |
| **Seedance 2.0** | ByteDance | 15s | 2K | 12-Asset Multimodal | ✓ | ✓ | ✓ | Feb 2026 | ✅ **NOWY** |
| **HappyHorse 1.1** | Alibaba | 15s | 1080p | 9-Image Reference | ✓ | ✓ | ✓/OSS | Apr 2026 | ✅ **NOWY** |

### ⚠️ KRYTYCZNE ALERTY (Aktualizacja Czerwiec 2026)

| Alert | Model | Data | Wpływ | Akcja |
|-------|-------|------|-------|-------|
| **🔴 WYCOFANY** | Sora App | 26 Apr 2026 | Aplikacja zamknięta | Migracja na Veo/Kling |
| **🔴 EOL** | Sora API | 24 Sep 2026 | API zostanie wyłączone | Usunąć `sora_adapter.py` |
| **🟡 EOL** | Runway Gen-3 Alpha | 30 Jul 2026 | Model przestanie działać | Aktualizacja do Gen-4.5 |
| **🟢 NOWY** | Kling 3.0 | 4 Feb 2026 | Lider ELO (1243) | Dodać `kling_v3_adapter.py` |
| **🟢 NOWY** | Luma Ray3 Modify | Mar 2026 | Character performance transfer | Nowa capability |
| **🟢 NOWY** | Veo 3.1 Lite | Apr 2026 | 50% tańszy | Dodać tier pricing |
| **🟢 NOWY** | Seedance 2.0 | Feb 2026 | 12-asset multimodal, native audio | Dodać `seedance_adapter.py` |
| **🟢 NOWY** | HappyHorse 1.1 | Apr 2026 | #1 ELO open-source, 7-lang lip-sync | Dodać `happyhorse_adapter.py` |

**Źródła:**
- [OpenAI Sora 2](https://openai.com/index/sora-2/) - Sep 2025
- [Sora Shutdown Notice](https://aipure.ai/articles/openai-shuts-down-sora-app-what-the-future-holds-for-ai-video-generation-in-2026) - Apr 2026
- [Google Veo 3.1](https://deepmind.google/models/veo/) - Oct 2025
- [Veo 3.1 Lite](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-lite/) - Apr 2026
- [Runway Gen-3 Deprecation](https://help.runwayml.com/hc/en-us/articles/30266515017875) - 2026
- [Kling 3.0 Launch](https://ir.kuaishou.com/news-releases/news-release-details/kling-ai-launches-30-model-ushering-era-where-everyone-can-be/) - Feb 2026
- [Luma Ray3](https://lumalabs.ai/ray) - Mar 2026
- [Wan 2.7](https://fal.ai/wan-2.7) - 2026
- [Pika 2.5](https://pikaslabs.com/pika-2.5/) - 2026
- [Seedance 2.0](https://www.mindstudio.ai/blog/what-is-seedance-2-bytedance-ai-video-model) - Feb 2026
- [Seedance 2.0 API](https://fal.ai/seedance-2.0) - Apr 2026
- [HappyHorse 1.1](https://www.explainx.ai/blog/happyhorse-1-1-alibaba-video-generation-model-2026) - Apr 2026
- [HappyHorse API](https://fal.ai/happyhorse-1.0) - 2026

### 2.2 Prompt Engineering (B)

**Uniwersalna Struktura Promptu:**
```
[SUBJECT DESCRIPTION] [ACTION/MOVEMENT] [ENVIRONMENT]
[LIGHTING] [ATMOSPHERE] [CAMERA MOVEMENT] [VISUAL STYLE]
```

**Kluczowe Wzorce:**

| Wzorzec | Opis | Zastosowanie |
|---------|------|--------------|
| **CAMS** | Character-Action-Movement-Setting | Podstawowe T2V |
| **CINE** | Camera-Intent-Narrative-Emotion | Cinematyczny styl |
| **SPARK** | Subject-Purpose-Action-Result-Key | Produktowe |
| **STORY** | Narrative structure | Multi-shot |

**Model-Specific Strategies (Zaktualizowane Czerwiec 2026):**
- **Sora 2**: ⛔ WYCOFANY - Migruj na Veo 3.1 lub Kling 3.0
- **Veo 3.1**: JSON schemas, structured data, reference images, native audio
- **Veo 3.1 Lite**: Ekonomiczna alternatywa (<50% kosztów)
- **Runway Gen-4.5**: Advanced controls, 4K native, Act-One performance
- **Kling 3.0**: 4K/60fps, 15s, unified multimodal, timeline scripts, audio sync
- **Luma Ray3**: Multi-keyframe control (16 keyframes), Ray3 Modify dla character transfer
- **Wan 2.7**: First/Last frame, subject referencing, open weights
- **Seedance 2.0**: 12-asset multimodal input, Dual-Branch Diffusion Transformer, native audio-video sync, multi-shot storytelling
- **HappyHorse 1.1**: 9-image reference, 7-language lip-sync, 15B unified transformer, DMD-2 distillation (8 steps), ~10s/gen

**Źródła:**
- [Venice.ai Video Prompt Guide](https://venice.ai/blog/the-complete-guide-to-ai-video-prompt-engineering) - 2024
- [Sora 2 Prompting Guide](https://cookbook.openai.com/examples/sora/sora2_prompting_guide) - Dec 2024

**So what?** ANIMAtiZE potrzebuje adaptera promptów per-model, nie uniwersalnego promptu. Obecna architektura adapterów jest właściwym podejściem.

### 2.3 Mechanizmy Kontroli (C)

| Mechanizm | Opis | Modele Wspierające | Precyzja |
|-----------|------|-------------------|----------|
| **Depth Control** | Mapa głębi dla 3D | ControlNet, Wan VACE | Wysoka |
| **Pose Control** | OpenPose skeleton | ControlNet, Kling | Wysoka |
| **Edge Control** | Canny/HED edges | ControlNet, Wan | Średnia |
| **Reference Images** | Style/character ref | Sora, Veo, Luma | Średnia |
| **Motion Brush** | Region-specific motion | Kling, Runway Gen-2 | Wysoka |
| **Camera Paths** | 3D camera trajectory | Luma Ray2, Runway | Średnia |
| **First/Last Frame** | Keyframe conditioning | Kling, Wan, Veo | Wysoka |
| **Temporal Consistency** | Frame coherence | Wan, Sora | Wysoka |

**So what?** ANIMAtiZE musi wspierać First/Last Frame conditioning i Motion Brush jako minimum viable control mechanisms.

### 2.4 Ewaluacja i Benchmarki (D)

| Benchmark | Zakres | Metryki | Lider (Czerwiec 2026) |
|-----------|--------|---------|----------------------|
| **VBench / ELO** | Temporal, aesthetic, motion | 16 dimensions + ELO | **Kling 3.0 (ELO 1243)** |
| **T2V-CompBench** | Compositional | Multi-object, attributes | - |
| **CLIP Score** | Prompt adherence | Cosine similarity | Korelacja 0.8+ z human |
| **DreamSim** | Perceptual similarity | Human correlation | r>0.75 |
| **ImageReward** | Human preference | Acceptance rate | 40% reduction in rejects |

**Źródła:**
- [VBench Leaderboard](https://github.com/Vchitect/VBench) - 2024
- [T2V-CompBench](https://arxiv.org/html/2404.05892) - 2024

**So what?** ANIMAtiZE potrzebuje wbudowanego VBench scoring do automatycznej ewaluacji jakości generacji.

### 2.5 Narzędzia i API (E)

| Narzędzie | Typ | Funkcjonalność | Cena | Status (Czerwiec 2026) |
|-----------|-----|----------------|------|------------------------|
| **Sora API** | Official | T2V, I2V, Video Extension | Tokenized | ⛔ **EOL 24 Sep 2026** |
| **Veo 3.1 on Vertex AI** | Official | T2V, I2V, SynthID | $0.35/s | ✅ Aktywny |
| **Veo 3.1 Lite** | Official | T2V, I2V | <$0.18/s | ✅ **NOWY** |
| **Runway Gen-4.5** | Official | T2V, I2V, Act-One | Per generation | ✅ Aktywny |
| **Runway Gen-3 Alpha** | Official | T2V, I2V | Per generation | ⚠️ **EOL 30 Jul 2026** |
| **Kling 3.0 via Fal.ai** | 3rd Party | 4K/60fps, 15s, Audio | $0.10-0.20/s | ✅ **NOWY** |
| **Luma Ray3.14 API** | Official | Multi-keyframe | $0.32/Mpx | ✅ Aktywny |
| **Pika 2.5** | Official | Pikaframes, 25s | Varies | ✅ Aktywny |
| **Seedance 2.0** | BytePlus/Volcengine | 12-asset multimodal, audio-video | ~$0.05/5s @720p | ✅ **NOWY** |
| **HappyHorse 1.1** | Alibaba/Fal.ai | 9-ref, 7-lang lip-sync | $0.14-0.18/s | ✅ **NOWY / OSS** |

**Bezpieczeństwo:**
- **SynthID** (Google) - Invisible watermarking
- **C2PA** - Content authenticity standard
- **OpenAI Moderation** - Content filtering

**So what?** ANIMAtiZE powinno wdrożyć SynthID-style watermarking jako differentiator i wymóg compliance.

### 2.6 UX Reżysera (F)

**Director Knobs w Konkurencji:**

| Kontrolka | Sora | Veo | Runway | Kling | Luma |
|-----------|------|-----|--------|-------|------|
| Shot Type | Prompt | JSON | UI | UI | Concepts |
| Motion Intensity | Prompt | Param | Slider | Slider | Slider |
| FPS | × | × | × | 30fps | × |
| Transitions | Prompt | Prompt | × | ✓ | × |
| Duration | 4/8/12s | 8s | 10s | 3-10s | 10s |
| Seed | ✓ | ✓ | ✓ | ✓ | ✓ |

**So what?** Brak standardowego "Director Panel" w konkurencji = szansa dla ANIMAtiZE.

---

## 3. ANALIZA LUK (GAP ANALYSIS)

| Zdolność Rynkowa | Mamy? | Jak Przewyższyć? | Metryka |
|------------------|-------|------------------|---------|
| Multi-model prompt generation | ✓ | Expand to 6+ models, auto-optimize | Models supported |
| First/Last frame conditioning | × | Add to consistency engine | Keyframe accuracy |
| Motion Brush regions | × | Integrate region-based motion | Region precision |
| Audio sync (lip-sync) | × | Partner or build | Sync accuracy |
| Real-time preview (<2s) | × | LCM integration | Preview latency |
| Multi-shot storytelling | ~ | OneStory-style memory | Shot consistency |
| VBench auto-scoring | × | Embed VBench metrics | Score correlation |
| LoRA custom styles | × | User style training | Training time |
| JSON schema prompts | × | Veo-style structured | Schema compliance |
| Watermarking/provenance | × | SynthID implementation | Detection rate |

### 3.1 Wedge Features (Trudne do Skopiowania, Wysokowartościowe)

1. **Consistency Engine** (MAMY) - Cross-shot character/style/world consistency
2. **Director OS** (BUDOWAĆ) - Film grammar + temporal logic + shot library
3. **Prompt Compiler** (ROZSZERZYĆ) - Intent → multi-model prompt set
4. **Evaluation Harness** (WZMOCNIĆ) - Automated VBench + golden prompts CI
5. **Reference Library** (MAMY) - Persistent character/style/world management
6. **Hierarchical Controls** (BUDOWAĆ) - Narrative/Cinematography/Style layers
7. **Auto-Regeneration** (BUDOWAĆ) - Fix violations automatically
8. **Style Memory Bank** (BUDOWAĆ) - RAG for visual consistency

---

## 4. STRATEGIA (WNIOSKI)

### 4.1 Director OS
- **Film Grammar**: 47 reguł → 100+ z temporalną logiką
- **Shot Library**: Pre-built shot templates z confidence scores
- **Auto Evaluation**: VBench + CLIPScore + human correlation

### 4.2 Prompt Compiler
- **Input**: Director intent (natural language + structured)
- **Output**: Multi-model prompt set (Sora, Veo, Runway, Kling, Luma, Wan)
- **Adapters**: Model-specific optimization z fallbacks

### 4.3 Consistency Engine (ROZSZERZENIE)
- **Character**: >95% F1 identity preservation
- **World**: Spatial relationship memory
- **Style**: RAG-based style anchors
- **Temporal**: <10% ΔRGB lighting variance

### 4.4 Evaluation Harness
- **Benchmark Suite**: 12 golden scenarios
- **Regression CI**: GitHub Actions integration
- **Quality Gates**: Block releases below threshold

---

## 5. DELIVERABLES

### 5.1 Market Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VIDEO GENERATION MARKET MAP                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FRONTIER MODELS (Highest Quality)                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                                     │
│  │ SORA 2  │  │ VEO 3.1 │  │SEEDANCE │                                     │
│  │ PRO     │  │         │  │  1.0    │                                     │
│  │ OpenAI  │  │ Google  │  │ByteDance│                                     │
│  └─────────┘  └─────────┘  └─────────┘                                     │
│                                                                             │
│  PRODUCTION-READY                                                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                        │
│  │ RUNWAY  │  │  KLING  │  │  LUMA   │  │  PIKA   │                        │
│  │ Gen-3   │  │  2.6    │  │  Ray3   │  │  2.5    │                        │
│  │ Alpha   │  │         │  │         │  │         │                        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                        │
│                                                                             │
│  OPEN SOURCE                                                                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                                     │
│  │  WAN    │  │ANIMATEDIFF│ │ SVD    │                                     │
│  │  2.2    │  │         │  │         │                                     │
│  │ Alibaba │  │         │  │Stability│                                     │
│  └─────────┘  └─────────┘  └─────────┘                                     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      ANIMAtiZE POSITIONING                          │   │
│  │  "Director OS" - Orchestration layer above all models               │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐               │   │
│  │  │Movement │  │Consist- │  │ Prompt  │  │ Evalua- │               │   │
│  │  │Predictor│  │  ency   │  │Compiler │  │  tion   │               │   │
│  │  │         │  │ Engine  │  │         │  │ Harness │               │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Control Map

| Kontrola | Sora | Veo | Runway | Kling | Luma | Wan | ANIMAtiZE |
|----------|------|-----|--------|-------|------|-----|-----------|
| Text Prompt | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Image Input | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Camera Control | ~ | ✓ | ✓ | ✓ | ✓ | ~ | **Unified** |
| Motion Brush | × | × | Gen-2 | ✓ | × | × | **Planned** |
| First/Last Frame | × | ✓ | × | ✓ | ✓ | ✓ | **Planned** |
| Duration Control | ✓ | ~ | ~ | ✓ | ✓ | ~ | ✓ |
| Seed/Reproducibility | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Audio Generation | × | ✓ | × | ✓ | × | × | **Planned** |
| Multi-shot | ~ | ✓ | × | ~ | × | ✓ | **✓ Strong** |
| Character Consistency | × | ~ | × | ~ | × | ✓ | **✓ Strong** |
| Style Consistency | × | ✓ | ~ | ~ | × | ✓ | **✓ Strong** |

### 5.3 10 Kluczowych Insights dla ANIMAtiZE

| # | Insight | Kategoria | Wpływ | Źródło |
|---|---------|-----------|-------|--------|
| 1 | Multi-modal LLMs umożliwiają unified pipelines | Model | Fundament | GPT-4V, Gemini |
| 2 | Chain-of-Thought poprawia temporal coherence | Prompting | Jakość | Wei et al. 2024 |
| 3 | RAG dla style consistency (10x szybsze niż fine-tuning) | Control | Retencja | StyleRAG Adobe |
| 4 | Constitutional AI dla content safety | Safety | Compliance | Anthropic |
| 5 | LoRA personalization (1000x tańsze) | Model | Engagement | Hu et al. 2024 |
| 6 | Hierarchical controls dla pro workflows | Control | Pro users | Hertz et al. |
| 7 | Automated eval (CLIP/DreamSim) koreluje 0.8+ z human | Eval | Velocity | Hessel et al. |
| 8 | Watermarking = competitive moat | Moat | Trust | SynthID |
| 9 | LCM = real-time preview | Model | Iteration | Luo et al. |
| 10 | Hybrid human-AI = 10x productivity | UX | Positioning | Disney Research |

### 5.4 Product Backlog (32 pozycje)

Pełny backlog jest dostępny w `src/core/product_backlog.py` i exportowany do `docs/PRODUCT_BACKLOG.md`.

**Top 10 według Priority Score:**

| # | Item | Impact | Effort | Risk | Priority | Owner | Phase |
|---|------|--------|--------|------|----------|-------|-------|
| 1 | User Feedback Collection | 3 | 2 | 1 | 1.35 | FE | Enhancement |
| 2 | Refactor: Decouple Prompt Expansion | 4 | 2 | 1 | 1.80 | R&D | Foundation |
| 3 | RESTful API Foundation | 5 | 3 | 2 | 1.33 | BE | Foundation |
| 4 | Refactor: Modularize Video Model | 4 | 3 | 2 | 1.07 | BE | Foundation |
| 5 | API Rate Limiting | 4 | 3 | 2 | 1.07 | BE | Enterprise |
| 6 | Batch Video Processing | 4 | 3 | 2 | 1.07 | BE | Enhancement |
| 7 | Video Prompt Catalog | 4 | 3 | 2 | 1.07 | Design | Enhancement |
| 8 | Advanced QA Metrics | 4 | 3 | 2 | 1.07 | R&D | Enhancement |
| 9 | Audit Logging | 4 | 3 | 2 | 1.07 | BE | Enterprise |
| 10 | Film Grammar Rule System | 4 | 4 | 3 | 0.70 | R&D | Core |

**Must-Do Refactors (maturity < 0.6):**

| Module | Maturity | Refactor |
|--------|----------|----------|
| Video Model Abstraction Layer | 0.45 | Modularize |
| Prompt Expansion Logic | 0.52 | Decouple |
| Image Generator | 0.48 | Extract to service |

### 5.5 Proponowana Architektura

```yaml
# Versioning Schema
API_VERSION: v2.0
SCHEMA_VERSION: 2.0.0
BREAKING_CHANGES:
  - UnifiedRequest.parameters restructured
  - ConsistencyEngine.validate() returns Report instead of List

# Interface Definitions
interfaces:
  IMovementPredictor:
    analyze(image: bytes) -> MovementPrediction
    predict_camera(scene: SceneAnalysis) -> CameraMovement

  IConsistencyEngine:
    validate_sequence(frames: List[Frame]) -> ConsistencyReport
    create_reference(image: bytes, type: RefType) -> Reference
    match_identity(query: bytes, library: RefLibrary) -> MatchResult

  IPromptCompiler:
    compile(intent: DirectorIntent, model: str) -> ModelPrompt
    expand(prompt: str, style: Style) -> ExpandedPrompt

  IModelAdapter:
    generate(request: UnifiedRequest) -> UnifiedResponse
    get_capabilities() -> ModelCapabilities
    health_check() -> HealthStatus

# Multi-Model Router
router:
  strategy: "quality_first" | "cost_optimized" | "latency_optimized"
  fallback_chain: ["sora", "veo", "runway", "kling"]
  retry_policy:
    max_retries: 3
    backoff: exponential
```

### 5.6 Test Plan (12 Scenariuszy)

| # | Scenariusz | Metryka | Golden Input | Expected Output | Threshold |
|---|------------|---------|--------------|-----------------|-----------|
| 1 | Portrait → cinematic pan | Movement type accuracy | portrait.jpg | "slow_pan_left" | 90% |
| 2 | Landscape → drone reveal | Camera prediction | landscape.jpg | "aerial_reveal" | 85% |
| 3 | Action → tracking shot | Motion intensity | action.jpg | intensity > 0.7 | 90% |
| 4 | Multi-shot character | Identity preservation | char_sequence/ | F1 > 0.95 | 95% |
| 5 | Lighting consistency | ΔRGB variance | lighting_seq/ | variance < 0.10 | 90% |
| 6 | Style anchor match | CLIP similarity | style_ref.jpg | cosine > 0.85 | 85% |
| 7 | Prompt → Sora format | Prompt compliance | intent.json | valid Sora prompt | 100% |
| 8 | Prompt → Veo format | JSON schema valid | intent.json | valid Veo JSON | 100% |
| 9 | API latency | Response time | request.json | latency < 500ms | 95% |
| 10 | Batch processing | Throughput | 100_images/ | >100/hour | 90% |
| 11 | Error handling | Graceful degradation | invalid.jpg | error_response | 100% |
| 12 | Regression suite | No quality drop | golden_set/ | score >= baseline | 100% |

**Golden Prompts:**
```json
{
  "golden_prompts": [
    {
      "id": "GP-001",
      "input_image": "portrait_dramatic.jpg",
      "expected_output": {
        "camera_movement": "slow_push_in",
        "subject_motion": "subtle_breathing",
        "lighting": "rembrandt_soft",
        "duration": 8
      }
    }
  ]
}
```

---

## 6. ZAŁOŻENIA I NIEWIADOME

### Założenia
1. API modeli (Sora, Veo, Runway) pozostaną stabilne przez 6 miesięcy
2. Ceny API nie wzrosną więcej niż 20%
3. VBench pozostanie standardem branżowym
4. First/Last frame conditioning stanie się standardem

### Niewiadome
1. Czy Sora 3 zmieni landscape kontroli?
2. Kiedy audio sync stanie się commoditized?
3. Czy Apple wejdzie na rynek T2V?
4. Regulacje EU AI Act - wpływ na generowanie?
5. Tempo rozwoju open-source (Wan 3.0?)

### Ryzyka
| Ryzyko | Prawdopodobieństwo | Wpływ | Mitygacja |
|--------|-------------------|-------|-----------|
| API deprecation | Średnie | Wysoki | Multi-model fallback |
| Price increases | Wysokie | Średni | Cost optimization layer |
| Quality regression | Niskie | Wysoki | Automated testing |
| Competition catch-up | Średnie | Średni | Wedge feature focus |

---

## 7. PODSUMOWANIE

ANIMAtiZE jest dobrze pozycjonowane jako **"Director OS"** - warstwa orkiestracji ponad modelami generowania wideo. Kluczowe assets:

1. **Consistency Engine** - Dojrzały, trudny do skopiowania
2. **Multi-model adapters** - Już zaimplementowane (Sora, Veo, Runway, Flux, Pika)
3. **47+ Cinematic Rules** - Unikalna biblioteka film grammar
4. **Product Backlog** - 32 pozycje z priorytetyzacją

**Następne Kroki (Q1 2026):**
1. Wdrożyć First/Last Frame conditioning
2. Dodać Motion Brush regions
3. Zintegrować VBench scoring
4. Zbudować Real-time preview (LCM)

---

*Dokument wygenerowany: 2026-02-07*
*Źródła: OpenAI, Google, Runway, Kuaishou, Luma AI, Alibaba, Adobe Research, Stanford HAI*
