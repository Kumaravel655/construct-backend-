from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook


def export_rows_to_excel(filename, headers, rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Data'

    sheet.append(headers)
    for row in rows:
        sheet.append(list(row))

    for column_index, _header in enumerate(headers, start=1):
        column_letter = sheet.cell(row=1, column=column_index).column_letter
        max_length = 0
        for cell in sheet[column_letter]:
            cell_value = '' if cell.value is None else str(cell.value)
            if len(cell_value) > max_length:
                max_length = len(cell_value)
        sheet.column_dimensions[column_letter].width = min(max_length + 2, 40)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
