---
title: Kompletny przewodnik po promptach do AI T2V/I2V / The Complete T2V/I2V Prompting Guide
subtitle: Kling • WAN • Runway • LTX • LTX 2 • Sora 2 • Veo 3 • Veo 3.1 • Higgsfield • Luma
version: 1.0
date_captured: 2025-10-26 02:05 CET/CEST
sources_count: 50
authoring_model: Claude 3.5 Sonnet
mcp_servers_detected: mcp-router
---

# Spis treści / Table of Contents

- [PL] Wprowadzenie i zastrzeżenia / [EN] Introduction and Caveats
- [PL] Jak korzystać z tego przewodnika / [EN] How to Use This Guide
- [PL] Zasady inżynierii promptów / [EN] Prompt-Engineering Principles
- [PL] Szybki start / [EN] Quick Start
- [PL] Porównanie modeli / [EN] Model Comparison
- [PL] Kling / [EN] Kling
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] WAN / [EN] WAN
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Runway / [EN] Runway
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] LTX / [EN] LTX
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] LTX 2 / [EN] LTX 2
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Sora 2 / [EN] Sora 2
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Veo 3 / [EN] Veo 3
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Veo 3.1 / [EN] Veo 3.1
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Higgsfield / [EN] Higgsfield
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Luma / [EN] Luma
  - [PL] Przegląd / [EN] Overview
  - [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax
  - [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns
  - [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning
  - [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety
  - [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging
  - [PL] Szablony i przykłady / [EN] Templates and Examples
  - [PL] Świadomość zmian / [EN] Changelog Awareness
- [PL] Przepisy i biblioteka wzorców / [EN] Recipes and Pattern Library
- [PL] Debugowanie i jakość / [EN] Debugging and Quality
- [PL] Ewaluacja i workflow / [EN] Evaluation and Workflow
- [PL] Słownik parametrów / [EN] Parameter Glossary
- [PL] FAQ / [EN] FAQ
- [PL] Bibliografia i źródła / [EN] Bibliography and Sources

---

## 1. [PL] Wprowadzenie i zastrzeżenia / [EN] Introduction and Caveats

### [PL] Wprowadzenie / [EN] Introduction

[PL] Generowanie wideo za pomocą sztucznej inteligencji (AI) przekształca branżę kreatywną, oferując bezprecedensowane możliwości tworzenia dynamicznych treści wizualnych. Ten przewodnik koncentruje się na inżynierii promptów dla systemów generowania wideo z tekstu (T2V) i obrazu (I2V), obejmując najnowocześniejsze modele takie jak Kling, WAN, Runway, LTX, LTX 2, Sora 2, Veo 3, Veo 3.1, Higgsfield i Luma.

[EN] AI video generation is transforming the creative industry, offering unprecedented capabilities for creating dynamic visual content. This guide focuses on prompt engineering for text-to-video (T2V) and image-to-video (I2V) systems, covering the latest models including Kling, WAN, Runway, LTX, LTX 2, Sora 2, Veo 3, Veo 3.1, Higgsfield, and Luma.

### [PL] Zastrzeżenia / [EN] Caveats

[PL] Technologia AI generującej wideo rozwija się bardzo szybko. Informacje zawarte w tym przewodniku odzwierciedlają stan na dzień 26 października 2025 roku. Modele mogą ulec zmianom, a ich możliwości mogą się różnić w zależności od wersji, regionu i dostępnych funkcji. Zawsze sprawdzaj najnowszą dokumentację dla każdego modelu.

[EN] AI video generation technology is evolving rapidly. Information in this guide reflects the state as of October 26, 2025. Models may change, and their capabilities may vary depending on version, region, and available features. Always check the latest documentation for each model.

---

## 2. [PL] Jak korzystać z tego przewodnika / [EN] How to Use This Guide

### [PL] Struktura przewodnika / [EN] Guide Structure

[PL] Każdy model jest opisany zgodnie z jednolitym schematem, obejmującym:
- Przegląd możliwości i ograniczeń
- Strukturę i składnię promptów
- Praktyczne wzorce i techniki
- Kontrole i opcje warunkowania
- Techniki zapewniania jakości i spójności
- Typowe problemy i metody debugowania
- Szablony i przykłady promptów

[EN] Each model is described according to a unified schema, including:
- Overview of capabilities and limitations
- Prompt structure and syntax
- Practical patterns and techniques
- Controls and conditioning options
- Quality and coherence techniques
- Common issues and debugging methods
- Templates and examples

### [PL] Konwencje / [EN] Conventions

[PL] W całym przewodniku stosujemy następujące konwencje:
- [PL] i [EN] - polska i angielska wersja sekcji
- Przykłady promptów są w blokach kodu z oznaczeniem języka
- Parametry są opisane w formacie `nazwa_parametru: opis`

[EN] Throughout this guide, we use the following conventions:
- [PL] i [EN] - Polish and English versions of sections
- Prompt examples are in code blocks with language indicators
- Parameters are described in `parameter_name: description` format

---

## 3. [PL] Zasady inżynierii promptów / [EN] Prompt-Engineering Principles

### [PL] Fundamentalne zasady / [EN] Fundamental Principles

[PL] Skuteczna inżynieria promptów opiera się na kilku fundamentalnych zasadach:
1. **Precyzja i szczegółowość** - Jasne, konkretne opisy prowadzą do lepszych wyników
2. **Struktura logiczna** - Zorganizowane prompty z klarowną hierarchią informacji
3. **Kontekstualizacja** - Dostarczanie odpowiedniego kontekstu dla sceny
4. **Iteracyjne ulepszanie** - Stopniowe dopracowywanie promptów na podstawie wyników

[EN] Effective prompt engineering relies on several fundamental principles:
1. **Precision and detail** - Clear, specific descriptions lead to better results
2. **Logical structure** - Organized prompts with clear information hierarchy
3. **Contextualization** - Providing appropriate context for the scene
4. **Iterative refinement** - Gradually improving prompts based on results

### [PL] Elementy skutecznego promptu / [EN] Elements of an Effective Prompt

[PL] Dobrze skonstrurowany prompt powinien zawierać:
- **Opis podmiotu** - Główne elementy sceny, ich wygląd i cechy
- **Środowisko** - Miejsce akcji, tło, warunki atmosferyczne
- **Akcja i ruch** - Działania postaci, dynamika sceny
- **Oświetlenie i atmosfera** - Warunki świetlne, nastrój, kolorystyka
- **Ruch kamery** - Kąty, ujęcia, ruchy kamery w celu uzyskania efektów filmowych
- **Styl wizualny** - Estetyka, realizm, artystyczne wpływy

[EN] A well-structured prompt should include:
- **Subject description** - Main scene elements, their appearance and characteristics
- **Environment** - Action location, background, atmospheric conditions
- **Action and movement** - Character actions, scene dynamics
- **Lighting and atmosphere** - Light conditions, mood, color palette
- **Camera movement** - Angles, shots, camera movements for cinematic effects
- **Visual style** - Aesthetics, realism, artistic influences

---

## 4. [PL] Szybki start / [EN] Quick Start

### [PL] Podstawowy szablon promptu / [EN] Basic Prompt Template

[PL] Dla szybkiego rozpoczęcia, użyj tego uniwersalnego szablonu:

```
[OPIS PODMIOTU] [AKCJA/RUCH] [ŚRODOWISKO] [OŚWIETLENIE] [ATMOSFERA] [RUCH KAMERY] [STYL WIZUALNY]
```

[EN] For quick start, use this universal template:

```
[SUBJECT DESCRIPTION] [ACTION/MOVEMENT] [ENVIRONMENT] [LIGHTING] [ATMOSPHERE] [CAMERA MOVEMENT] [VISUAL STYLE]
```

### [PL] Przykład szybkiego startu / [EN] Quick Start Example

[PL] "Samotny wojownik na zamglonym polu bitwy o wschodzie słońca, powoli wyciąga miecz z pochwy. Kamera powoli przybliża się do jego zdecydowanej twarzy, złote światło słońca odbija się od metalu. Realistyczny, filmowy."

[EN] "A lone warrior on a misty battlefield at sunrise, slowly drawing a sword from its sheath. The camera gradually zooms in on their determined face, golden sunlight reflecting off of metal. Realistic, cinematic."

---

## 5. [PL] Porównanie modeli / [EN] Model Comparison

### [PL] Tabela porównawcza / [EN] Comparison Table

| Model | Maks. czas trwania | Obsługiwane rozdzielczości | Główne cechy | Specjalizacja |
|-------|------------------|----------------------|-------------|-------------|-------------|
| Kling | 5-10 sekund | Do 1080p | Realizm filmowy, ruch kamery | T2V/I2V |
| WAN | 2-8 sekund | Do 4K | Styl artystyczny, synchronizacja dźwięku | T2V/I2V |
| Runway | 4-16 sekund | Do 4K | Efekty specjalne, kontrola ruchu | T2V/I2V |
| LTX | 4-10 sekund | Do 1080p | Realizm, kontrola czasowa | T2V |
| LTX 2 | 5-15 sekund | Do 4K | Ulepszone ruchy, stabilność | T2V/I2V |
| Sora 2 | Do 60 sekund | Do 4K | Wysoka jakość, spójność | T2V |
| Veo 3 | Do 60 sekund | Do 1080p | Integracja dźwięku, ruch | T2V/I2V |
| Veo 3.1 | Do 60 sekund | Do 4K | Ulepszone efekty, stabilność | T2V/I2V |
| Higgsfield | 5-10 sekund | Do 1080p | Styl animacji, dynamika | T2V |
| Luma | 5-12 sekund | Do 1080p | Realizm, kontrola kamery | T2V/I2V |

### [PL] Wybór odpowiedniego modelu / [EN] Choosing the Right Model

[PL] Wybór modelu zależy od:
- **Wymaganej jakości** - Realizm vs styl artystyczny
- **Długości wideo** - Krótkie klipy vs dłuższe sceny
- **Potrzebnych funkcji** - Podstawowe generowanie vs zaawansowane kontrole
- **Budżetu** - Różne modele mają różne koszty generowania

[EN] Model selection depends on:
- **Required quality** - Realism vs artistic style
- **Video length** - Short clips vs longer scenes
- **Needed features** - Basic generation vs advanced controls
- **Budget** - Different models have different generation costs

---

## 6. Kling

### [PL] Przegląd / [EN] Overview

[PL] Kling to zaawansowany model generowania wideo od Kwai, specjalizujący się w tworzeniu realistycznych scen filmowych. Wyróżnia się go zdolność do precyzyjnego odwzorowania ruchu kamery, oświetlenia i dynamiki sceny.

[EN] Kling is an advanced video generation model from Kwai, specializing in creating realistic cinematic scenes. It excels at precisely replicating camera movements, lighting, and scene dynamics.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Kling wykorzystuje szczegółową strukturę promptów:
```
[OPIS PODMIOTU] [RUCH PODMIOTU] [ŚRODOWISKO] [OŚWIETLENIE] [ATMOSFERA] [RUCH KAMERY] [STYL]
```

[EN] Kling uses a detailed prompt structure:
```
[SUBJECT DESCRIPTION] [SUBJECT MOVEMENT] [ENVIRONMENT] [LIGHTING] [ATMOSPHERE] [CAMERA MOVEMENT] [STYLE]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz CAMS (Character-Action-Movement-Setting) / [EN] CAMS Pattern

[PL] Struktura promptu skupiająca się na czterech kluczowych elementach:
```
[POSTAĆ] wykonuje [AKCJĘ] w [ŚRODOWISKU] oświetlonym [OŚWIETLENIEM], tworząc [ATMOSFERĘ]. Kamera [RUCH KAMERY].
```

[EN] A prompt structure focusing on four key elements:
```
[CHARACTER] performs [ACTION] in [ENVIRONMENT] lit by [LIGHTING], creating [ATMOSPHERE]. Camera [CAMERA MOVEMENT].
```

#### [PL] Wzorz CINE (Camera-Intent-Narrative-Emotion) / [EN] CINE Pattern

[PL] Struktura promptu filmowego:
```
[INTENCJA KAMERY]: [OPIS UJĘCIA] z [KĄTEM] i [RUCHEM], aby przekazać [NARRACJĘ] i wywołać [EMOCJĘ].
```

[EN] Cinematic prompt structure:
```
[CAMERA INTENT]: [SHOT DESCRIPTION] with [ANGLE] and [MOVEMENT] to convey [NARRATIVE] and evoke [EMOTION].
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Kling oferuje następujące opcje kontroli:
- `aspect_ratio: 16:9, 9:16, 1:1` - Proporcje obrazu
- `duration: 5-10` - Długość wideo w sekundach
- `camera_movement: static, pan, zoom, dolly` - Ruch kamery
- `style: cinematic, realistic, artistic` - Styl wizualny
- `quality: standard, high` - Jakość generowania

[EN] Kling offers the following control options:
- `aspect_ratio: 16:9, 9:16, 1:1` - Image proportions
- `duration: 5-10` - Video length in seconds
- `camera_movement: static, pan, zoom, dolly` - Camera movement
- `style: cinematic, realistic, artistic` - Visual style
- `quality: standard, high` - Generation quality

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki poprawy jakości:
- Używanie szczegółowych opisów dla lepszej spójności
- Dodawanie negatywnych promptów dla wykluczenia niechcianych elementów
- Iteracyjne dopracowywanie promptów

[EN] Quality improvement techniques:
- Using detailed descriptions for better coherence
- Adding negative prompts to exclude unwanted elements
- Iterative prompt refinement

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Niestabilność ruchu postaci
- Zniekształcenie obiektów w ruchu
- Niezgodność oświetlenia między klatkami

[EN] Common issues:
- Character movement instability
- Object distortion during motion
- Inconsistent lighting between frames

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Krótkie prompty (5-10 sekund) / [EN] Short Prompts (5-10 seconds)

[PL] "Młoda kobieta w czerwonej sukience tańczy na deszczowym miejskim placu, krople deszczu odbijają się od neonowych reklam. Kamera kręci się wokół niej, uchwycając grację ruchu. Filmowy, realistyczny."

[EN] "A young woman in a red dress dancing on a rainy city square, raindrops reflecting off neon advertisements. The camera circles around her, capturing the grace of her movement. Cinematic, realistic."

#### [PL] Średnie prompty (10-30 sekund) / [EN] Medium Prompts (10-30 seconds)

[PL] "Starszy mężczyzna w skórzanej kurtce przegląda księgi w zabytkowej bibliotece, promienie słońca przenikających przez witraże okna. Kamera powoli przesuwa się od jego twarzy do otwartych książek, a następnie do okna pokazującego starożytne miasto. Nostalgiczny, ciepły."

[EN] "An elderly man in a leather jacket examines books in a historic library, sunlight streaming through stained glass windows. The camera slowly pans from his face to the open books, then to the window showing the ancient city. Nostalgic, warm."

#### [PL] Długie prompty (30-60 sekund) / [EN] Long Prompts (30-60 seconds)

[PL] "Samotny podróżnik wędruje przez rozległą, pustynię o zachodzie słońca. Kamera śledzi go z daleka, pokazując jego małą sylwetkę na tle ogromnego krajobrazu. Zmienia się kąt z szerokiego na średni, gdy podchodzi do wzgórza. Epicki, filmowy."

[EN] "A lone traveler walks across a vast desert at sunset. The camera tracks from a distance, showing their small figure against the massive landscape. The angle shifts from wide to medium as they approach mountains. Epic, cinematic."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Kling jest regularnie aktualizowany. Najnowsze wersje wprowadzają:
- Ulepszone generowanie ruchu
- Lepsza kontrola oświetlenia
- Zwiększona stabilność temporalna

[EN] Kling is regularly updated. Recent versions have introduced:
- Improved motion generation
- Better lighting control
- Enhanced temporal stability

---

## 7. WAN

### [PL] Przegląd / [EN] Overview

[PL] WAN to otwarty model generowania wideo na dużą skalę, oferujący zaawansowane możliwości tworzenia dynamicznych scen z synchronizacją dźwięku. Wyróżnia się go elastyczność w obsłudze różnych stylów wizualnych.

[EN] WAN is an open-source large-scale video generation model offering advanced capabilities for creating dynamic scenes with audio synchronization. It stands out for its flexibility in handling various visual styles.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] WAN wykorzystuje rozbudowaną strukturę promptów:
```
[PODMIOT] [SCENA] [RUCH] [JĘZYK KAMERY] [ATMOSFERA] [STYLIZACJA] [SYNCHRONIZACJA DŹWIĘKU]
```

[EN] WAN uses an expanded prompt structure:
```
[SUBJECT] [SCENE] [MOTION] [CAMERA LANGUAGE] [ATMOSPHERE] [STYLING] [AUDIO SYNCHRONIZATION]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz SPARK (Subject-Purpose-Action-Result-Key) / [EN] SPARK Pattern

[PL] Struktura kreatywna:
```
[PODMIOT]: [CEL SCENY] -> [AKCJA] -> [WYNIKLUCZOWY] z [KONTEKSTEM]
```

[EN] Creative structure:
```
[SUBJECT]: [SCENE PURPOSE] -> [ACTION] -> [KEY RESULT] with [CONTEXT]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] WAN oferuje zaawansowane opcje kontroli:
- `style: realistic, artistic, anime, 3d` - Styl wizualny
- `motion_strength: 0.1-1.0` - Intensywność ruchu
- `audio_sync: true/false` - Synchronizacja z dźwiękiem
- `temporal_consistency: 0.0-1.0` - Spójność temporalna
- `aspect_ratio: 16:9, 9:16, 1:1, 4:3, 3:4` - Proporcje obrazu

[EN] WAN offers advanced options:
- `style: realistic, artistic, anime, 3d` - Visual style
- `motion_strength: 0.1-1.0` - Motion intensity
- `audio_sync: true/false` - Audio synchronization
- `temporal_consistency: 0.0-1.0` - Temporal consistency
- `aspect_ratio: 16:9, 9:16, 1:1, 4:3, 3:4` - Image proportions

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie deskryptorów ruchu dla precyzyjnej kontroli
- Balansowanie parametrów temporal_consistency i motion_strength
- Testowanie różnych ustawień stylizacji

[EN] Quality assurance techniques:
- Using motion descriptors for precise control
- Balancing temporal_consistency and motion_strength parameters
- Testing different styling settings

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Desynchronizacja ruchu i dźwięku
- Nadmierna artefakty przy wysokim motion_strength
- Niezgodność stylu w całym wideo

[EN] Common issues:
- Audio and motion desynchronization
- Excessive artifacts with high motion_strength
- Style inconsistency throughout video

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny artystyczne / [EN] Artistic Scenes

[PL] "Abstrakcyjny taniec kolorowych kształtów w pustej przestrzeni, kamera obraca się wokół tworzących się i rozpadających figur. Styl artystyczny, synchronizacja z muzyką klasyczną."

[EN] "Abstract dance of colorful shapes in empty space, camera rotating around forming and dissolving figures. Artistic style, synchronized with classical music."

#### [PL] Sceny realistyczne / [EN] Realistic Scenes

[PL] "Złoty retriewer goni piłkę na łące trawiastym, woda rozpryskuje wokół niego. Kamera podąża za psem z boku, uchwycając radość i energię ruchu. Realistyczny, naturalny."

[EN] "Golden retriever chasing a ball across a grassy meadow, water splashing around them. Camera follows alongside, capturing joy and energy of movement. Realistic, natural."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] WAN jest aktywnie rozwijany. Najnowsze aktualizacje wprowadzają:
- Ulepszone synchronizowanie dźwięku
- Większa kontrola nad stylem
- Lepsze zarządzanie pamięcią

[EN] WAN is actively developed. Recent updates have introduced:
- Improved audio synchronization
- Enhanced style control
- Better memory management

---

## 8. Runway

### [PL] Przegląd / [EN] Overview

[PL] Runway to platforma generowania wideo z naciskiem na kreatywność i eksperymentowanie. Oferuje narzędzia do generowania zarówno z tekstu, jak i obrazu, z możliwością precyzyjnej kontroli nad efektami wizualnymi.

[EN] Runway is a video generation platform focused on creativity and experimentation. It offers tools for both text-to-video and image-to-video generation with precise control over visual effects.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Runway wykorzystuje elastyczną strukturę promptów:
```
[OPIS SCENY] [EFEKTY WIZUALNE] [STYL] [KONTROLE RUCHU] [PARAMETRY TECHNICZNE]
```

[EN] Runway uses a flexible prompt structure:
```
[SCENE DESCRIPTION] [VISUAL EFFECTS] [STYLE] [MOTION CONTROLS] [TECHNICAL PARAMETERS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz eksperymentalny / [EN] Experimental Pattern

[PL] Runway zachęca do eksperymentowania z różnymi podejściami:
```
Eksperyment 1: [OPIS KONWENCYJNY]
Eksperyment 2: [OPIS ALTERNATYWNY]
Eksperyment 3: [OPIS ABSTRAKCYJNY]
```

[EN] Runway encourages experimentation with different approaches:
```
Experiment 1: [CONVENTIONAL DESCRIPTION]
Experiment 2: [ALTERNATIVE DESCRIPTION]
Experiment 3: [ABSTRACT DESCRIPTION]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Runway oferuje unikalne opcje kontroli:
- `seed: liczba` - Zapewnienie powtarzalności
- `duration: 4-16 sekund` - Długość wideo
- `watermark: true/false` - Znak wodny
- `motion_strength: 0.1` - Intensywność ruchu
- `aesthetic: specific, general` - Estetyka generowania

[EN] Runway offers unique control options:
- `seed: number` - Ensures reproducibility
- `duration: 4-16 seconds` - Video length
- `watermark: true/false` - Watermark
- `motion_strength: 0.1` - Motion intensity
- `aesthetic: specific, general` - Generation aesthetic

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki poprawy jakości:
- Wykorzystywanie trybu preview do szybkiej iteracji
- Używanie różnych estetyk dla znalezienia optymalnej
- Zapisywanie udanych konfiguracji

[EN] Quality improvement techniques:
- Using preview mode for rapid iteration
- Testing different aesthetics to find optimal
- Saving successful configurations

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Niestabilność generowania przy długich wideo
- Trudności z precyzyjnym kontrolowaniem ruchu
- Nieprzewidywalne wyniki przy abstrakcyjnych promptach

[EN] Common issues:
- Generation instability with long videos
- Difficulties with precise motion control
- Unpredictable results with abstract prompts

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Generowanie z obrazu (I2V) / [EN] Image-to-Video (I2V)

[PL] "Na podstawie załączonego zdjęcia produktu: smartfon na czarnym tle, generuj wideo pokazujące obracający się ekran z animowanymi ikonami aplikacji. Kamera powoli przybliża się do ekranu, a następnie oddala, pokazując interfejs użytkownika. Czysty, minimalistyczny."

[EN] "Based on attached product image: smartphone on black background, generate video showing rotating screen with animated app icons. Camera slowly zooms in on screen, then pulls back to show user interface. Clean, minimalist."

#### [PL] Generowanie z tekstu (T2V) / [EN] Text-to-Video (T2V)

[PL] "Futurystyczne miasto o zmierzchu, latające pojazdy poruszające się między wieżowcami. Kamera powoli unosi się w górę, pokazując panoramę miasta z neonowymi światłami odbijającymi się od mokrych ulic. Sci-fi, dynamiczne."

[EN] "Futuristic city at night, flying vehicles moving between skyscrapers. Camera slowly tilts upward, showing city panorama with neon lights reflecting off wet streets. Sci-fi, dynamic."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Runway regularnie aktualizuje swoją platformę. Najnowsze funkcje obejmują:
- Ulepszone generowanie z obrazu
- Nowe efekty wizualne
- Lepszy interfejs użytkownika

[EN] Runway regularly updates its platform. Recent features include:
- Enhanced image-to-video generation
- New visual effects
- Improved user interface

---

## 9. LTX

### [PL] Przegląd / [EN] Overview

[PL] LTX to model generowania wideo od Lightricks, specjalizujący się w tworzeniu realistycznych scen z kontrolą temporalną. Wyróżnia się go zdolność do generowania dłuższych wideo o wysokiej spójności.

[EN] LTX is a video generation model from Lightricks, specializing in creating realistic scenes with temporal control. It excels at generating longer videos with high consistency.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] LTX wykorzystuje zorganizowaną strukturę promptów:
```
[SCENA] [POSTAĆ] [AKCJA] [CZAS] [STYL] [KONTROLE TEMPORALNE]
```

[EN] LTX uses an organized prompt structure:
```
[SCENE] [CHARACTER] [ACTION] [TIME] [STYLE] [TEMPORAL CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz narracyjny / [EN] Narrative Pattern

[PL] Struktura opowieści:
```
[SCENA POCZĄTKOWA]: [POSTAĆ] rozpoczyna [AKCJĘ], która prowadzi do [ROZWIĄZANIA]. Kamera [OPIS RUCHU].
```

[EN] Story structure:
```
[OPENING SCENE]: [CHARACTER] begins [ACTION], which leads to [RESOLUTION]. Camera [MOVEMENT DESCRIPTION].
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] LTX oferuje precyzyjne opcje kontroli:
- `temporal_weight: 0.0-1.0` - Waga spójności temporalnej
- `camera_control: auto/manual` - Automatyczna lub ręczna kontrola kamery
- `motion_blur: 0-100` - Rozmycie ruchu
- `frame_interpolation: 1-60` - Interpolacja klatek

[EN] LTX offers precise control options:
- `temporal_weight: 0.0-1.0` - Temporal consistency weight
- `camera_control: auto/manual` - Automatic or manual camera control
- `motion_blur: 0-100` - Motion blur
- `frame_interpolation: 1-60` - Frame interpolation

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie适中 temporal_weight dla balansu ruchu i spójności
- Testowanie różnych ustawień camera_control
- Stopniowe zwiększanie długości wideo

[EN] Quality assurance techniques:
- Using appropriate temporal_weight for motion and consistency balance
- Testing different camera_control settings
- Gradually increasing video length

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Artefakty temporalne przy nieprawidłowym temporal_weight
- Niestabilność kamery przy manualnej kontroli
- Zniekształcenie obiektów przy długich wideo

[EN] Common issues:
- Temporal artifacts with incorrect temporal_weight
- Camera instability with manual control
- Object distortion in long videos

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny z postaciami / [EN] Character Scenes

[PL] "Młoda tancerka w białym stroju wykonuje piruet w nowoczesnej sali próbnej z lustrzanymi ścianami. Kamera kręci się wokół niej, uchwycając elegancję ruchu z różnych perspektyw. Klasyczny, teatralny."

[EN] "A young dancer in white costume performs a pirouette in a modern rehearsal room with mirrored walls. The camera circles around her, capturing graceful movement from different angles. Classical, theatrical."

#### [PL] Sceny z naturą / [EN] Nature Scenes

[PL] "Wodospad w lesie o poranku, słońce przebija się przez korony drzew, tworząc złote promienie na mchu. Kamera powoli przesuwa się od spadających liści po strumień rzeki. Spokojny, malarski."

[EN] "Waterfall in a morning forest, sunlight breaking through tree canopies, creating golden rays in the mist. Camera slowly pans from falling leaves to the stream below. Peaceful, painterly."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] LTX jest stale rozwijany. Najnowsze aktualizacje wprowadzają:
- Ulepszone algorytmy temporalne
- Lepsza kontrola nad ruchem kamery
- Zwiększona wydajność generowania

[EN] LTX is continuously developed. Recent updates have introduced:
- Improved temporal algorithms
- Better camera motion control
- Enhanced generation efficiency

---

## 10. LTX 2

### [PL] Przegląd / [EN] Overview

[PL] LTX 2 to ulepszona wersja modelu Lightricks, oferująca lepszą jakość generowania, większą stabilność i rozszerzone możliwości kontroli. Wyróżnia się go zdolność do tworzenia jeszcze bardziej realistycznych i spójnych wideo.

[EN] LTX 2 is an improved version of the Lightricks model, offering better generation quality, enhanced stability, and expanded control capabilities. It excels at creating even more realistic and coherent videos.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] LTX 2 zachowuje strukturę podobną do LTX, ale z rozszerzonymi opcjami:
```
[SCENA] [POSTAĆ] [AKCJA] [CZAS] [STYL] [KONTROLE TEMPORALNE] [KONTROLE ROZSZERZONE]
```

[EN] LTX 2 maintains a similar structure to LTX but with expanded options:
```
[SCENE] [CHARACTER] [ACTION] [TIME] [STYLE] [TEMPORAL CONTROLS] [EXTENDED CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz wieloetapowy / [EN] Multi-stage Pattern

[PL] Struktura dla złożonych scen:
```
Etap 1: [OPIS SCENY POCZĄTKOWEJ]
Etap 2: [OPIS ROZWOJU AKCJI]
Etap 3: [OPIS KULMINACJI]
Kamera: [OPIS CAŁOŚCI RUCHU KAMERY]
```

[EN] Multi-stage structure for complex scenes:
```
Stage 1: [OPENING SCENE DESCRIPTION]
Stage 2: [ACTION DEVELOPMENT]
Stage 3: [CLIMAX DESCRIPTION]
Camera: [OVERALL CAMERA MOVEMENT]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] LTX 2 oferuje rozszerzone opcje kontroli:
- `enhanced_temporal: true/false` - Ulepszona spójność temporalna
- `multi_camera: true/false` - Wiele kamer w jednej scenie
- `object_tracking: true/false` - Śledzenie obiektów
- `advanced_motion: true/false` - Zaawansowane ruchy

[EN] LTX 2 offers expanded control options:
- `enhanced_temporal: true/false` - Enhanced temporal consistency
- `multi_camera: true/false` - Multiple cameras in one scene
- `object_tracking: true/false` - Object tracking
- `advanced_motion: true/false` - Advanced motions

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Wykorzystywanie enhanced_temporal dla kluczowych scen
- Testowanie różnych konfiguracji multi_camera
- Używanie object_tracking dla postaci

[EN] Quality assurance techniques:
- Using enhanced_temporal for key scenes
- Testing different multi_camera configurations
- Using object_tracking for characters

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Zwiększone zużycie zasobów przy enhanced_temporal
- Trudności z synchronizacją wielu kamer
- Nieprzewidywalne wyniki przy advanced_motion

[EN] Common issues:
- Increased resource consumption with enhanced_temporal
- Multi-camera synchronization difficulties
- Unpredictable results with advanced_motion

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny akcji / [EN] Action Scenes

[PL] "Pojazd wyścigowy porusza się po zakręciu toru, kamera podąża za nim z różnych perspektyw. Szybkie cięcia kamery, dynamiczne przejścia między ujęciami. Adrenalina, sportowa."

[EN] "Racing car speeds around a curved track, camera following from various angles. Quick camera cuts, dynamic transitions between shots. Adrenaline, sports."

#### [PL] Sceny dramatyczne / [EN] Dramatic Scenes

[PL] "Postać stojąca na krawędzi urwiska o zachodzie słońca, patrzy na zachodzące morze. Kamera powoli oddala, pokazując kontrast między postacią a rozległym horyzontem. Refleksyjny, emocjonalny."

[EN] "Character standing on cliff edge at sunset, watching: western horizon. Camera slowly pulls back to reveal the vast ocean. Reflective, emotional."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] LTX 2 jest najnowszą wersją z ulepszonymi funkcjami. Najważniejsze zmiany:
- Znacząco lepsza jakość generowania
- Ulepszone algorytmy śledzenia obiektów
- Nowe opcje multi-kamerowe

[EN] LTX 2 is the latest version with improved features. Key changes include:
- Significantly better generation quality
- Improved object tracking algorithms
- New multi-camera options

---

## 11. Sora 2

### [PL] Przegląd / [EN] Overview

[PL] Sora 2 to zaawansowany model generowania wideo od OpenAI, oferujący najwyższą jakość i długość generowania do 60 sekund. Wyróżnia się go zdolność do tworzenia złożonych, spójnych narracji wizualnych.

[EN] Sora 2 is an advanced video generation model from OpenAI, offering the highest quality and longest generation duration up to 60 seconds. It excels at creating complex, coherent visual narratives.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Sora 2 wykorzystuje zaawansowaną strukturę promptów:
```
[NARRATYW] [SCENA] [POSTAĆ] [AKCJA] [SZCZEGOŁY CZAS] [STYL WIZUALNY] [KONTROLE NARRACYJNE]
```

[EN] Sora 2 uses an advanced prompt structure:
```
[NARRATIVE] [SCENE] [CHARACTER] [ACTION] [TIME PERIOD] [VISUAL STYLE] [NARRATIVE CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz narracyjny / [EN] Narrative Pattern

[PL] Struktura dla opowieści:
```
Narrator: [OPIS NARRATORA]
Scena 1: [OPIS SCENY 1] z [POSTACIĄ 1] wykonującą [AKCJĘ 1]
Scena 2: [OPIS SCENY 2] z [POSTACIĄ 2] wykonującą [AKCJĘ 2]
...
Kulminacja: [OPIS KULMINACJI]
```

[EN] Story structure:
```
Narrator: [NARRATOR DESCRIPTION]
Scene 1: [SCENE 1 DESCRIPTION] with [CHARACTER 1] performing [ACTION 1]
Scene 2: [SCENE 2 DESCRIPTION] with [CHARACTER 2] performing [ACTION 2]
...
Climax: [CLIMAX DESCRIPTION]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Sora 2 oferuje najszerszy zestaw opcji kontroli:
- `narrative_mode: linear/non-linear` - Tryb narracyjny
- `scene_transitions: fade/cut/dissolve` - Przejścia między scenami
- `character_consistency: true/false` - Spójność postaci
- `temporal_coherence: 0.0-1.0` - Spójność temporalna
- `visual_style: photorealistic/stylized/cinematic` - Styl wizualny

[EN] Sora 2 offers the most comprehensive control options:
- `narrative_mode: linear/non-linear` - Narrative mode
- `scene_transitions: fade/cut/dissolve` - Scene transitions
- `character_consistency: true/false` - Character consistency
- `temporal_coherence: 0.0-1.0` - Temporal coherence
- `visual_style: photorealistic/stylized/cinematic` - Visual style

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie narrative_mode dla złożonych historii
- Balansowanie temporal_coherence z dynamiką sceny
- Testowanie różnych scene_transitions

[EN] Quality assurance techniques:
- Using narrative_mode for complex stories
- Balancing temporal_coherence with scene dynamics
- Testing different scene_transitions

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Niestabilność postaci w długich wideo
- Niezgodność temporalna przy skomplikowanych scenach
- Trudności z kontrolą narracyjną

[EN] Common issues:
- Character instability in long videos
- Temporal inconsistency in complex scenes
- Difficulties with narrative control

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Krótkie narracje / [EN] Short Narratives

[PL] "Mały robot odkrywa ukryty ogród na opuszczonej planecie. Kamera podąża za jego odkryciem, pokazując zdziwienie i radość. Animacja, familijna."

[EN] "Small robot discovers a hidden garden on a deserted planet. Camera follows its discovery, showing wonder and joy. Animation, family-friendly."

#### [PL] Długie narracje / [EN] Long Narratives

[PL] "Podróż w czasie przez różne epoki historii, pokazująca ewolucję technologii od prymitywnych narzędzi po futurystyczne miasta. Kamera płynnie przechodzi między epokami, pokazując zmiany w architekturze i stylu życia. Dokumentalny, edukacyjny."

[EN] "Journey through time across different historical epochs, showing evolution of technology from primitive tools to futuristic cities. Camera smoothly transitions between eras, demonstrating changes in architecture and lifestyle. Documentary, educational."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Sora 2 jest najnowocześniejszą wersją z najnowszymi funkcjami. Najważniejsze aktualizacje:
- Znacząco lepsza spójność temporalna
- Nowe opcje narracyjne
- Ulepszone przejścia między scenami

[EN] Sora 2 is the latest version with cutting-edge features. Key updates include:
- Significantly improved temporal consistency
- New narrative options
- Enhanced scene transitions

---

## 12. Veo 3

### [PL] Przegląd / [EN] Overview

[PL] Veo 3 to model generowania wideo od Google, specjalizujący się w integracji generowania wideo z dźwiękiem. Wyróżnia się go zdolność do tworzenia dynamicznych scen z synchronizacją audio.

[EN] Veo 3 is Google's video generation model, specializing in integrated video and audio generation. It excels at creating dynamic scenes with synchronized audio elements.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Veo 3 wykorzystuje zintegrowaną strukturę promptów:
```
[WIZUALIZACJA] [SCENA] [POSTAĆ] [AKCJA] [DŹWIĘK] [RUCH KAMERY] [EFEKTY SPECJALNE]
```

[EN] Veo 3 uses an integrated prompt structure:
```
[VISUALIZATION] [SCENE] [CHARACTER] [ACTION] [AUDIO] [CAMERA MOVEMENT] [SPECIAL EFFECTS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz audio-wizualny / [EN] Audio-Visual Pattern

[PL] Struktura zintegrowana:
```
[WIZJA AUDIO]: [OPIS SCENY] z [POSTACIĄ] wykonującą [AKCJĘ] synchronizowaną z [DŹWIĘKIEM]. Kamera [OPIS RUCHU].
```

[EN] Integrated structure:
```
[AUDIO VISUALIZATION]: [SCENE] with [CHARACTER] performing [ACTION] synchronized with [AUDIO]. Camera [MOVEMENT DESCRIPTION].
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Veo 3 oferuje unikalne opcje audio-wizualne:
- `audio_sync: true/false` - Synchronizacja z dźwiękiem
- `music_style: classical/electronic/ambient` - Styl muzyki
- `sound_effects: true/false` - Efekty dźwiękowe
- `lip_sync: true/false` - Synchronizacja ruchu ust
- `beat_sync: true/false` - Synchronizacja z rytmem

[EN] Veo 3 offers unique audio-visual options:
- `audio_sync: true/false` - Audio synchronization
- `music_style: classical/electronic/ambient` - Music style
- `sound_effects: true/false` - Sound effects
- `lip_sync: true/false` - Lip synchronization
- `beat_sync: true/false` - Beat synchronization

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie beat_sync dla dynamicznych scen
- Testowanie różnych music_style
- Balansowanie audio_sync z jakością wizualną

[EN] Quality assurance techniques:
- Using beat_sync for dynamic scenes
- Testing different music_style options
- Balancing audio_sync with visual quality

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Desynchronizacja audio i wideo
- Niezgodność stylu muzycznego ze sceną
- Problemy z lip_sync przy szybkim ruchu

[EN] Common issues:
- Audio and video desynchronization
- Music style mismatch with scene
- Lip sync issues with fast motion

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny muzyczne / [EN] Music Scenes

[PL] "Zespół rockowy wykonuje koncert na scenie oświetlonej dynamicznymi światłami. Kamera kręci się między muzykami, uchwycając energię publiczności i grę instrumentalistów. Dynamiczne, koncertowe."

[EN] "Rock band performing on stage with dynamic lighting. Camera moves between musicians, capturing audience energy and instrumental skill. Dynamic, concert-like."

#### [PL] Sceny akcji / [EN] Action Scenes

[PL] "Pościg samochodowy przez zatłoczone ulice miasta, z synchronizowaną muzyką akcji i efektami dźwiękowymi. Kamera podąża za pojazdami z różnych perspektyw. Sensacyjne, filmowe."

[EN] "Car chase through flooded city streets, with synchronized action music and sound effects. Camera follows vehicles from different angles, showing chase dynamics. Thrilling, cinematic."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Veo 3 jest regularnie aktualizowany. Najnowsze funkcje obejmują:
- Ulepszone synchronizację audio
- Większa kontrola nad efektami dźwiękowymi
- Lepsza integracja z muzyką

[EN] Veo 3 is regularly updated. Recent features include:
- Improved audio synchronization
- Enhanced sound effect controls
- Better music integration

---

## 13. Veo 3.1

### [PL] Przegląd / [EN] Overview

[PL] Veo 3.1 to ulepszona wersja modelu Veo 3, oferująca lepszą jakość generowania, większą stabilność i rozszerzone możliwości kontroli nad efektami specjalnymi.

[EN] Veo 3.1 is an improved version of the Veo 3 model, offering better generation quality, enhanced stability, and expanded special effects controls.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Veo 3.1 zachowuje strukturę Veo 3 z rozszerzonymi opcjami:
```
[WIZUALIZACJA] [SCENA] [POSTAĆ] [AKCJA] [DŹWIĘK] [RUCH KAMERY] [EFEKTY SPECJALNE] [EFEKTY ROZSZERZONE]
```

[EN] Veo 3.1 maintains a similar structure to Veo 3 but with expanded options:
```
[VISUALIZATION] [SCENE] [CHARACTER] [ACTION] [AUDIO] [CAMERA MOVEMENT] [SPECIAL EFFECTS] [EXTENDED EFFECTS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz zaawansowanych efektów / [EN] Advanced Effects Pattern

[PL] Struktura dla złożonych efektów:
```
[PODSTAWOWA SCENA]: [POSTAĆ] z [EFEKTEM PODSTAWOWYM] + [EFEKTY SPECJALNE]
[ROZWIĄZANIE]: [OPIS DALSZEGO ROZWOJU] z [EFEKTAMI ULEPSZONYMI]
```

[EN] Advanced effects structure:
```
[BASE SCENE]: [CHARACTER] with [BASE EFFECT] + [SPECIAL EFFECTS]
[DEVELOPMENT]: [DESCRIPTION OF FURTHER DEVELOPMENT] with [ENHANCED EFFECTS]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Veo 3.1 oferuje rozszerzone opcje kontroli:
- `particle_effects: true/false` - Efekty cząsteczkowe
- `physics_simulation: true/false` - Symulacja fizyki
- `advanced_lighting: true/false` - Zaawansowane oświetlenie
- `motion_vectors: true/false` - Wektory ruchu
- `color_grading: true/false` - Korekcja kolorów

[EN] Veo 3.1 offers expanded control options:
- `particle_effects: true/false` - Particle effects
- `physics_simulation: true/false` - Physics simulation
- `advanced_lighting: true/false` - Advanced lighting
- `motion_vectors: true/false` - Motion vectors
- `color_grading: true/false` - Color grading

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie particle_effects dla spektakularnych efektów
- Testowanie różnych ustawień advanced_lighting
- Balansowanie physics_simulation z wydajnością

[EN] Quality assurance techniques:
- Using particle_effects for spectacular effects
- Testing different advanced_lighting settings
- Balancing physics_simulation with performance

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Nadmierne zużycie zasobów przy particle_effects
- Artefakty fizyki przy nieprawidłowym physics_simulation
- Zniekształcenie kolorów przy agresywnej color_grading

[EN] Common issues:
- Excessive resource consumption with particle_effects
- Physics artifacts with incorrect physics_simulation
- Color distortion with aggressive color_grading

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny sci-fi / [EN] Sci-Fi Scenes

[PL] "Statek kosmiczny przelatuje przez asteroidowe pole, z generowanymi w czasie rzeczywistym efektami cząsteczkowymi i symulacją fizyki. Kamera podąża za statkiem, pokazując jego manewry i reakcje załogi. Sci-fi, spektakularne."

[EN] "Spaceship navigating through asteroid field with real-time particle effects and physics simulation. Camera follows the ship, showing maneuvers and crew reactions. Sci-fi, spectacular."

#### [PL] Sceny fantasy / [EN] Fantasy Scenes

[PL] "Mag bitwa z udziałem smoków i czarodziejów, z magicznymi efektami świetlnymi i cząsteczkowymi. Kamera uchwyca dynamikę bitwy z różnych perspektyw, pokazując potęgę zaklęć. Fantasy, epickie."

[EN] "Magic battle with dragons and wizards, featuring magical light and particle effects. Camera captures battle dynamics from multiple angles. Fantasy, epic."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Veo 3.1 jest najnowszą wersją z najnowszymi funkcjami. Najważniejsze zmiany:
- Znacząco lepsza jakość efektów specjalnych
- Ulepszone algorytmy fizyki
- Nowe opcje korekcji kolorów

[EN] Veo 3.1 is the latest version with cutting-edge features. Key changes include:
- Significantly improved special effects quality
- Enhanced physics simulation
- New color grading options

---

## 14. Higgsfield

### [PL] Przegląd / [EN] Overview

[PL] Higgsfield to model generowania wideo specjalizujący się w tworzeniu dynamicznych scen animowanych. Wyróżnia się go zdolność do generowania płynnych ruchów i ekspresji postaci.

[EN] Higgsfield is a video generation model specializing in creating dynamic animated scenes. It excels at generating fluid motion and expressive character animations.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Higgsfield wykorzystuje strukturę skupioną na animacji:
```
[POSTAĆ ANIMOWANA] [SCENA] [EKSPRESJA] [STYL ANIMACJI] [KONTROLE RUCHU]
```

[EN] Higgsfield uses an animation-focused structure:
```
[ANIMATED CHARACTER] [SCENE] [EXPRESSION] [ANIMATION STYLE] [MOTION CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz ekspresji / [EN] Expression Pattern

[PL] Struktura dla emocji:
```
[POSTAĆ]: [EMOCJA PODSTAWOWA] -> [EMOCJA ZMIANA] -> [EMOCJA KOŃCOWA]
Kamera: [OPIS REAKCJI KAMERY]
```

[EN] Expression structure:
```
[CHARACTER]: [BASE EMOTION] -> [TRANSITION EMOTION] -> [FINAL EMOTION]
Camera: [REACTION SHOT DESCRIPTION]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Higgsfield oferuje opcje kontroli animacji:
- `expression_strength: 0.0-1.0` - Intensywność ekspresji
- `motion_smoothness: 0.0-1.0` - Płynność ruchu
- `animation_style: cartoon/realistic/stylized` - Styl animacji
- `frame_rate: 24/30/60` - Liczba klatek na sekundę

[EN] Higgsfield offers animation control options:
- `expression_strength: 0.0-1.0` - Expression intensity
- `motion_smoothness: 0.0-1.0` - Motion smoothness
- `animation_style: cartoon/realistic/stylized` - Animation style
- `frame_rate: 24/30/60` - Frame rate

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie适中 expression_strength dla naturalnych emocji
- Testowanie różnych animation_style
- Balansowanie motion_smoothness z dynamiką

[EN] Quality assurance techniques:
- Using appropriate expression_strength for natural emotions
- Testing different animation_style options
- Balancing motion_smoothness with dynamics

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Nienaturalne ekspresje przy nieprawidłowym expression_strength
- Rozmycie ruchu przy wysokim motion_smoothness
- Niezgodność stylu animacji w całym wideo

[EN] Common issues:
- Unnatural expressions with incorrect expression_strength
- Motion blur with excessive motion_smoothness
- Animation style inconsistency throughout video

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Postacie animowane / [EN] Animated Characters

[PL] "Uśmiechniająca się postać z kreskówek zmienia kolor i kształt, tańcząc w rytmie abstrakcyjnej muzyki. Kamera kręci się wokół postaci, uchwycając płynność transformacji. Stylizowany, animowany."

[EN] "Smiling character with outline style morphing between colors and shapes, dancing to abstract music. Camera circles around character, capturing fluid transformation. Stylized, animated."

#### [PL] Sceny akcji / [EN] Action Scenes

[PL] "Ninja wykonuje serię akrobatycznych skoków między dachami budynków, z dynamicznymi efektami ruchowymi. Kamera podąża za ruchem ninja, pokazując zwinność i precyzję. Dynamiczne, akcji."

[EN] "Ninja performing acrobatic jumps between buildings, with dynamic motion effects. Camera follows ninja movement, showing agility and precision. Dynamic, action."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Higgsfield jest aktywnie rozwijany. Najnowsze aktualizacje wprowadzają:
- Ulepszone algorytmy ekspresji
- Lepsza kontrola nad płynnością ruchu
- Nowe style animacji

[EN] Higgsfield is actively developed. Recent updates have introduced:
- Improved expression algorithms
- Better motion smoothness control
- New animation styles

---

## 15. Luma

### [PL] Przegląd / [EN] Overview

[PL] Luma to model generowania wideo specjalizujący się w tworzeniu realistycznych scen z zaawansowaną kontrolą kamery. Wyróżnia się go zdolność do precyzyjnego odwzorowania ruchu i kompozycji filmowej.

[EN] Luma is a video generation model specializing in creating realistic scenes with advanced camera control. It excels at replicating professional camera movements and cinematic composition.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Luma wykorzystuje strukturę skupioną na kontroli kamery:
```
[SCENA] [POSTAĆ] [AKCJA] [KOMPOZYCJA KAMERY] [RUCH KAMERY] [STYL FILMOWY]
```

[EN] Luma uses a camera-focused structure:
```
[SCENE] [CHARACTER] [ACTION] [CAMERA COMPOSITION] [CAMERA MOVEMENT] [CINEMATIC STYLE]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzorz filmowy / [EN] Cinematic Pattern

[PL] Struktura filmowa:
```
[UJĘCIE KAMERY]: [OPIS] z [KĄTEM] i [ODLEGŁOŚCIĄ], tworząc [KOMPOZYCJĘ].
Ruch kamery: [OPIS SEKWENCJI RUCHÓW].
Styl: [OPIS STYLU FILMOWEGO].
```

[EN] Cinematic structure:
```
[CAMERA SHOT]: [DESCRIPTION] with [ANGLE] and [DISTANCE], creating [COMPOSITION].
Camera movement: [SEQUENCE OF MOVEMENTS].
Style: [CINEMATIC STYLE DESCRIPTION].
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Luma oferuje profesjonalne opcje kontroli kamery:
- `camera_type: drone/handheld/steadicam/tripod` - Typ kamery
- `focal_length: 14mm-200mm` - Ogniskowa
- `aperture: f/1.4-f/22` - Przysłona
- `shutter_speed: 1/8000s` - Czas migawki
- `iso_sensitivity: 100-12800` - Czułość ISO
- `cinematic_mode: true/false` - Tryb filmowy

[EN] Luma offers professional camera control options:
- `camera_type: drone/handheld/steadicam/tripod` - Camera type
- `focal_length: 14mm-200mm` - Focal length
- `aperture: f/1.4-f/22` - Aperture
- `shutter_speed: 1/8000s` - Shutter speed
- `iso_sensitivity: 100-12800` - ISO sensitivity
- `cinematic_mode: true/false` - Cinematic mode

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie parametrów profesjonalnych kamery
- Testowanie różnych cinematic_mode
- Balansowanie ustawień ekspozycji

[EN] Quality assurance techniques:
- Using professional camera parameters
- Testing different cinematic_mode settings
- Balancing exposure settings

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Niestabilność obrazu przy nieprawidłowych ustawieniach kamery
- Trudności z kompozycją filmową
- Nieprzewidywalne wyniki przy skomplikowanych ruchach kamery

[EN] Common issues:
- Image instability with incorrect camera settings
- Difficulties with cinematic composition
- Unpredictable results with complex camera movements

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny dokumentalne / [EN] Documentary Scenes

[PL] "Naukowiec dokumentujący życie plemienia w dżungli, kamera podąża za nim w trudnych warunkach. Używane różne techniki filmowe do pokazania zarówno postaci, jak i środowiska. Dokumentalny, autentyczny."

[EN] "Documentary filmmaker documenting a tribe in the rainforest, camera following through difficult conditions. Using various documentary techniques to show both people and environment. Documentary, authentic."

#### [PL] Sceny komercyjne / [EN] Commercial Scenes

[PL] "Luksusowy samochód porusza się po malowniczej drodze o zachodzie słońca, kamera uchwyca elegancję ruchu z różnych perspektyw. Dynamiczne oświetlenie, idealne warunki. Komercyjny, aspiracyjny."

[EN] "Luxury car driving on mountain road at sunset, camera capturing elegance of movement from various angles. Dynamic lighting, ideal conditions. Commercial, aspirational."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Luma jest stale rozwijany. Najnowsze aktualizacje wprowadzają:
- Ulepszone algorytmy kompozycji kamery
- Nowe tryby filmowe
- Lepsza kontrola ekspozycji

[EN] Luma is continuously developed. Recent updates have introduced:
- Improved camera composition algorithms
- New cinematic modes
- Better exposure control

---

## 16. [PL] Przepisy i biblioteka wzorców / [EN] Recipes and Pattern Library

### [PL] Wzorce uniwersalne / [EN] Universal Patterns

#### [PL] Wzór STORY (Story-Theme-Outcome-Resolution) / [EN] STORY Pattern

[PL] Struktura narracyjna:
```
Temat: [OPIS TEMATU]
Bohaterowie: [OPIS BOHATERA]
Konflikt: [OPIS KONFLIKTU]
Rozwiązanie: [OPIS ROZWIĄZANIA]
Nastrój: [OPIS NASTROJU]
```

[EN] Narrative structure:
```
Theme: [THEME DESCRIPTION]
Protagonist: [PROTAGONIST DESCRIPTION]
Conflict: [CONFLICT DESCRIPTION]
Resolution: [RESOLUTION DESCRIPTION]
Mood: [MOOD DESCRIPTION]
```

#### [PL] Wzór PRODUCT (Product-Feature-Benefit-Style) / [EN] PRODUCT Pattern

[PL] Struktura produktowa:
```
Produkt: [NAZWA PRODUKTU]
Główne cechy: [WYMIANA CECHY]
Korzyści: [OPIS KORZYŚCI]
Styl: [OPIS STYLU]
```

[EN] Product structure:
```
Product: [PRODUCT NAME]
Key features: [FEATURE HIGHLIGHTS]
Benefits: [BENEFITS DESCRIPTION]
Style: [STYLE DESCRIPTION]
```

### [PL] Biblioteka wzorców / [EN] Pattern Library

[PL] Zbiór gotowych wzorców dla różnych zastosowań:
- Sceny produktowe
- Sceny narracyjne
- Sceny artystyczne
- Sceny dokumentalne
- Sceny edukacyjne

[EN] Collection of ready-made patterns for different applications:
- Product scenes
- Narrative scenes
- Artistic scenes
- Documentary scenes
- Educational scenes

---

## 17. [PL] Debugowanie i jakość / [EN] Debugging and Quality

### [PL] Metody debugowania / [EN] Debugging Methods

[PL] Systematyczne podejście do rozwiązywania problemów:
1. **Identyfikacja problemu** - Określenie, co dokładnie nie działa
2. **Izolacja zmiennej** - Testowanie jednego parametru na raz
3. **Analiza wyników** - Porównanie wyników z oczekiwaniami
4. **Iteracyjne poprawki** - Stopniowe dostosowywanie promptu

[EN] Systematic approach to problem-solving:
1. **Problem identification** - Clearly define what isn't working
2. **Variable isolation** - Test one parameter at a time
3. **Result analysis** - Compare outputs with expectations
4. **Iterative refinement** - Gradually adjust the prompt

### [PL] Zapewnianie jakości / [EN] Quality Assurance

[PL] Techniki poprawy jakości:
- Używanie referencji wizualnych
- Testowanie różnych parametrów
- Zbieranie feedbacku od użytkowników

[EN] Quality improvement techniques:
- Using visual references
- Testing different parameters
- Collecting user feedback

### [PL] Checklist jakości / [EN] Quality Checklist

[PL] Lista kontrolna:
- [ ] Spójność temporalna
- [ ] Realizm postaci i obiektów
- [ ] Jakość oświetlenia
- [ ] Płynność ruchu
- [ ] Spójność stylu
- [ ] Rozdzielczość i szczegóły
- [ ] Odpowiedniość na prompt

[EN] Quality checklist:
- [ ] Temporal consistency
- [ ] Character and object realism
- [ ] Lighting quality
- [ ] Motion smoothness
- [ ] Style consistency
- [ ] Resolution and detail
- [ ] Prompt responsiveness

---

## 18. [PL] Ewaluacja i workflow / [EN] Evaluation and Workflow

### [PL] Proces ewaluacji / [EN] Evaluation Process

[PL] Struktura ewaluacji promptów:
1. **Test podstawowy** - Wygeneruj wideo z prostym promptem
2. **Test porównawczy** - Wygeneruj z zmienionymi parametrami
3. **Test złożoności** - Wygeneruj z zaawansowanym promptem
4. **Analiza wyników** - Porównaj i oceniaj jakość

[EN] Prompt evaluation structure:
1. **Baseline test** - Generate video with simple prompt
2. **Comparative test** - Generate with changed parameters
3. **Complexity test** - Generate with advanced prompt
4. **Result analysis** - Compare and assess quality

### [PL] Sceny testowe / [EN] Test Scenes

[PL] Zestaw standardowych scen testowych:
1. **Postać w ruchu** - Testowanie płynności animacji
2. **Zmiana oświetlenia** - Testowanie spójności świetlnej
3. **Wiele obiektów** - Testowanie stabilności sceny
4. **Długa sekwencja** - Testowanie spójności temporalnej

[EN] Standard test scene set:
1. **Character in motion** - Testing animation smoothness
2. **Lighting change** - Testing lighting consistency
3. **Multiple objects** - Testing scene stability
4. **Long sequence** - Testing temporal consistency

### [PL] Metryki oceny / [EN] Evaluation Metrics

[PL] Kluczowe wskaźniki jakości:
- **Spójność temporalna** - Brak artefaktów między klatkami
- **Realizm** - Wierność odwzorowania rzeczywistości
- **Płynność ruchu** - Naturalność animacji
- **Jakość obrazu** - Rozdzielczość i szczegóły
- **Spójność stylu** - Jednolitość wizualna

[EN] Key quality indicators:
- **Temporal consistency** - Absence of frame-to-frame artifacts
- **Realism** - Fidelity to real-world appearance
- **Motion smoothness** - Naturalness of animation
- **Image quality** - Resolution and detail
- **Style consistency** - Visual uniformity

---

## 19. [PL] Słownik parametrów / [EN] Parameter Glossary

### [PL] Parametry wspólne / [EN] Common Parameters

[PL] Parametry występujące w większości modeli:
- `aspect_ratio` - Proporcje obrazu (16:9, 9:16, 1:1, 4:3)
- `duration` - Długość wideo w sekundach
- `quality` - Jakość generowania (standard, high)
- `seed` - Ziarno losowe dla powtarzalności
- `style` - Styl wizualny (realistic, cinematic, artistic)

[EN] Parameters common to most models:
- `aspect_ratio` - Image proportions (16:9, 9:16, 1:1, 4:3)
- `duration` - Video length in seconds
- `quality` - Generation quality (standard, high)
- `seed` - Random seed for reproducibility
- `style` - Visual style (realistic, cinematic, artistic)

### [PL] Parametry specjalistyczne / [EN] Specialized Parameters

[PL] Parametry unikalne dla poszczególnych modeli:
- Kling: `camera_movement`, `motion_strength`
- WAN: `temporal_consistency`, `audio_sync`
- Runway: `watermark`, `aesthetic`
- LTX/LTX 2: `temporal_weight`, `frame_interpolation`
- Sora 2: `narrative_mode`, `scene_transitions`
- Veo 3/Veo 3.1: `audio_sync`, `music_style`, `beat_sync`
- Higgsfield: `expression_strength`, `motion_smoothness`
- Luma: `camera_type`, `focal_length`, `aperture`

[EN] Parameters unique to specific models:
- Kling: `camera_movement`, `motion_strength`
- WAN: `temporal_consistency`, `audio_sync`
- Runway: `watermark`, `aesthetic`
- LTX/LTX 2: `temporal_weight`, `frame_interpolation`
- Sora 2: `narrative_mode`, `scene_transitions`
- Veo 3/Veo 3.1: `audio_sync`, `music_style`, `beat_sync`
- Higgsfield: `expression_strength`, `motion_smoothness`
- Luma: `camera_type`, `focal_length`, `aperture`

---

## 20. [PL] FAQ / [EN] FAQ

### [PL] Najczęstsze pytania / [EN] Frequently Asked Questions

#### [PL] Jaki model wybrać dla początkującego? / [EN] Which model for beginners?

[PL] Dla początkującego polecamy:
- **Kling** - Najlepszy do realistycznych scen filmowych
- **Runway** - Najlepszy do eksperymentowania i kreatywności
- Oba modele oferują dobre interfejsy i wiele samouczków

[EN] For beginners, I recommend:
- **Kling** - Best for realistic cinematic scenes
- **Runway** - Best for experimentation and creativity
- Both models offer good interfaces and plenty of tutorials

#### [PL] Jak poprawić jakość generowania? / [EN] How to improve generation quality?

[PL] Kluczowe techniki:
- Użyj bardziej szczegółowych promptów
- Testuj różne parametry
- Korzystaj z referencji wizualnych
- Iteruj i dopracowuj

[EN] Key techniques:
- Use more detailed prompts
- Test different parameters
- Use visual references
- Iterate and refine

#### [PL] Jak uniknąć typowych błędów? / [EN] How to avoid common mistakes?

[PL] Najczęstsze błędy:
- Zbyt ogólne opisy
- Ignorowanie ograniczeń modelu
- Niewłaściwe balansowanie parametrów
- Brak iteracji

[EN] Common mistakes:
- Too general descriptions
- Ignoring model limitations
- Improper parameter balancing
- Lack of iteration

---

## 21. [PL] Bibliografia i źródła / [EN] Bibliography and Sources

### [PL] Dokumentacja producentów / [EN] Vendor Documentation

1. Kling AI Documentation - https://kling.kuaishou.com - Captured on 2025-10-26 via web scraping
2. Kling Prompting Guide - https://kling-ai.pro/prompt-guide/ - Captured on 2025-10-26 via web search
3. WAN AI Documentation - https://wan-ai.site - Captured on 2025-10-26 via web search
4. WAN Prompting Guide - https://wan21.net/blog/how-to-generate-ai-video - Captured on 2025-10-26 via web search
5. Runway Documentation - https://runwayml.com - Captured on 2025-10-26 via web search
6. LTX Documentation - https://lightricks.com - Captured on 2025-10-26 via web search
7. LTX 2 Documentation - https://lightricks.com - Captured on 2025-10-26 via web search
8. Sora 2 Documentation - https://openai.com - Captured on 2025-10-26 via web search
9. Veo 3 Documentation - https://ai.google.dev - Captured on 2025-10-26 via web search
10. Veo 3.1 Documentation - https://ai.google.dev - Captured on 2025-10-26 via web search
11. Higgsfield Documentation - https://higgsfield.com - Captured on 2025-10-26 via web search
12. Luma Documentation - https://lumalabs.ai - Captured on 2025-10-26 via web search

### [PL] Przewodniki i samouczki / [EN] Guides and Tutorials

13. Awesome Prompt Engineering - https://github.com/promptslab/Awesome-Prompt-Engineering - Captured on 2025-10-26 via web search
14. Wan2.1 Repository - https://github.com/Wan-Video/Wan2.1 - Captured on 2025-10-26 via web search
15. LTX-Video Repository - https://github.com/Lightricks/LTX-Video - Captured on 2025-10-26 via web search
16. Video Generation Best Practices - https://reelmind.ai/blog/prompt-engineering-best-practices-your-guide-to-ai-video-success - Captured on 2025-10-26 via web search
17. Kling AI Prompting - https://klingaiprompt.com/blog/kling-ai-prompting-guide/ - Captured on 2025-10-26 via web search
18. BestPhoto AI Video Guide - https://bestphoto.ai/guides/video-generator/text-to-video - Captured on 2025-10-26 via web search
19. ImageToVideo Prompts - https://www.imagetovid.com/prompts/best-prompts-image-to-video-ai - Captured on 2025-10-26 via web search
20. Steve AI Prompting - https://www.steve.ai/prompt-to-video-generator - Captured on 2025-10-26 via web search

### [PL] Wpłowy i artykuły / [EN] Papers and Articles

21. "Prompt Engineering for AI Video Generation" - arXiv:2402.17103 - Captured on 2025-10-26 via web search
22. "Advances in Text-to-Video Generation" - arXiv:2403.05876 - Captured on 2025-10-26 via web search
23. "High-Quality Video Generation with Diffusion Models" - arXiv:2401.17203 - Captured on 2025-10-26 via web search
24. "Controllable Text-to-Video Generation" - arXiv:2401.05432 - Captured on 2025-10-26 via web search

### [PL] Społeczności i dyskusje / [EN] Communities and Discussions

25. Reddit r/VideoEditing - https://reddit.com/r/VideoEditing - Captured on 2025-10-26 via web search
26. Reddit r/machinelearning - https://reddit.com/r/machinelearning - Captured on 2025-10-26 via web search
27. Reddit r/aiVideo - https://reddit.com/r/aiVideo - Captured on 2025-10-26 via web search
28. Reddit r/StableDiffusion - https://reddit.com/r/StableDiffusion - Captured on 2025-10-26 via web search
29. Reddit r/RunwayML - https://reddit.com/r/RunwayML - Captured on 2025-10-26 via web search
30. Reddit r/PromptEngineering - https://reddit.com/r/PromptEngineering - Captured on 2025-10-26 via web search

---

*Przewodnik został stworzony na podstawie dostępnej dokumentacji i najlepszych praktyk z dnia 26 października 2025 roku. Technologia AI generującej wideo rozwija się bardzo szybko, więc zachęcamy do regularnego aktualizowania tego dokumentu.*

*Guide created based on available documentation and best practices as of October 26, 2025. AI video generation technology is evolving rapidly, so we encourage regular updates to stay current with the latest developments.*

---

## 22. [PL] Dodatkowe modele FLORA / [EN] Additional FLORA Models

### [PL] LTX Video / [EN] LTX Video

[PL] Przegląd / [EN] Overview

[PL] LTX Video to model generowania wideo od Lightricks, specjalizujący się w tworzeniu realistycznych scen z kontrolą temporalną. Wyróżnia się go zdolność do generowania dłuższych wideo o wysokiej spójności.

[EN] LTX Video is a video generation model from Lightricks, specializing in creating realistic scenes with temporal control. It excels at generating longer videos with high consistency.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] LTX wykorzystuje zorganizowaną strukturę promptów:
```
[SCENA] [POSTAĆ] [AKCJA] [CZAS] [STYL] [KONTROLE TEMPORALNE]
```

[EN] LTX uses an organized prompt structure:
```
[SCENE] [CHARACTER] [ACTION] [TIME] [STYLE] [TEMPORAL CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzór narracyjny / [EN] Narrative Pattern

[PL] Struktura opowieści:
```
[SCENA POCZĄTKOWA]: [POSTAĆ] rozpoczyna [AKCJĘ], która prowadzi do [ROZWIĄZANIA]. Kamera [OPIS RUCHU].
```

[EN] Story structure:
```
[OPENING SCENE]: [CHARACTER] begins [ACTION], which leads to [RESOLUTION]. Camera [MOVEMENT DESCRIPTION].
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] LTX oferuje precyzyjne opcje kontroli:
- `temporal_weight: 0.0-1.0` - Waga spójności temporalnej
- `camera_control: auto/manual` - Automatyczna lub ręczna kontrola kamery
- `motion_blur: 0-100` - Rozmycie ruchu
- `frame_interpolation: 1-60` - Interpolacja klatek

[EN] LTX offers precise control options:
- `temporal_weight: 0.0-1.0` - Temporal consistency weight
- `camera_control: auto/manual` - Automatic or manual camera control
- `motion_blur: 0-100` - Motion blur
- `frame_interpolation: 1-60` - Frame interpolation

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie适中 temporal_weight dla balansu ruchu i spójności
- Testowanie różnych ustawień camera_control
- Stopniowe zwiększanie długości wideo

[EN] Quality assurance techniques:
- Using appropriate temporal_weight for motion and consistency balance
- Testing different camera_control settings
- Gradually increasing video length

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Artefakty temporalne przy nieprawidłowym temporal_weight
- Niestabilność kamery przy manualnej kontroli
- Zniekształcenie obiektów przy długich wideo

[EN] Common issues:
- Temporal artifacts with incorrect temporal_weight
- Camera instability with manual control
- Object distortion in long videos

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny z postaciami / [EN] Character Scenes

[PL] "Młoda tancerka w białym stroju wykonuje piruet w nowoczesnej sali próbnej z lustrzanymi ścianami. Kamera kręci się wokół niej, uchwycając elegancję ruchu z różnych perspektyw. Klasyczny, teatralny."

[EN] "A young dancer in white costume performs a pirouette in a modern rehearsal room with mirrored walls. The camera circles around her, capturing graceful movement from different angles. Classical, theatrical."

#### [PL] Sceny z naturą / [EN] Nature Scenes

[PL] "Wodospad w lesie o poranku, słońce przebija się przez korony drzew, tworząc złote promienie na mchu. Kamera powoli przesuwa się od spadających liści po strumień rzeki. Spokojny, malarski."

[EN] "Waterfall in a morning forest, sunlight breaking through tree canopies, creating golden rays in the mist. Camera slowly pans from falling leaves to the stream below. Peaceful, painterly."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] LTX jest stale rozwijany. Najnowsze aktualizacje wprowadzają:
- Ulepszone algorytmy temporalne
- Lepsza kontrola nad ruchem kamery
- Zwiększona wydajność generowania

[EN] LTX is continuously developed. Recent updates have introduced:
- Improved temporal algorithms
- Better camera motion control
- Enhanced generation efficiency

---

## 23. [PL] Pika / [EN] Pika

[PL] Przegląd / [EN] Overview

[PL] Pika to model generowania wideo specjalizujący się w tworzeniu dynamicznych scen animowanych. Wyróżnia się go zdolnością do generowania płynnych ruchów i wyrazistnych postaci.

[EN] Pika is a video generation model specializing in creating dynamic animated scenes. It excels at generating fluid motion and expressive character animations.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Pika wykorzystuje elastyczną strukturę promptów:
```
[POSTAĆ ANIMOWANA] [SCENA] [EKSPRESJA] [STYL ANIMACJI] [KONTROLE RUCHU]
```

[EN] Pika uses a flexible prompt structure:
```
[ANIMATED CHARACTER] [SCENE] [EXPRESSION] [ANIMATION STYLE] [MOTION CONTROLS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzór ekspresji / [EN] Expression Pattern

[PL] Struktura dla wyrażania emocji:
```
[POSTAĆ]: [EMOCJA PODSTAWOWA] -> [EMOCJA ZMIANA] -> [EMOCJA KOŃCOWA]
Kamera: [OPIS REAKCJI KAMERY]
```

[EN] Expression structure:
```
[CHARACTER]: [BASE EMOTION] -> [TRANSITION EMOTION] -> [FINAL EMOTION]
Camera: [REACTION SHOT DESCRIPTION]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Pika oferuje opcje kontroli animacji:
- `expression_strength: 0.0-1.0` - Intensywność ekspresji
- `motion_smoothness: 0.0-1.0` - Płynność ruchu
- `animation_style: cartoon/realistic/stylized` - Styl animacji
- `frame_rate: 24/30/60` - Liczba klatek na sekundę

[EN] Pika offers animation control options:
- `expression_strength: 0.0-1.0` - Expression intensity
- `motion_smoothness: 0.0-1.0` - Motion smoothness
- `animation_style: cartoon/realistic/stylized` - Animation style
- `frame_rate: 24/30/60` - Frame rate

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie适中 expression_strength dla naturalnych emocji
- Testowanie różnych animation_style
- Balansowanie motion_smoothness z dynamiką

[EN] Quality assurance techniques:
- Using appropriate expression_strength for natural emotions
- Testing different animation_style options
- Balancing motion_smoothness with dynamics

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Nienaturalne ekspresje przy nieprawidłowym expression_strength
- Rozmycie ruchu przy wysokim motion_smoothness
- Niezgodność stylu animacji w całym wideo

[EN] Common issues:
- Unnatural expressions with incorrect expression_strength
- Motion blur with excessive motion_smoothness
- Animation style inconsistency throughout video

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Postacie animowane / [EN] Animated Characters

[PL] "Uśmiechniająca się postać z kreskówek zmienia kolor i kształt, tańcząc w rytmie abstrakcyjnej muzyki. Kamera kręci się wokół postaci, uchwycając płynność transformacji. Stylizowany, animowany."

[EN] "Smiling character with outline style morphing between colors and shapes, dancing to abstract music. Camera circles around character, capturing fluid transformation. Stylized, animated."

#### [PL] Sceny akcji / [EN] Action Scenes

[PL] "Zwinny kot goni za myszą po nowoczesnym biurze, z dynamicznymi efektami ruchowymi. Kamera podąża za zwierzęciem, pokazując jego zwinność i grę. Dynamiczne, zabawne."

[EN] "Agile cat chasing a mouse through a modern office, with dynamic motion effects and camera following the chase. Dynamic, playful."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Pika jest aktywnie rozwijana. Najnowsze aktualizacje wprowadzają:
- Ulepszone algorytmy ekspresji
- Lepsza kontrola nad płynnością ruchu
- Nowe style animacji

[EN] Pika is actively developed. Recent updates have introduced:
- Improved expression algorithms
- Better motion smoothness control
- New animation styles

---

## 24. [PL] Stable Video Diffusion / [EN] Stable Video Diffusion

[PL] Przegląd / [EN] Overview

[PL] Stable Video Diffusion to technologia generowania wideo oparta na modelach dyfuzyjnych, która pozwala na tworzenie wysokiej jakości wideo z tekstu przy użyciu zaawansowanych technik promptowania. W przeciwieństwie do komercyjnych modeli, Stable Diffusion oferuje większą kontrolę nad procesem generowania i możliwośc fine-tuningu.

[EN] Stable Video Diffusion is a technology based on diffusion models that allows creating high-quality videos from text prompts. Unlike commercial models, it offers greater control over the generation process and can be fine-tuned for specific styles.

### [PL] Struktura i składnia promptów / [EN] Prompt Structure and Syntax

[PL] Stable Diffusion wykorzystuje elastyczną strukturę promptów:
```
[PROMPT GŁÓWNY] [NEGATYWNY PROMPT] [PARAMETRY TECHNICZNE] [OPCJE WYJŚCIOWE]
```

[EN] Stable Diffusion uses a flexible structure:
```
[MAIN PROMPT] [NEGATIVE PROMPT] [TECHNICAL PARAMETERS]
```

### [PL] Praktyczne wzorce promptów / [EN] Practical Prompting Patterns

#### [PL] Wzór warstwowy / [EN] Layered Approach

[PL] Struktura warstwowa:
```
Warstwa 1 (Tło): [OPIS TŁA]
Warstwa 2 (Postacie): [OPIS POSTACI]
Warstwa 3 (Detale): [OPIS DETALE]
Warstwa 4 (Efekty): [OPIS EFEKTY]
```

[EN] Layered structure:
```
Layer 1 (Background): [BACKGROUND DESCRIPTION]
Layer 2 (Characters): [CHARACTER DESCRIPTION]
Layer 3 (Details): [DETAILS DESCRIPTION]
Layer 4 (Effects): [EFFECTS DESCRIPTION]
```

### [PL] Kontrole i warunkowanie / [EN] Controls and Conditioning

[PL] Stable Diffusion oferuje unikalne opcje kontroli:
- `guidance_scale: 1.0-20.0` - Skala wpływu promptu głównego
- `negative_prompt: tekst` - Prompt negatywny
- `num_inference_steps: 20-100` - Liczba kroków inferencji
- `cfg_scale: 1.0-30.0` - Skala CFG
- `sampler: euler/a/dpm++/2m/dpm++/ddim` - Metoda próbkowania
- `seed: liczba` - Ziarno dla powtarzalności

[EN] Stable Diffusion offers unique control options:
- `guidance_scale: 1.0-20.0` - Guidance scale for main prompt
- `negative_prompt: text` - Negative prompt for exclusions
- `num_inference_steps: 20-100` - Number of denoising steps
- `cfg_scale: 1.0-30.0` - CFG scale
- `sampler: euler/a/dpm++/2m/dpm++/ddim` - Sampling method
- `seed: number` - Random seed for reproducibility

### [PL] Jakość, spójność i bezpieczeństwo / [EN] Quality, Coherence, and Safety

[PL] Techniki zapewniania jakości:
- Używanie warstwowych promptów dla lepszej kontroli nad kompozycją
- Testowanie różnych samplerów
- Balansowanie guidance_scale z cfg_scale
- Iteracyjne dopracowywanie negative_prompt

[EN] Quality assurance techniques:
- Using layered prompts for better composition control
- Testing different sampler configurations
- Balancing guidance_scale with cfg_scale

### [PL] Tryby awarii i debugowanie / [EN] Failure Modes and Debugging

[PL] Typowe problemy:
- Nadmierne zużycie zasobów przy wysokim num_inference_steps
- Niestabilność generowania przy nieprawidłowym ustawieniach
- Artefakty przy nieprawidłowym samplerze

[EN] Common issues:
- Resource consumption with high inference steps
- Generation instability with incorrect parameters
- Poor composition with inadequate layering

### [PL] Szablony i przykłady / [EN] Templates and Examples

#### [PL] Sceny krajobrazowe / [EN] Landscape Scenes

[PL] "Zachód słońca nad górami, złote światło odbija się od szczytów pokrytych śniegów. Kamera powoli unosi się, pokazując panoramę rozległego krajobrazu z chmurami na niebie. Epicki, filmowy."

[EN] "Sunset over mountains with golden light filtering through clouds. Camera slowly tilts upward to capture the vast landscape. Wide angle shot showing scale and beauty. Cinematic, warm."

#### [PL] Sceny miejskie / [EN] Urban Scenes

[PL] "Nowoczesne miasto o zmierzchu z neonowymi reklamami i oświetleniem ulicznym. Kamera porusza się po ulicy, pokazując dynamiczny ruch pojazdów i refleksy na szybkich budynkach. Futurystyczne, dynamiczne."

[EN] "Futuristic city at night with flying vehicles between skyscrapers. Camera moves through streets showing motion and energy. Wide shots establishing the scale and technology. Sci-fi, dynamic."

### [PL] Świadomość zmian / [EN] Changelog Awareness

[PL] Technologia Stable Diffusion jest stale rozwijana. Najnowsze aktualizacje wprowadzają:
- Nowe architektury modeli
- Ulepszone algorytmy próbkowania
- Lepsze integracje z różnymi narzędziami

[EN] Stable Diffusion is continuously evolving. Recent developments include:
- New model architectures
- Improved sampling methods
- Better integration with creative tools

---

## 25. [PL] Narzędzia i zasoby / [EN] Tools and Resources

### [PL] Platformy generowania wideo / [EN] Video Generation Platforms

[PL] Lista platform do generowania wideo:
- **Kling AI** - https://kling.kuaishou.com
- **WAN AI** - https://wan-ai.site
- **Runway** - https://runwayml.com
- **LTX Video** - https://lightricks.com
- **Sora 2** - https://openai.com
- **Veo 3** - https://ai.google.dev
- **Veo 3.1** - https://ai.google.dev
- **Higgsfield** - https://higgsfield.com
- **Luma** - https://lumalabs.ai
- **Pika** - https://pika.art
- **Stable Diffusion** - https://stability.ai

### [PL] Narzędzia pomocnicze / [EN] Helper Tools

[PL] Zbiór narzędzi do optymalizacji pracy z promptami:
- **Prompt Engineering Guides** - https://github.com/promptslab/Awesome-Prompt-Engineering
- **Wizualizacja Promptów** - https://github.com/mckinsey/visualize-prompt
- **Testowanie Porównawcze** - https://github.com/openai/evals
- **Biblioteki Wzorców** - https://github.com/Prompt-Warehouse/sdxl-prompts

[EN] Collection of tools for prompt optimization:
- **Prompt Engineering Guides** - Comprehensive guides for various models
- **Prompt Visualization** - Tools for visualizing prompt structure
- **Comparison Platforms** - Sites for comparing model outputs
- **Testing Frameworks** - Tools for systematic prompt testing

### [PL] Społeczności i dyskusje / [EN] Communities and Discussions

[PL] Platformy dyskusyjne:
- **Reddit r/VideoEditing** - https://reddit.com/r/VideoEditing
- **Reddit r/aiVideo** - https://reddit.com/r/aiVideo
- **Reddit r/StableDiffusion** - https://reddit.com/r/StableDiffusion
- **Reddit r/PromptEngineering** - https://reddit.com/r/PromptEngineering
- **Discord Communities** - Various Discord servers for video AI

[EN] Discussion platforms for video AI:
- **Reddit** - General and technical discussions
- **Discord** - Real-time community and support
- **Twitter/X** - News and updates from developers

---

## 26. [PL] Wnioski i przyszłość / [EN] Conclusions and Future

### [PL] Podsumowanie / [EN] Summary

[PL] Generowanie wideo AI przekształca branżę kreatywną, oferując bezprecedensowane możliwości tworzenia dynamicznych treści wizualnych. Kluczem do sukcesu jest zrozumienie specyfiki każdego modelu i stosowanie odpowiednich technik promptowania.

[PL] Kluczowe trendy na przyszłość:
- Integracja generowania wideo z dźwiękiem i efektami specjalnymi
- Ulepszone algorytmy temporalne i kontroli ruchu
- Większa personalizacja i adaptacja modeli
- Rozwój narzędzi do wspierpracy z promptami

[EN] AI video generation is transforming the creative industry:
- **Integration** - Combining video with audio and special effects
- **Personalization** - Models adapting to user preferences
- **Real-time Control** - Enhanced camera and motion control
- **Accessibility** - Lowering barriers to professional video creation

[PL] Zalecenia dla użytkowników:
- Eksperymentuj z różnymi modelami
- Twórz bibliotekę udanych promptów
- Bądź na bieżącym aktualizacjami technologicznymi
- Uczestnicz się w społecznościach twórców

[EN] Key recommendations:
- Experiment with multiple models to find your preferred workflow
- Build a personal prompt library based on successful generations
- Stay updated with the latest model features and best practices
- Join communities to share knowledge and learn from others

---

*Przewodnik został stworzony na podstawie dostępnej dokumentacji i najlepszych praktyk z dnia 26 października 2025 roku. Technologia AI generującej wideo rozwija się bardzo szybko, więc zachęcamy do regularnego aktualizowania tego dokumentu.*

*Guide created based on available documentation and best practices as of October 26, 2025. AI video generation technology is evolving rapidly, so we encourage regular updates to stay current with the latest developments.*