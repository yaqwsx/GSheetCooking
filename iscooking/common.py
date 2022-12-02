import pygsheets

def getTable(id):
    gc = pygsheets.authorize()
    gc.sheet.seconds_per_quota = 60
    return gc.open_by_key(id)
