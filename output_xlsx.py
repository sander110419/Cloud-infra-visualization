import json
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Color

def output_to_excel(data):
    # Create a new workbook and select the active sheet
    wb = Workbook()
    index_sheet = wb.active
    index_sheet.title = "Index"

    # Initialize a dictionary to store resource types and their columns
    resource_types = {}

    # Define the fixed order of the first three columns
    fixed_columns_order = ['type', 'id', 'name']

    # Iterate over subscriptions
    for subscription, resource_groups in data['Objects'].items():
        # Iterate over resource groups
        for rg_name, resources in resource_groups.items():
            # Iterate over resources
            for resource in resources:
                resource_type = resource['ResourceType'].replace('Microsoft.', '')
                details = resource['Details']

                # Replace invalid characters in the resource type
                safe_resource_type = resource_type.replace('/', '_')

                # Convert the details dictionary to a DataFrame and normalize it
                df = pd.json_normalize(details)

                # Ensure 'type', 'id', and 'name' columns exist in the DataFrame
                for column in fixed_columns_order:
                    if column not in df.columns:
                        df[column] = ''

                # If the resource type is not yet in the dictionary, create a new sheet and add headers
                # If the safe_resource_type is longer than 31 characters, truncate it
                if len(safe_resource_type) > 31:
                    safe_resource_type = safe_resource_type[:30]

                if safe_resource_type not in resource_types:
                    # Sort the columns so that columns starting with "tag." are at the end
                    other_columns = [col for col in df.columns.tolist() if col not in fixed_columns_order and not col.startswith('tag.')]
                    tag_columns = [col for col in df.columns.tolist() if col.startswith('tag.')]

                    sorted_columns = fixed_columns_order + sorted(other_columns) + sorted(tag_columns)
                    resource_types[safe_resource_type] = sorted_columns

                    wb.create_sheet(title=safe_resource_type)

                    # Write the header to the worksheet
                    for row in dataframe_to_rows(df[sorted_columns], index=False, header=True):
                        wb[safe_resource_type].append(row)
                        break  # We only want the header, so break after the first row

                # Reindex the DataFrame with the fixed set of columns
                df = df.reindex(columns=resource_types[safe_resource_type])

                # Append the DataFrame to the corresponding sheet
                for row in dataframe_to_rows(df, index=False, header=False):
                    # Convert empty lists to a string representation
                    row = [str(cell) if isinstance(cell, list) else cell for cell in row]
                    wb[safe_resource_type].append(row)

    # Write the resource types to the index sheet
    for resource_type in resource_types:
        # Append the resource type to the index sheet
        index_sheet.append([resource_type])
        
        # Get the last row number
        last_row = index_sheet.max_row
        
        # Get the cell at the last row and first column
        cell = index_sheet.cell(row=last_row, column=1)
        
        # Create a hyperlink to the corresponding sheet
        cell.hyperlink = f'#{resource_type}!A1'
        
        # Style the cell as a hyperlink (optional)
        cell.font = Font(color=Color('0563C1'), underline='single')

    # Save the workbook
    wb.save('output.xlsx')