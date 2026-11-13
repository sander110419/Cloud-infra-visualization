import json
import os
import re

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Color, Font
from openpyxl.utils import get_column_letter

from azure_func.inventory import iter_details

LINK_FONT = Font(color=Color('0563C1'), underline='single')
HEADER_FONT = Font(bold=True)
FIXED_COLUMNS = ['subscription_id', 'resource_group', 'type', 'id', 'name']
MAX_CELL_LENGTH = 32000  # Excel allows 32767 characters in a cell
RESERVED_SHEETS = ('Index', 'All Resources', 'Recommendations')


def sheet_title(resource_type, used):
    """Human friendly, valid and unique sheet name for a resource type.

    'Microsoft.Compute/virtualMachines' -> 'Compute - Virtualmachines'
    """
    parts = resource_type.replace('Microsoft.', '').replace('microsoft.', '').replace('/', '_').lower().split('_')
    if len(parts) > 1:
        title = f"{parts[0].capitalize()} - {' '.join(part.capitalize() for part in parts[1:])}"
    else:
        title = parts[0].capitalize() or 'Unknown'
    title = re.sub(r"[\[\]:*?/\\']", ' ', title)[:31].strip() or 'Unknown'
    candidate, counter = title, 2
    while candidate.lower() in used:  # Excel sheet names are limited to 31 characters and case-insensitive
        suffix = f"~{counter}"
        candidate = title[:31 - len(suffix)] + suffix
        counter += 1
    used.add(candidate.lower())
    return candidate


def cell_value(value):
    """Convert a value to something Excel can store."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, (list, dict)):
        if not value:
            return None
        if isinstance(value, list) and all(isinstance(item, (str, int, float)) for item in value):
            value = ', '.join(map(str, value))
        else:
            value = json.dumps(value, default=str)
    if isinstance(value, str):
        return ILLEGAL_CHARACTERS_RE.sub('', value)[:MAX_CELL_LENGTH]
    if isinstance(value, (bool, int, float)):
        return value
    return str(value)[:MAX_CELL_LENGTH]


def get_visio_shape_name(resource_type):
    """Convert Azure resource type to a clean stencil shape name"""
    return (resource_type or '').replace('Microsoft.', '').replace('/', '_').lower()


def add_index_link(ws):
    cell = ws.cell(row=1, column=1)
    cell.value = "Index"
    cell.hyperlink = "#Index!A1"
    cell.font = LINK_FONT


def write_table(ws, columns, rows, index_link=True):
    """Write a header and data rows, optionally below a link back to the Index sheet."""
    if index_link:
        add_index_link(ws)
    ws.append(columns)
    header_row = ws.max_row
    for cell in ws[header_row]:
        cell.font = HEADER_FONT
    for row in rows:
        ws.append([cell_value(value) for value in row])
    ws.freeze_panes = f'A{header_row + 1}'
    if columns:
        ws.auto_filter.ref = f"A{header_row}:{get_column_letter(len(columns))}{max(ws.max_row, header_row)}"
    for index, column in enumerate(columns, start=1):
        ws.column_dimensions[get_column_letter(index)].width = min(max(len(str(column)) + 2, 12), 60)


def group_by_type(data):
    """resource type -> list of flat rows (dicts)."""
    by_type = {}
    for subscription_id, rg_name, entry, detail in iter_details(data):
        resource_type = detail.get('type') or entry.get('ResourceType') or 'Unknown'
        row = {'subscription_id': subscription_id, 'resource_group': rg_name, **detail}
        row['type'] = resource_type
        by_type.setdefault(resource_type, []).append(row)
    return by_type


def order_columns(columns):
    other = sorted(col for col in columns if col not in FIXED_COLUMNS and not col.startswith('tags.'))
    tags = sorted(col for col in columns if col.startswith('tags.'))
    return FIXED_COLUMNS + other + tags


def collect_recommendations(data):
    rows = []
    for subscription_id, rg_name, entry, detail in iter_details(data):
        for recommendation in entry.get('Recommendations') or []:
            if not isinstance(recommendation, dict) or 'Error' in recommendation:
                continue
            rows.append({
                **recommendation,
                'SubscriptionId': subscription_id,
                'ResourceGroupName': rg_name,
                'ResourceId': detail.get('id', ''),
                'ResourceName': detail.get('name', ''),
                'ResourceType': entry.get('ResourceType') or detail.get('type', ''),
            })
    for subscription_id, info in (data.get('Subscriptions') or {}).items():
        for recommendation in info.get('Recommendations') or []:
            rows.append({
                **recommendation,
                'SubscriptionId': subscription_id,
                'ResourceGroupName': '',
                'ResourceId': f'/subscriptions/{subscription_id}',
                'ResourceName': info.get('displayName', subscription_id),
                'ResourceType': 'Microsoft.Resources/subscriptions',
            })
    return rows


def output_to_excel(data, output_folder):
    wb = Workbook()
    index_sheet = wb.active
    index_sheet.title = "Index"
    index_sheet.append(['Sheet', 'Resource type', 'Count'])
    for cell in index_sheet[1]:
        cell.font = HEADER_FONT

    def add_to_index(title, resource_type='', count=None):
        index_sheet.append([title, resource_type, count])
        cell = index_sheet.cell(row=index_sheet.max_row, column=1)
        cell.hyperlink = f"#'{title}'!A1"
        cell.font = LINK_FONT

    used_titles = {name.lower() for name in RESERVED_SHEETS}
    all_rows = []
    by_type = group_by_type(data)
    for resource_type in sorted(by_type, key=str.lower):
        rows = by_type[resource_type]
        # One table per type; the columns are the union over all resources of that type.
        frame = pd.json_normalize(rows)
        columns = order_columns(list(frame.columns))
        frame = frame.reindex(columns=columns).astype(object)
        title = sheet_title(resource_type, used_titles)
        write_table(wb.create_sheet(title=title), columns, frame.itertuples(index=False, name=None))
        add_to_index(title, resource_type, len(rows))
        for row in rows:
            all_rows.append([row.get('subscription_id'), row.get('resource_group'), resource_type, row.get('id'),
                             row.get('name'), get_visio_shape_name(resource_type)])

    recommendations = collect_recommendations(data)
    if recommendations:
        frame = pd.json_normalize(recommendations)
        front = ['SubscriptionId', 'ResourceGroupName', 'ResourceId', 'ResourceName', 'ResourceType']
        columns = front + [col for col in frame.columns if col not in front]
        frame = frame.reindex(columns=columns).astype(object)
        write_table(wb.create_sheet(title='Recommendations'), columns, frame.itertuples(index=False, name=None))
        add_to_index('Recommendations', '', len(recommendations))

    # Flat list of everything, including the shape name used for Visio data linking.
    # A plain table with the header in row 1, so Visio can import it as is.
    write_table(wb.create_sheet(title='All Resources'), FIXED_COLUMNS + ['VisioShape'], all_rows, index_link=False)
    add_to_index('All Resources', '', len(all_rows))

    index_sheet.column_dimensions['A'].width = 34
    index_sheet.column_dimensions['B'].width = 70
    index_sheet.freeze_panes = 'A2'
    wb.save(os.path.join(output_folder, 'output.xlsx'))
