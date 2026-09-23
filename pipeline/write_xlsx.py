import openpyxl


def write_xlsx(sheet_title, header, rows, output_path):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = sheet_title
    sheet.append(header)

    for row in rows:
        sheet.append(row)

    workbook.save(output_path)
