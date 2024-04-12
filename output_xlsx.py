import json
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Color

def create_workbook():
    wb = Workbook()
    index_sheet = wb.active
    index_sheet.title = "Index"
    return wb, index_sheet

def process_resource(resource):
    details = resource['Details']
    df = pd.json_normalize(details)
    
    # Extract the 'type' field from the dataframe
    resource_type_df = df['type'].values[0] if 'type' in df.columns else ''
    
    safe_resource_type_df = resource_type_df.replace('Microsoft.', '').replace('/', '_').lower()
    
    # Fall back to using ResourceType if type field is empty
    if not safe_resource_type_df:
        resource_type = resource['ResourceType']
        safe_resource_type = resource_type.replace('Microsoft.', '').replace('/', '_').lower()
    else:
        safe_resource_type = safe_resource_type_df
    
    fixed_columns_order = ['type', 'id', 'name']
    for column in fixed_columns_order:
        if column not in df.columns:
            df[column] = ''
    return safe_resource_type, df

def update_resource_types(safe_resource_type, df, resource_types):
    if len(safe_resource_type) > 31:
        safe_resource_type = safe_resource_type[:30]
    if safe_resource_type not in resource_types:
        other_columns = [col for col in df.columns.tolist() if col not in ['type', 'id', 'name'] and not col.startswith('tag.')]
        tag_columns = [col for col in df.columns.tolist() if col.startswith('tag.')]
        sorted_columns = ['type', 'id', 'name'] + sorted(other_columns) + sorted(tag_columns)
        resource_types[safe_resource_type] = sorted_columns
    return safe_resource_type, resource_types

def write_to_workbook(wb: Workbook, safe_resource_type: str, df, resource_types):
    if safe_resource_type not in wb.sheetnames:
        wb.create_sheet(title=safe_resource_type)
        wb[safe_resource_type].insert_rows(0)
        # Add a link to the index sheet at the top of the current sheet
        cell = wb[safe_resource_type].cell(row=1, column=1)
        cell.value = "Index"
        cell.hyperlink = "#Index!A1"
        cell.font = Font(color=Color('0563C1'), underline='single')
        for row in dataframe_to_rows(df[resource_types[safe_resource_type]], index=False, header=True):
            wb[safe_resource_type].append(row)
            break
    df = df.reindex(columns=resource_types[safe_resource_type])
    for row in dataframe_to_rows(df, index=False, header=False):
        row = [str(cell) if isinstance(cell, list) else cell for cell in row]
        wb[safe_resource_type].append(row)

def output_to_excel(data, output_folder):
    wb, index_sheet = create_workbook()
    resource_types = {}
    for subscription, resource_groups in data['Objects'].items():
        for rg_name, resources in resource_groups.items():
            for resource in resources:
                safe_resource_type, df = process_resource(resource)
                safe_resource_type, resource_types = update_resource_types(safe_resource_type, df, resource_types)
                write_to_workbook(wb, safe_resource_type, df, resource_types)
    for resource_type in resource_types:
        index_sheet.append([resource_type])
        last_row = index_sheet.max_row
        cell = index_sheet.cell(row=last_row, column=1)
        cell.hyperlink = f'#{resource_type}!A1'
        cell.font = Font(color=Color('0563C1'), underline='single')
    wb.save(f'{output_folder}/output.xlsx')