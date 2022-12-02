from iscooking.common import getTable
from datetime import timedelta
import pygsheets
from pygsheets import Cell, DataRange, Address, FormatType

WEEKDAYS = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]

START_ROW = 3
HEADER_ROW = START_ROW + 5

def batchUpdate(sheet, values):
    request = list(values.items())
    sheet.update_values_batch([(x[0], x[0]) for x in request], [[[x[1]]] for x in request], parse=True)

def addDayHeader(sheet, name):
    sumPrice = "+".join(Address((6, i * 8 + 6)).label for i in range(10))
    return {
        "A1": "Jídelníček",
        "B1": name,
        "E1": "Cena za den:",
        "F1": f"={sumPrice}"
    }

def addMealPrice(sheet, offset):
    priceCell = sheet.cell((START_ROW + 3, offset + 6))
    priceCell.set_number_format(FormatType.NUMBER, "####0 Kč")
    priceCell.wrap_strategy = "OVERFLOW_CELL"
    sheet.merge_cells((START_ROW + 3, offset + 6), (START_ROW + 3, offset + 7))
    priceCell = sheet.cell((START_ROW + 4, offset + 6))
    priceCell.set_number_format(FormatType.NUMBER, "####0 Kč")
    priceCell.wrap_strategy = "OVERFLOW_CELL"
    sheet.merge_cells((START_ROW + 4, offset + 6), (START_ROW + 4, offset + 7))
    return {
        (START_ROW + 3, offset + 5): "Cena",
        (START_ROW + 3, offset + 6): f'=SUM({Address((HEADER_ROW + 1, offset + 5)).label}:{Address((HEADER_ROW + 51, offset + 5)).label})',
        (START_ROW + 4, offset + 5): "Na porci",
        (START_ROW + 4, offset + 6): f'={Address((START_ROW + 3, offset + 6)).label} / {Address((START_ROW + 2, offset + 2)).label}',
    }

def addMealWeight(sheet, offset):
    weightCell = sheet.cell((START_ROW + 3, offset + 2))
    weightCell.set_number_format(FormatType.NUMBER, "####0.0 kg")
    weightCell.wrap_strategy = "OVERFLOW_CELL"
    sheet.merge_cells((START_ROW + 3, offset + 2), (START_ROW + 3, offset + 3))
    weightCell = sheet.cell((START_ROW + 4, offset + 2))
    weightCell.set_number_format(FormatType.NUMBER, "###0 g")
    weightCell.wrap_strategy = "OVERFLOW_CELL"
    sheet.merge_cells((START_ROW + 4, offset + 2), (START_ROW + 4, offset + 3))
    return {
        (START_ROW + 3, offset + 1): "Hmoty:",
        (START_ROW + 3, offset + 2): f'=SUM({Address((HEADER_ROW + 1, offset + 6)).label}:{Address((HEADER_ROW + 51, offset + 6)).label})',
        (START_ROW + 4, offset + 1): "Na porci",
        (START_ROW + 4, offset + 2): f'={Address((START_ROW + 3, offset + 2)).label} / {Address((START_ROW + 2, offset + 2)).label} * 1000',
    }

def addMealLayout(sheet, offset, name):
    changes = {
        (START_ROW, offset + 1): name,
        (START_ROW + 1, offset + 1): "<název jídla>",
        (START_ROW + 2, offset + 1): "Porcí:",
        (START_ROW + 2, offset + 2): "42",

        (HEADER_ROW, offset + 1): "Co",
        (HEADER_ROW, offset + 2): "Kolik",
        (HEADER_ROW, offset + 4): "Jednotková cena",
        (HEADER_ROW, offset + 5): "Cena",
        (HEADER_ROW, offset + 6): "Hmotnost",
        (HEADER_ROW, offset + 7): "Nákup"
    }

    changes.update(addMealPrice(sheet, offset))
    changes.update(addMealWeight(sheet, offset))

    for i in range(50):
        changes[(HEADER_ROW + i + 1, offset + 3)] = f'=IFERROR(VLOOKUP({Address((HEADER_ROW + i + 1, offset + 1)).label};Suroviny!A1:D5000;2;FALSE))'
        changes[(HEADER_ROW + i + 1, offset + 4)] = f'=IFERROR(VLOOKUP({Address((HEADER_ROW + i + 1, offset + 1)).label};Suroviny!A1:D5000;4;FALSE))'
        sum = f'({Address((HEADER_ROW + i + 1, offset + 2)).label}*{Address((HEADER_ROW + i + 1, offset + 4)).label})'
        changes[(HEADER_ROW + i + 1, offset + 5)] = f'=IF({sum} = 0; ""; {sum})'
        changes[(HEADER_ROW + i + 1, offset + 6)] = f'=IFERROR({Address((HEADER_ROW + i + 1, offset + 2)).label} * VLOOKUP({Address((HEADER_ROW + i + 1, offset + 1)).label};Suroviny!A1:D5000;3;FALSE))'

    sheet.add_conditional_formatting(
        Address((HEADER_ROW + 1, offset + 1)).label,
        Address((HEADER_ROW + 50, offset + 1)).label,
        condition_type="CUSTOM_FORMULA",
        condition_values=[f'=AND(NOT(ISBLANK({Address((HEADER_ROW + 1, offset + 1)).label})); ISBLANK({Address((HEADER_ROW + 1, offset + 4)).label}))'],
        format={'backgroundColor':{'red':234 / 255, 'green': 153/ 255, 'blue': 153 / 255}} )

    header = sheet.cell((START_ROW, offset + 1))
    header.set_text_format("bold", True)
    header.set_horizontal_alignment(pygsheets.custom_types.HorizontalAlignment.CENTER)
    header.set_vertical_alignment(pygsheets.custom_types.VerticalAlignment.MIDDLE)
    header.color = (249 / 255, 203 / 255, 156 / 255)

    meal = sheet.cell((START_ROW + 1, offset + 1))
    meal.set_text_format("bold", True)

    labels = DataRange((HEADER_ROW, offset + 1), (HEADER_ROW, offset + 7), sheet)
    labelsTemplate = Cell("A1").set_text_format("bold", True)
    labelsTemplate.color = (159 / 255, 197 / 255, 232 / 255)
    labels.apply_format(labelsTemplate)

    sheet.merge_cells((START_ROW, offset + 1), (START_ROW, offset + 7))
    sheet.merge_cells((START_ROW + 1, offset + 1), (START_ROW + 1, offset + 7))
    sheet.adjust_column_width(offset + 2, pixel_size=35)
    sheet.adjust_column_width(offset + 3, pixel_size=40)
    sheet.adjust_column_width(offset + 4, offset + 6, pixel_size=60)
    sheet.adjust_column_width(offset + 7, pixel_size=50)
    sheet.adjust_column_width(offset + 8, pixel_size=30)

    return changes, 8

def populateDay(sheet, title):
    print(f"Populating {title}")

    sheet.spreadsheet.client.set_batch_mode(True)

    changes = {}

    changes.update(addDayHeader(sheet, title))
    offset = 0
    for meal in ["Snídaně", "Oběd", "Večeře", "Svačina"]:
        ch, off = addMealLayout(sheet, offset, meal)
        changes.update(ch)
        offset += off

    sheet.spreadsheet.client.run_batch()
    sheet.spreadsheet.client.set_batch_mode(False)
    batchUpdate(sheet, changes)
    print(f"Done {title}")

def populateIngredients(sheet):
    changes = {
        "A1": "Název",
        "B1": "Jednotka",
        "C1": "Hmotnost jednotky",
        "D1": "Jednotková cena",
        "E1": "Sekce"
    }
    row = 1
    def push(name, unit, weight, price, section):
        nonlocal row
        row += 1
        changes.update({
            f"A{row}": name,
            f"B{row}": unit,
            f"C{row}": weight,
            f"D{row}": price,
            f"E{row}": section
        })

    push("voda", "l", 1, 0, "-")
    push("mouka", "kg", 1, 15, "TRVANLIVÉ")
    push("vejce", "ks", 0.03, 4, "CHLAZENÉ")

    batchUpdate(sheet, changes)


def setupTable(id, start, end):
    table = getTable(id)

    # originalSheets = table.worksheets()
    # for w in originalSheets[1:]:
    #     table.del_worksheet(w)
    # originalSheets[0].title = "TO_DELETE"

    ing = table.add_worksheet(title="Suroviny", rows=500, cols=7)
    populateIngredients(ing)

    table.add_worksheet(title="Útrata", rows=500, cols=7)
    # table.del_worksheet(originalSheets[0])

    days = [start + timedelta(days=x) for x in range((end-start).days)]
    for i, day in enumerate(days):
        title = f"{WEEKDAYS[day.weekday()]} ({day.day}.{day.month})"
        w = table.add_worksheet(title=title, rows=100, cols=50, index=i)
        populateDay(w, title)


