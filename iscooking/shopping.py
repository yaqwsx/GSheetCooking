from .common import getTable
from dataclasses import dataclass
from pygsheets import Cell, DataRange, Address, FormatType

def toFloat(str):
    if len(str) == 0:
        return 0
    return float(str.replace(",", "."))


@dataclass
class Type:
    name: str
    unit: str
    unitPrice: float
    section: str

@dataclass
class ShoppingItem:
    type: Type
    recipe: str
    amount: float
    shopping: str

def getRecipeSheets(table):
    sheets = []
    for s in table.worksheets():
        if s.cell("A1").value == "Jídelníček":
            sheets.append(s)
    return sheets

def collectTypes(table):
    return {row[0]: Type(row[0], row[1], toFloat(row[3]), row[4])
         for row in table.worksheet_by_title("Suroviny").get_all_values()[1:]
         if len(row[0]) > 0}

def extractRecipeItems(data, offset, types):
    rOffset = 8 * offset
    meal = data[3][rOffset].split('\n')[0]
    return [
        ShoppingItem(types[row[0 + rOffset]], meal, toFloat(row[1 + rOffset]), row[6 + rOffset])
        for row in data[8:] if len(row[0 + rOffset]) > 0
    ]

def collectShoppingItems(table):
    types = collectTypes(table)
    items = []
    for r in getRecipeSheets(table):
        data = r.get_all_values()
        for i in range(5):
            items += extractRecipeItems(data, i, types)
    return items

def groupShoppingItems(items):
    groups = {}
    for item in items:
        group = groups.get(item.type.section, {})
        t = group.get(item.type.name, [])
        t.append(item)
        group[item.type.name] = t
        groups[item.type.section] = group
    return groups

def fillShoppingTable(sheet, groups):
    sheet.spreadsheet.client.set_batch_mode(True)

    sheet.adjust_column_width(1, pixel_size=20)
    sheet.adjust_column_width(5, pixel_size=500)
    sheet.adjust_column_width(9, pixel_size=500)

    rows = []
    for section, group in sorted(groups.items()):
        rowIdx = len(rows) + 1
        rows.append([section, "", "", "", "", ""])
        sheet.merge_cells((rowIdx, 1), (rowIdx, 5))
        sectionHeader = sheet.cell((rowIdx, 1))
        sectionHeader.color = (249 / 255, 203 / 255, 156 / 255)
        for type, items in sorted(group.items()):
            rowIdx = len(rows) + 1
            typeInfo = items[0].type
            pricing = f"{str(typeInfo.unitPrice).replace('.', ',')} Kč/{typeInfo.unit}"

            itemsText = ", ".join(f"{i.recipe}({i.amount})" for i in items)
            rows.append(["",
                         type,
                         f"={str(sum(i.amount for i in items)).replace('.', ',')}-{Address((rowIdx, 8)).label}",
                         pricing, itemsText,
                         f"={Address((rowIdx, 3)).label} * {str(typeInfo.unitPrice).replace('.', ',')}",
                         "Máme:",
                         0])
            amounts = DataRange((rowIdx, 8), (rowIdx, 8), sheet)
            amountsTemplate = Cell("A1").set_number_format(FormatType.NUMBER, f"####0.0# \"{items[0].type.unit}\"")
            amounts.apply_format(amountsTemplate)

            sheet.add_conditional_formatting(
                Address((rowIdx, 1)).label,
                Address((rowIdx, 4)).label,
                condition_type="CUSTOM_FORMULA",
                condition_values=[f'=$A${rowIdx}'],
                format={'backgroundColor':{'red': 182 / 255, 'green': 215/ 255, 'blue': 168 / 255}} )
            sheet.set_data_validation(
                Address((rowIdx, 1)).label,
                Address((rowIdx, 1)).label,
                condition_type="BOOLEAN"
            )

    sheet.spreadsheet.client.run_batch()
    sheet.spreadsheet.client.set_batch_mode(False)
    sheet.update_values_batch([f"A1:H{len(rows)}"], [rows], parse=True)


def makeShoppping(id, shoppingName):
    table = getTable(id)

    listName = f"Nákup {shoppingName}"
    try:
        sheet = table.worksheet_by_title(listName)
        table.del_worksheet(sheet)
    except Exception as e:
        pass
    sheet = table.add_worksheet(listName, rows=500, cols=9)

    items = [x for x in collectShoppingItems(table) if x.shopping == shoppingName]
    groups = groupShoppingItems(items)
    fillShoppingTable(sheet, groups)

