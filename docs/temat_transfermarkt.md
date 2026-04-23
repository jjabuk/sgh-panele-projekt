---
format:
  typst:
    # toc: true
    # toc-depth: 2
    # number-sections: true
    margin:
      x: 1in
      y: 1in
    fontsize: 9pt
    papersize: a4
    columns: 1

    fig-format: png
    monofont: 'Fira Code'
    sansfont: 'Open Sans'
    mainfont: 'Helvetica Neue'
---

# Transfermarkt

Źródło danych: <https://github.com/dcaribou/transfermarkt-datasets>

## Opis zbioru

Jest to automatycznie aktualizowany zbiór danych piłkarskich oparty na danych z serwisu Transfermarkt.

Zbiór obejmuje ponad 79 tys. meczów, 37 tys. piłkarzy oraz 1,8 mln występów i jest odświeżany co tydzień.

W najnowszej wersji uwzględniono także dane o piłce reprezentacyjnej. Oznacza to, że w zbiorze znajdują się informacje o państwach, reprezentacjach narodowych, meczach turniejów reprezentacyjnych oraz o liczbie występów i goli reprezentacyjnych zawodników.

## Co zawiera zbiór

Zbiór składa się z 12 tabel obejmujących rozgrywki, mecze, kluby, zawodników, występy, wyceny zawodników, dane klubowe dla meczów, zdarzenia meczowe, składy, transfery, państwa i reprezentacje narodowe. Tabele zawierają identyfikatory, które pozwalają łączyć dane między obiektami.

| Tabela              | Opis                                                                   | Skala      |
| ------------------- | ---------------------------------------------------------------------- | ---------- |
| `competitions`      | Ligi, turnieje i rozgrywki reprezentacyjne                             | 40+        |
| `clubs`             | Informacje o klubach, wielkości kadry i wartości rynkowej              | 400+       |
| `players`           | Profile zawodników, pozycje, wartości rynkowe, występy reprezentacyjne | 37 000+    |
| `games`             | Wyniki meczów, składy, frekwencja                                      | 79 000+    |
| `appearances`       | Jeden wiersz na zawodnika i mecz, w którym wystąpił                    | 1 800 000+ |
| `player_valuations` | Historyczne wyceny rynkowe zawodników                                  | 500 000+   |
| `club_games`        | Ujęcie meczu z perspektywy klubu                                       | 150 000+   |
| `game_events`       | Gole, kartki, zmiany                                                   | 1 100 000+ |
| `game_lineups`      | Wyjściowe składy i ławki rezerwowych                                   | 2 800 000+ |
| `transfers`         | Transfery zawodników pomiędzy klubami                                  | 87 000+    |
| `countries`         | Informacje o krajach i konfederacjach                                  | 100+       |
| `national_teams`    | Profile reprezentacji, wielkość kadry, ranking FIFA                    | 100+       |

## Propozycje problemów modelowych

Poniżej znajduje się kilka propozycji pytań badawczych, które dobrze pasują do założeń projektu data mining. Wszystkie można modelować przy użyciu drzew decyzyjnych, modeli zespołowych opartych na drzewach oraz sieci neuronowych.

### 1. Czy i w jakim stopniu gra w reprezentacji jest związana z wartością rynkową zawodnika?

To najbardziej naturalna propozycja, jeśli chcesz połączyć wątek sportowy i ekonomiczny. Metodologicznie najlepiej interpretować ją jako badanie związku i siły predykcyjnej, a nie czystego wpływu przyczynowego.

- Zmienna objaśniana `y`:
  - `wartosc_rynkowa_eur`
- Typ zadania: regresja
- Kluczowe zmienne objaśniające:
  - `liczba_wystepow_reprezentacyjnych`,
  - `liczba_goli_reprezentacyjnych`,
  - `aktualna_reprezentacja_id`,
  - `czy_reprezentant`,
  - `mecze_reprezentacyjne_12m`,
  - `minuty_w_reprezentacji_12m`
- Dodatkowe zmienne kontrolne:
  - `wiek_zawodnika_lata`,
  - `pozycja_glowna`,
  - `liczba_minut_sezon`,
  - `gole_na_90_minut`,
  - `asysty_na_90_minut`,
  - `wartosc_klubu_eur`,
  - `poziom_rozgrywek`,
  - `trend_wartosci_rynkowej_12m`

### 2. Czy i w jakim stopniu wartość rynkowa zawodnika jest związana z prawdopodobieństwem gry w reprezentacji?

To podobne pytanie, ale z odwróconą logiką modelowania. Tutaj wartość rynkowa jest jedną z głównych zmiennych objaśniających, a celem jest przewidywanie powołania albo występu w reprezentacji.

- Zmienna objaśniana `y`:
  - `czy_wystep_w_reprezentacji_w_12m` albo
  - `czy_powolanie_do_reprezentacji`
- Typ zadania: klasyfikacja binarna
- Kluczowe zmienne objaśniające:
  - `wartosc_rynkowa_eur`,
  - `trend_wartosci_rynkowej_12m`,
  - `zmiana_wartosci_rynkowej_6m_proc`
- Inne interesujące zmienne objaśniające:
  - `wiek_zawodnika_lata`,
  - `pozycja_glowna`,
  - `liczba_minut_sezon`,
  - `gole_na_90_minut`,
  - `asysty_na_90_minut`,
  - `udzial_meczow_w_pierwszym_skladzie`,
  - `wartosc_klubu_eur`,
  - `ranking_fifa_reprezentacji`

### 3. Czy i w jakim stopniu profil sportowy zawodnika wyjaśnia jego wartość rynkową?

To szersza i bardzo bezpieczna projektowo wersja problemu regresyjnego. Pozwala badać, które cechy sportowe i karierowe najmocniej wiążą się z wyceną zawodnika.

- Zmienna objaśniana `y`:
  - `wartosc_rynkowa_eur`
- Typ zadania: regresja
- Kluczowe zmienne objaśniające:
  - `wiek_zawodnika_lata`,
  - `pozycja_glowna`,  
  - `liczba_minut_sezon`,
  - `liczba_goli_sezon`,
  - `liczba_asyst_sezon`,
  - `gole_na_90_minut`,
  - `asysty_na_90_minut`
- Inne interesujące zmienne objaśniające:
  - `udzial_w_golach_na_90_minut`,
  - `udzial_meczow_w_pierwszym_skladzie`,
  - `liczba_wystepow_reprezentacyjnych`,
  - `wartosc_klubu_eur`,
  - `miejsce_klubu_w_tabeli`,
  - `procent_wygranych_klubu`,
  - `dni_od_ostatniego_transferu`

### 4. Czy i w jakim stopniu historia transferowa zawodnika jest związana z jego obecną wartością rynkową?

To ciekawy problem, bo łączy komponent sportowy z rynkowym. Można badać, czy częstotliwość transferów, opłaty transferowe i stabilność kariery są związane z obecną ceną zawodnika.

- Zmienna objaśniana `y`:
  - `wartosc_rynkowa_eur`
- Typ zadania: regresja
- Kluczowe zmienne objaśniające:
  - `liczba_transferow_w_karierze`,
  - `oplata_ostatniego_transferu_eur`,
  - `dni_od_ostatniego_transferu`,
  - `staz_w_aktualnym_klubie_dni`
- Inne interesujące zmienne objaśniające:
  - `wiek_zawodnika_lata`,
  - `pozycja_glowna`,
  - `liczba_minut_sezon`,
  - `gole_na_90_minut`,
  - `wartosc_klubu_eur`,
  - `poziom_rozgrywek`,
  - `liczba_wystepow_reprezentacyjnych`

### 5. Czy i w jakim stopniu bieżąca forma zawodnika pozwala przewidzieć jego miejsce w pierwszym składzie?

To propozycja bardziej taktyczna niż rynkowa, ale bardzo dobrze nadaje się do klasyfikacji i do porównania różnych modeli predykcyjnych.

- Zmienna objaśniana `y`: 
  - `czy_pierwszy_sklad`
- Typ zadania: klasyfikacja binarna
- Kluczowe zmienne objaśniające: 
  - `liczba_minut_sezon`, 
  - `srednia_minut_na_mecz`, 
  - `gole_na_90_minut`, 
  - `asysty_na_90_minut`, 
  - `liczba_kartek_zoltych_sezon`
- Inne interesujące zmienne objaśniające: 
  - `pozycja_glowna`, 
  - `wiek_zawodnika_lata`, 
  - `udzial_meczow_w_pierwszym_skladzie`, 
  - `procent_wygranych_klubu`, 
  - `miejsce_klubu_w_tabeli`, 
  - `staz_w_aktualnym_klubie_dni`
