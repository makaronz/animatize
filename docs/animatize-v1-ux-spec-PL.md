# ANIMAtiZE: Specyfikacja interfejsu V1 (PL)

Ten dokument definiuje koncepcję UX V1 dla ANIMAtiZE, narzędzia workflow do
generacji video AI, skoncentrowanego na spójności i podejściu intent-first.
Celem jest umożliwienie twórcom szybkiego przejścia od pomysłu do używalnej
sekwencji, przy jasnych kontrolach i minimalnym tarciu.

## Zakres

Specyfikacja V1 obejmuje tylko poniższe workflow:
- Tworzenie nowej sekwencji na podstawie obrazu i intencji.
- Konfigurację i uruchamianie generacji.
- Porównywanie wielu wyników.
- Historię, ulubione i regenerację jednym kliknięciem.

Wersja V1 nie obejmuje funkcji spekulatywnych, takich jak sterowanie głosem
czy współpraca w czasie rzeczywistym.

## Zasady UX i ograniczenia

Interfejs opiera się na następujących zasadach:
- Stosuj progressive disclosure, aby ograniczyć obciążenie poznawcze.
- Utrzymuj wygenerowany content w centrum uwagi.
- Zapewnij smart defaults i presety.
- Optymalizuj pod szybki pierwszy sukces.
- Utrzymuj kontrolki jako jawne, przewidywalne i odwracalne.

## Architektura informacji

Aplikacja powinna mieć prostą, zadaniową nawigację.

## Główna nawigacja

- `Create` (domyślny ekran startowy)
- `History`
- `Favorites`
- `Presets`
- `Settings`

## Struktura stron

- `Create`
  - Główna przestrzeń tworzenia (centrum)
  - Panel parametrów (prawa strona, zwijany)
  - Oś czasu generacji (dolna szuflada)
- `History`
  - Chronologiczna lista uruchomień z filtrami
  - Akcje w wierszu: otwórz, porównaj, regeneruj
- `Favorites`
  - Zapisane wyniki z szybkim porównaniem i regeneracją
- `Presets`
  - Presety systemowe i własne: szybkość, spójność, jakość
- `Settings`
  - Ustawienia domyślne, dostępność i preferencje konta

## 5 low-fidelity wireframeów (opis tekstowy)

Każdy wireframe jest celowo low-fidelity i skupiony na użyteczności.

## Wireframe 1: Workspace Create (empty state)

Layout:
- Górny pasek aplikacji z nawigacją i menu konta.
- Duży centralny drop zone obrazu (`Drop image or browse`).
- Pole `Intent` bezpośrednio pod drop zone, z podpowiedziami.
- Prawy panel parametrów zwinięty do paska podsumowania.
- Dolna szuflada timeline z placeholderem (`No generations yet`).

Główne akcje:
- Wgraj obraz.
- Wpisz intencję.
- Kliknij `Generate` (nieaktywne do czasu walidacji wymaganych pól).

Zachowanie stanu:
- Komunikat empty state tłumaczy minimalne kroki.
- Domyślnie zaznaczony preset `Cinematic balanced`.

## Wireframe 2: Setup i wykonanie (loading state)

Layout:
- Podgląd wgranego obrazu pozostaje centralnie.
- Sloty wyników pojawiają się jako karty ładowania (domyślnie 3 warianty).
- Prawy panel otwarty w trybie `Basic`:
  - Preset
  - Duration
  - Aspect ratio
  - Motion intensity
- Sekcja `Advanced` pozostaje zwinięta.

Główne akcje:
- Uruchom generację.
- Przerwij bieżące uruchomienie.
- Dostosuj parametry basic i ponów.

Zachowanie stanu:
- Pasek postępu per wariant z ETA.
- Bieżące uruchomienie od razu widoczne w timeline jako `Running`.

## Wireframe 3: Workspace wyników (success state)

Layout:
- Centrum pokazuje karty wyników z podglądem i metrykami.
- Prawy panel pokazuje użyte parametry i szybkie poprawki.
- Górny pasek podsumowania runu: ID, preset, czas, status.
- Dolny timeline przypina ostatni run do szybkiego powrotu.

Główne akcje:
- Otwórz szczegóły wyniku.
- Dodaj do ulubionych.
- Porównaj wybrane wyniki.
- Regeneruj z wybranego wyniku.

Zachowanie stanu:
- Toast sukcesu potwierdza gotowość.
- Nieudane warianty pozostają widoczne z akcją `Retry`.

## Wireframe 4: Panel porównania wyników

Layout:
- Widok side-by-side (`A | B`, opcjonalnie `C`).
- Wspólny scrubber do zsynchronizowanego odtwarzania.
- Chipy metryk: coherence, intent fidelity, motion quality.
- Prawy panel różnic parametrów.

Główne akcje:
- Wybierz zwycięzcę.
- Dodaj zwycięzcę do ulubionych.
- Regeneruj zwycięzcę po drobnych zmianach.

Zachowanie stanu:
- Porównanie można uruchomić z Create, History i Favorites.
- Na mobile V1 porównanie ograniczone do dwóch wariantów.

## Wireframe 5: History + Favorites timeline

Layout:
- Lewy panel filtrów:
  - Zakres dat
  - Status
  - Preset
  - Tylko ulubione
- Główna oś czasu grupowana po dniach/sesjach.
- Każdy wiersz: miniatura, fragment intencji, ustawienia, status.

Główne akcje:
- Otwórz run.
- Porównaj wyniki runu.
- Regeneruj jednym kliknięciem.
- Oznacz/odznacz ulubione.

Zachowanie stanu:
- Empty state kieruje użytkownika do `Create`.
- Wiersze błędów pokazują przyczynę i opcję ponowienia.

## Inwentarz komponentów

V1 powinno używać małego, spójnego zestawu komponentów wielokrotnego użycia.

## Inputy i pola

- Drop zone obrazu z fallbackiem file picker.
- Pole tekstowe `Intent` z przykładami i walidacją inline.
- Opcjonalne pole negative intent (tylko advanced).
- Edycja nazwy runu inline.

## Selektory i kontrolki

- Selektor presetów.
- Segmented control dla proporcji.
- Slider lub stepper czasu trwania.
- Selektor liczby wariantów (domyślnie 3).
- Selektor quality/speed.

## Karty

- Karta wyniku (preview, metryki, akcje).
- Karta runu (wiersz historii + status + szybkie akcje).
- Karta błędu (przyczyna, ścieżka retry).
- Karta empty state (prowadzenie onboardingowe).

## Timeline i compare

- Dolna szuflada timeline generacji.
- Pełna lista timeline w `History`.
- Viewer porównania ze zsynchronizowanym scrubberem.
- Chipy metryk i lista różnic parametrów.

## Kluczowe wzorce interakcji

Model interakcji ma minimalizować tarcie i utrzymywać kontekst.

1. Drag and drop obrazu z fallbackiem klawiaturowym i file picker.
2. One-click generate z domyślnego presetu.
3. Progressive disclosure w panelu parametrów (`Basic` przed `Advanced`).
4. One-click regenerate z kart wyników, historii i ulubionych.
5. Regeneracja zachowuje poprzednie ustawienia do czasu jawnej zmiany.
6. Toggle ulubionych dostępny we wszystkich widokach wyników.
7. Porównanie aktywne po zaznaczeniu co najmniej dwóch wyników.
8. Pętla tweak + rerun bezpośrednio z wybranego wyniku porównania.
9. Recoverable errors z jasną przyczyną i akcją `Retry`.
10. Skróty klawiszowe dla power userów (`G`, `C`, `F`, `R`) z widoczną pomocą.

## Zachowanie responsywne

Layout powinien pozostać task-first na wszystkich breakpointach.

- Desktop (`>=1200px`)
  - Układ 3-strefowy: centrum media, prawy panel parametrów, dolny timeline.
- Tablet (`768px-1199px`)
  - Layout center-first i zwijany side sheet parametrów.
  - Timeline jako dolny panel zakładkowy.
- Mobile (`<768px`)
  - Flow krokowy: Upload -> Intent -> Generate -> Compare.
  - Bottom sheets dla parametrów i akcji runu.
  - Compare ograniczony do dwóch wyników w V1.

Reguły touch i layout:
- Minimalny touch target: 44x44 px.
- Sticky obszar głównych akcji (`Generate`, `Regenerate`).
- Brak poziomego scrolla w głównych workflow.

## Checklist dostępności (WCAG AA)

V1 musi spełniać bazowe wymagania dostępności.

- Kontrast tekstu zgodny z WCAG AA (4.5:1 dla tekstu zwykłego, 3:1 dla dużego).
- Pełna nawigacja klawiaturą przez wszystkie kluczowe workflow.
- Widoczne focus indicators dla elementów interaktywnych.
- Dostępne nazwy i etykiety dla kontrolek oraz akcji medialnych.
- Drag and drop ma alternatywę niewskaźnikową.
- Postęp i status komunikowane przez ARIA live regions.
- Błędy są konkretne, naprawialne i powiązane z polami.
- Status i jakość nie są kodowane tylko kolorem.
- Ruch i animacje respektują `prefers-reduced-motion`.
- Zoom 200 procent zachowuje czytelność i operowalność.

## 10 ryzyk UX i mitigacje (V1)

Tabela skupia się na ryzykach obciążenia poznawczego i użyteczności.

| Ryzyko | Wpływ | Mitigacja |
|---|---|---|
| Przeciążenie parametrami na starcie | Wolny onboarding i niepewność | Domyślnie pokaż tylko 4 kontrolki basic. |
| Zbyt wiele wariantów wyników | Zmęczenie decyzyjne | Domyślnie 3 warianty, więcej tylko po świadomym wyborze. |
| Niejasne metryki jakości | Niskie zaufanie do wyniku | Proste etykiety i tooltipy z przykładami. |
| Utrata kontekstu między widokami | Tarcie nawigacyjne | Stałe podsumowanie runu i czytelne ścieżki powrotu. |
| Zapętlenie regeneracji | Strata czasu i kosztów | Rekomendacja zwycięzcy i sugestie kolejnego kroku. |
| Niewidoczny koszt i czas uruchomień | Frustracja użytkownika | Pokazuj estymację czasu przed startem i ponowieniem. |
| Nieprzejrzyste błędy | Odpływ użytkowników po porażce | Wyjaśnij przyczynę, fallback i `Retry` jednym kliknięciem. |
| Przeciążenie widoku compare | Wysokie obciążenie poznawcze | Limit porównania: 3 desktop, 2 mobile. |
| Bałagan w historii przy skali | Trudne wyszukiwanie runów | Grupowanie, filtry i zapisane widoki. |
| Regresje dostępności przy media-heavy UI | Wykluczenie i ryzyko prawne | Automatyczne i manualne bramki QA dostępności. |

## Kryteria sukcesu UX dla V1

Te rezultaty definiują skuteczność interfejsu V1.

- Skraca się czas do pierwszej udanej sekwencji.
- Użytkownicy kończą główny flow bez użycia advanced controls.
- Compare i regenerate są łatwo odkrywalne i szybkie.
- History i Favorites wspierają szybkie odtworzenie i ponowne użycie.
- Checklist dostępności przechodzi bez krytycznych błędów.

## Następne kroki

1. Zweryfikuj wireflowy z 5-8 reprezentatywnymi twórcami.
2. Przygotuj klikalny prototyp low-fidelity i wykonaj testy użyteczności.
3. Rozbij specyfikację na tickety implementacyjne per workflow.
