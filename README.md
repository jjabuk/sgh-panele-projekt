# Projekt: Zielona Transformacja Polski - Analiza Regionalna

Analiza wpływu wydatków środowiskowych na emisje CO2 w regionach NUTS2 Polski w latach 2008-2024.

## Dane
- **BDL API** - dane lokalne polskie (wydatki, OZE, energia)
- **Eurostat** - dane europejskie (PKB, bezrobocie, populacja)
- **EDGAR** - dane emisji CO2 z Unii Europejskiej

## Wymagania
```bash
pip install pandas numpy requests eurostat matplotlib
pip install openpyxl
```

## Struktura
- `main.py` - skrypt główny
- `main2.ipynb` - notebook analityczny z pełną analizą
- `panel_zielona_transformacja_nuts2_PL.csv` - finalna baza danych

## Uruchomienie
```bash
python main.py
# lub
jupyter notebook main2.ipynb
```
