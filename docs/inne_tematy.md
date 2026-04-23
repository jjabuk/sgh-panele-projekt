# Alternatywne tematy projektów — regiony NUTS-2

Dane na poziomie NUTS-2 pozwalają na bardziej niszowe i analitycznie ciekawsze tematy niż sam PKB — zmienne są wtedy silniej i logiczniej powiązane.

---

## 1. Odporność rynku pracy na cyfryzację

**Pytanie badawcze:** Które regiony są najbardziej narażone na wzrost bezrobocia technologicznego?

| Element | Opis |
|---|---|
| Zmienna zależna | wysoka vs. niska dynamika zmian zatrudnienia w sektorach tradycyjnych |
| Zmienne objaśniające | odsetek pracujących w produkcji, udział usług wysokotechnologicznych, poziom kompetencji cyfrowych, wydatki firm na szkolenia |
| Sugerowana metoda | drzewa decyzyjne (ujawniają konkretne progi, np. edukacja cyfrowa > X → niższe ryzyko) |

---

## 2. Sukces zielonej transformacji

**Pytanie badawcze:** Które regiony skutecznie redukują emisje bez utraty dynamiki gospodarczej?

| Element | Opis |
|---|---|
| Zmienna zależna | region „Eco-Leader" (spadek emisji przy wzroście produkcji) vs. „Laggard" |
| Zmienne objaśniające | udział energii odnawialnej, inwestycje w ochronę środowiska, gęstość zaludnienia, liczba zarejestrowanych aut elektrycznych |
| Sugerowana metoda | sieci neuronowe (nieliniowe zależności między ekologią a przemysłem) |

---

## 3. Pułapka demograficzna

**Pytanie badawcze:** Które regiony są zagrożone wyludnieniem i drenażem mózgów?

| Element | Opis |
|---|---|
| Zmienna zależna | region stabilny demograficznie vs. region wymierający |
| Zmienne objaśniające | mediana wieku, wskaźnik migracji wewnętrznej, liczba studentów na 1000 mieszkańców, dostępność żłobków, ceny mieszkań |
| Sugerowana metoda | Random Forest (pozwala ocenić, co bardziej wpływa na decyzje młodych — praca czy jakość usług społecznych) |

---

## Porównanie tematów

| Temat | Łatwość obrony | Nowoczesność | Dostępność danych |
|---|---|---|---|
| Odporność na cyfryzację | średnia | wysoka | dobra |
| Zielona transformacja | średnia | bardzo wysoka | dobra |
| Pułapka demograficzna | wysoka | średnia | bardzo dobra |
