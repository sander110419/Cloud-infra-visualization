from docx import Document
from docx.shared import Pt

import re

def create_document():
    doc = Document()
    return doc

def add_subscription_table(doc, data):
    subscriptions = data['Objects']
    
    # Add 'Subscriptions' as a heading
    doc.add_heading('Subscriptions', level=1)

    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Subscription ID'
    hdr_cells[1].text = 'Name'
    for subscription in subscriptions:
        row_cells = table.add_row().cells
        row_cells[0].text = subscription
        if 'name' in subscriptions[subscription]:
            row_cells[1].text = subscriptions[subscription]['name']
        else:
            row_cells[1].text = 'Name not found'

        # Reduce paragraph spacing
        for cell in row_cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)

def add_resource_group_table(doc, data):
    objects = data['Objects']

    # Add 'Resource Groups' as a heading
    doc.add_heading('Resource Groups', level=1)

    table = doc.add_table(rows=0, cols=1)
    resource_groups = set()

    for subscription_id in objects:
        for user_name, resources in objects[subscription_id].items():
            for resource in resources:
                match = re.search(r'/resourceGroups/(.*?)/', resource['Details']['id'])
                if match:
                    resource_group = match.group(1)
                    resource_groups.add(resource_group)

    for rg in resource_groups:
        row_cells = table.add_row().cells
        row_cells[0].text = rg

        # Reduce paragraph spacing
        for paragraph in row_cells[0].paragraphs:
            paragraph.paragraph_format.space_after = Pt(0)

    doc.add_paragraph('\n')

def group_resources_by_resource_group(resources):
    resource_groups = {}
    for resource in resources:
        match = re.search(r'/resourceGroups/(.*?)/', resource['Details']['id'])
        if match:
            resource_group = match.group(1)
            if resource_group not in resource_groups:
                resource_groups[resource_group] = []
            resource_groups[resource_group].append(resource)
    return resource_groups

def sort_resources_by_type(resources):
    return sorted(resources, key=lambda x: x['ResourceType'])

def format_attribute(attribute):
    attribute = attribute.replace('_', ' ')
    return attribute.capitalize()

def add_resource_table(doc, resource):
    if not resource['Details']:
        print(f"No details found for resource: {resource}")
        return

    resource_type = format_resource_type(resource['ResourceType'])
    add_heading(doc, resource_type, resource['Details']['name'])
    add_dict_as_table(doc, resource['Details'], 3)
    doc.add_paragraph()

def format_resource_type(resource_type):
    # Remove 'Microsoft.' from the resource type
    return resource_type.replace('Microsoft.', '')

def add_heading(doc, resource_type, resource_name, level=3):
    # Add resource type and name as a heading
    doc.add_heading(f"{resource_type} - {resource_name}", level)

def add_dict_as_table(doc, value_dict, level):
    table = doc.add_table(rows=0, cols=2)
    for attr, val in value_dict.items():
        if isinstance(val, dict):  # Check if the attribute value is a dictionary
            # Add this attribute as a separate table with 'attribute' as a header
            doc.add_heading(format_attribute(attr), level+1)
            add_dict_as_table(doc, val, level+1)
        else:
            add_row_to_table(table, attr, val)

def add_row_to_table(table, attr, val):
    row_cells = table.add_row().cells
    row_cells[0].text = format_attribute(attr)
    row_cells[1].text = str(val)
    reduce_paragraph_spacing(row_cells)

def reduce_paragraph_spacing(row_cells):
    # Reduce paragraph spacing
    for cell in row_cells:
        for paragraph in cell.paragraphs:
            paragraph.paragraph_format.space_after = Pt(0)

def add_resource_tables(doc, data):
    objects = data['Objects']
    for subscription_id in objects:
        for user_name, resources in objects[subscription_id].items():
            resource_groups = group_resources_by_resource_group(resources)
            for resource_group, resources in resource_groups.items():
                doc.add_heading("Resource Group: " + resource_group, level=2)
                sorted_resources = sort_resources_by_type(resources)
                for resource in sorted_resources:
                    add_resource_table(doc, resource)

def generate_word_document(data, output_folder):
    doc = create_document()
    add_subscription_table(doc, data)
    add_resource_group_table(doc, data)
    add_resource_tables(doc, data)
    doc.save(f'{output_folder}/output.docx')