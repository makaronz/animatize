# ANIMAtiZE: Minimum viable design system v1 (PL)

Ten dokument definiuje minimalny, wdrażalny design system (MVDS) dla ANIMAtiZE.
Przekłada specyfikację UX na system, który można realnie adoptować w designie i
frontendzie, z jasnym ownership, metrykami sukcesu i planem ewolucji.

Dokument jest zgodny z:
- `/Users/arkadiuszfudali/Git/animatize/docs/animatize-v1-ux-spec-PL.md`
- `/Users/arkadiuszfudali/Git/animatize/docs/animatize-product-vision-prfaq-PL.md`

## 1) Dlaczego system teraz

ANIMAtiZE ma już wystarczająco dużo powtarzalnych wzorców UX, aby uzasadnić
inwestycję w lekki system. Celem V1 nie jest estetyczna perfekcja. Celem jest
przewidywalna szybkość dostarczania, spójne zachowanie interfejsu i mniejsze
obciążenie poznawcze użytkownika.

## 2) Zakres V1 i non-goals

### In-scope

- Fundament tokenów: kolor, typografia, spacing, radius, shadow, motion,
  breakpoints i z-index.
- Biblioteka komponentów kluczowych dla czterech workflow V1.
- Kontrakty stanów i dostępności wspólne dla wszystkich komponentów.
- Governance, polityka wydań i metryki adopcji.

### Out-of-scope

- Pełna platforma multi-brand klasy enterprise.
- Eksperymenty wizualne bez wpływu na cele produktowe.
- Nadmiernie złożone silniki zmiennych ponad potrzeby V1.

## 3) Zasady systemowe

1. Intent-first clarity zamiast złożonej konfiguracji.
2. Wygenerowany content zawsze pozostaje centralny wizualnie.
3. Progressive disclosure jako domyślny mechanizm.
4. Komponenty mają uczyć sposobu użycia przez strukturę i domyślne wartości.
5. Decyzje systemowe muszą poprawiać jednocześnie spójność i szybkość.

## 4) Architektura tokenów

MVDS używa trójwarstwowego modelu tokenów.

### 4.1 Warstwy tokenów

- `reference`: surowe skale i prymitywy.
- `semantic`: mapowanie znaczeń UX do ról.
- `component`: aliasy lokalne dla zachowań komponentu.

### 4.2 Konwencja nazewnictwa

Stosuj stabilne nazewnictwo z notacją kropkową:
- `ref.<kategoria>.<skala>`
- `sem.<domena>.<rola>`
- `cmp.<komponent>.<slot>.<stan>`

Przykłady:
- `ref.color.neutral.900`
- `sem.text.primary`
- `cmp.button.primary.bg.default`

### 4.3 Zestaw tokenów bazowych (V1)

| Kategoria | Przykładowe tokeny | Wymagalność V1 |
|---|---|---|
| Kolor | `ref.color.*`, `sem.bg.*`, `sem.text.*`, `sem.border.*` | Wymagane |
| Typografia | `ref.type.size.*`, `ref.type.weight.*`, `sem.type.*` | Wymagane |
| Spacing | `ref.space.0` do `ref.space.12` | Wymagane |
| Radius | `ref.radius.none/sm/md/lg/xl/pill` | Wymagane |
| Shadow | `ref.shadow.xs/sm/md/lg` | Wymagane |
| Motion | `ref.motion.duration.*`, `ref.motion.easing.*` | Wymagane |
| Breakpoints | `ref.bp.sm/md/lg/xl` | Wymagane |
| Z-index | `ref.z.base/overlay/modal/toast` | Wymagane |

### 4.4 Rekomendowane skale bazowe

Skala spacing (px): `0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64`

Skala typograficzna (size/line-height):
- `12/16`, `14/20`, `16/24`, `18/26`, `20/28`, `24/32`, `30/38`

Czasy motion (ms):
- `80` (mikro), `140` (domyślny), `220` (złożony), `320` (panel i drawer)

Breakpoints:
- `sm: 640`, `md: 768`, `lg: 1200`, `xl: 1440`

### 4.5 Przykład formatu tokenów

```json
{
  "ref": {
    "color": {
      "neutral": { "0": "#FFFFFF", "900": "#0B1020" },
      "brand": { "500": "#3B82F6", "600": "#2563EB" },
      "success": { "500": "#16A34A" },
      "danger": { "500": "#DC2626" }
    },
    "space": { "0": 0, "1": 2, "2": 4, "3": 8, "4": 12, "5": 16 }
  },
  "sem": {
    "bg": { "canvas": "{ref.color.neutral.0}", "panel": "#F7F9FC" },
    "text": { "primary": "{ref.color.neutral.900}", "muted": "#4B5563" },
    "border": { "default": "#D1D5DB", "focus": "{ref.color.brand.500}" }
  }
}
```

## 5) Kierunek wizualny i tematy

ANIMAtiZE V1 ma unikać generycznego flat designu. Interfejs powinien być
precyzyjny, filmowy i lekko przestrzenny, bez utraty czytelności.

### Reguły wizualne V1

- Utrzymuj wysoki kontrast między sceną contentu a powierzchniami kontroli.
- Stosuj subtelną głębię (shadow + hierarchy warstw) do separacji obszarów.
- Kolor brandowy zachowaj dla akcji priorytetowych i kluczowych statusów.
- Motion ma komunikować zmianę stanu, nie dekorować.

### Strategia tematów

- Najpierw dostarcz motyw jasny.
- Motyw ciemny dopiero po pełnej parytecie tokenów i dostępności.

## 6) Kontrakt biblioteki komponentów V1

Tabela definiuje komponenty system-owned i minimalne kontrakty.

| Komponent | Cel | Wymagane warianty | Wymagane stany | Minimum dostępności |
|---|---|---|---|---|
| `AppShell` | Globalny szkielet layoutu | Desktop, tablet, mobile | Default | Landmarks, skip link |
| `TopNav` | Główna nawigacja | Standard, compact | Default, focus | Nawigacja klawiaturą |
| `SidePanel` | Obszar parametrów | Collapsed, expanded | Default, loading | Focus trap przy modalizacji |
| `BottomDrawer` | Kontener timeline | Collapsed, expanded | Default, dragging | Klawiaturowe open/close |
| `DropZone` | Upload obrazu | Idle, drag-over | Empty, error, success | Alternatywa bez wskaźnika |
| `IntentInput` | Edycja intencji | Single-line, multi-line | Default, error | Label, helper, powiązanie błędu |
| `PresetSelector` | Wybór presetu | List, segmented | Default, disabled | Nawigacja strzałkami |
| `SegmentedControl` | Przełączniki aspektu i trybu | 2-4 opcje | Selected, disabled | Semantyka `aria-pressed` |
| `DurationControl` | Sterowanie czasem | Slider, stepper | Default, error | Krokowanie klawiaturą |
| `ResultCard` | Preview i akcje wyniku | Compact, full | Loading, success, failed, favorited | Etykiety akcji i focus order |
| `RunCard` | Wiersz historii | Compact, detailed | Running, failed, success | Odczyt statusu |
| `StatusBadge` | Etykiety stanu | Neutral, success, warning, error | Default | Tekst + kolor |
| `Timeline` | Chronologia uruchomień | Grouped, flat | Empty, loading | Logiczny porządek odczytu |
| `CompareViewer` | Analiza side-by-side | 2-up, 3-up | Loading, ready | Obsługa scrubbera klawiaturą |
| `MetricChip` | Wskaźniki jakości | Info, positive, warning | Default | Ikona + tekst |
| `Toast` | Komunikat chwilowy | Info, success, warning, error | Enter, exit | Live region i dismiss |

## 7) Wspólna macierz stanów

Każdy komponent V1 musi wspierać wspólny model stanów.

| Stan | Traktowanie wizualne | Zachowanie interakcji | Wymagana semantyka |
|---|---|---|---|
| Empty | Placeholder z prowadzeniem | Widoczne główne CTA | Instrukcja dla użytkownika |
| Loading | Skeleton lub progress | Ograniczone akcje wtórne | Komunikacja postępu |
| Success | Pozytywne potwierdzenie | Widoczny kolejny krok | Etykieta sukcesu |
| Error | Czytelna powierzchnia błędu | Widoczna ścieżka naprawy | Rola błędu i mapowanie pól |
| Disabled | Ograniczony kontrast | Brak interakcji | Programowe disabled |
| Focused | Kontrastowa obwódka | Widoczny focus klawiaturowy | Wskaźnik focusu |

## 8) Prymitywy interakcji i motion

### Prymitywy interakcji

- Drag and drop z jawnym fallbackiem click-to-upload.
- One-click regenerate z zachowaniem ustawień.
- Progressive disclosure dla advanced controls.
- Przejścia między Create, Compare i History bez utraty kontekstu.

### Prymitywy motion

- Mikro feedback: `80-140ms`.
- Przejścia paneli i drawerów: `220-320ms`.
- Domyślne easing:
  - Wejście: `ease-out`.
  - Wyjście: `ease-in`.
- Wymagana obsługa `prefers-reduced-motion`.

## 9) Baseline dostępności i bramki QA

### Baseline dostępności (WCAG AA)

- Kontrast tekstu >=4.5:1 dla tekstu zwykłego.
- Pełna operowalność klawiaturą dla kluczowych workflow.
- Etykiety screen reader dla wszystkich akcji.
- Status nie może być kodowany wyłącznie kolorem.
- Zoom 200 procent bez utraty funkcji.

### Wymagane bramki QA przed wydaniem

1. Skan automatyczny a11y bez błędów krytycznych.
2. Manualny keyboard walkthrough dla Create, Compare, History.
3. Smoke test czytnikiem ekranu dla statusów i błędów.
4. Testy responsive na desktop, tablet i mobile.

## 10) Governance i model operacyjny

### Ownership

- Product owner design systemu: Product Design lead.
- Engineering owner design systemu: Frontend lead.
- Owner dostępności: QA lead lub UX quality lead.

### Workflow kontrybucji

1. Otwórz issue z propozycją zmiany systemowej.
2. Dołącz dowody użycia z ekranów workflow.
3. Przejdź review design + frontend.
4. Wdroż aktualizacje tokenów i komponentów.
5. Opublikuj release notes i guidance migracyjne.

### Polityka wydań

- SemVer dla kontraktów komponentów.
- Patch: poprawki wizualne i bugfixy bez zmian API.
- Minor: dodatki kompatybilne wstecz.
- Major: zmiany łamiące z planem migracji.

### Polityka deprecacji

- Komponent oznaczony jako deprecated przez dwie wersje minor.
- Przed usunięciem wymagany codemod lub przewodnik migracyjny.

## 11) Model adopcji i metryki sukcesu

Adopcja musi być mierzona i powiązana z szybkością dostarczania oraz jakością.

| Metryka | Definicja | Baseline | Target 90 dni |
|---|---|---:|---:|
| Reuse komponentów | Udział nowych ekranów opartych o MVDS | Do pomiaru | >=80% |
| Compliance tokenów | Udział styli opartych o tokeny | Do pomiaru | >=90% |
| Defekty niespójności UI | Błędy wynikające z driftu stylu/zachowania | Do pomiaru | -40% |
| Czas budowy ekranu workflow | Czas implementacji end-to-end | Do pomiaru | -25% |
| Krytyczne defekty a11y | Błędy krytyczne dostępności | Do pomiaru | 0 |
| First-pass UX QA pass rate | Ekrany przechodzące QA bez reworku | Do pomiaru | >=75% |

## 12) Plan rolloutu

### Faza 0 (tydzień 1): setup

- Zatwierdź nazewnictwo tokenów i skale.
- Utwórz strukturę repo dla tokenów i dokumentacji.
- Potwierdź ownership i proces review.

### Faza 1 (tygodnie 2-3): fundamenty

- Zaimplementuj bazowy zestaw tokenów.
- Zbuduj `AppShell`, `TopNav`, `SidePanel`, `BottomDrawer`.
- Zweryfikuj baseline responsive i dostępności.

### Faza 2 (tygodnie 4-6): komponenty workflow

- Zbuduj komponenty dla workflow Create.
- Zbuduj `ResultCard`, `Timeline`, `CompareViewer`.
- Zintegruj z ekranami History i Favorites.

### Faza 3 (tygodnie 7-8): hardening

- Wykonaj regresję usability i dostępności.
- Zmierz KPI adopcji i trend defektów.
- Opublikuj release `v1.0.0` MVDS i guide użycia.

## 13) Definition of done dla komponentów MVDS

Komponent jest gotowy dopiero po spełnieniu wszystkich warunków.

- Wszystkie style oparte na tokenach.
- Wdrożone wymagane warianty i stany.
- Zweryfikowana dostępność.
- Udokumentowane i przetestowane zachowanie klawiaturą.
- Opisane przykłady użycia i antywzorce.
- Opublikowany wpis w changelogu i tag wersji.

## 14) Najbliższe kroki

1. Zatwierdź zakres MVDS i ownerów.
2. Utwórz pakiet tokenów i starter package komponentów.
3. Zaplanuj komponenty P0 do pierwszego sprintu wdrożeniowego.
