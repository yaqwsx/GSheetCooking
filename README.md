# GSpreadCooking

English TLDR: Tooling to generate cooking and shopping lists for cooking at
events organized by InstruktoriBrno.

# Google tabulky jako jídelníček pro vaření

[Ukázkový jídelníček](https://docs.google.com/spreadsheets/d/163tgeG5d46xNGNdxJ9Oh2tIOZ-LNej2ZlVy3bEYCuYw/edit?usp=sharing)

Instaluje se pomocí:

```
pip install git+https://github.com/yaqwsx/GSheetCooking.git@master
```

Poté je možné používat příkaz `iscooking`. Standardní použití je následující:

- založ prázdnout tabulku
- zavolej `iscooking setup <ID tabulky> --start <date> --end <date>`
- to vygeneruje šablonu tabulky. Do listu `suroviny` zadávej suroviny, v listech
  dnech poté jen vyplňuj co a kolik. Zbytek se doplní sám.
- do sloupce nákup je možné poznačit název nákupu.
- pomocí `iscooking shopping <ID tabulky> <název nákupu>` můžeš vygenerovat
  nákupní seznam.
- do nákupního seznamu je možné zadat kolik které suroviny už mám
- v nákupním seznamu je možné odškrtávat již nakoupené položky.
