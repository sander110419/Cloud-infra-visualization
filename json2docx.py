from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

def create_document():
    doc = Document()
    return doc

def add_subscription_table(doc, data):
    subscriptions = data['Objects']
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Subscription ID'
    hdr_cells[1].text = 'Name'
    for subscription in subscriptions:
        row_cells = table.add_row().cells
        row_cells[0].text = subscription
        # Check if 'name' key exists in the dictionary before accessing it
        if 'name' in subscriptions[subscription]:
            row_cells[1].text = subscriptions[subscription]['name']
        else:
            row_cells[1].text = 'Name not found'

def add_resource_group_table(doc, data):
    objects = data['Objects']
    table = doc.add_table(rows=1, cols=1)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Resource Groups'
    
    # Create a set to store unique resource group names
    resource_groups = set()

    for subscription_id in objects:
        for user_name, resources in objects[subscription_id].items():
            for resource in resources:
                # Extract resource group from id
                match = re.search(r'/resourceGroups/(.*?)/', resource['Details']['id'])
                if match:
                    resource_group = match.group(1)
                    resource_groups.add(resource_group)

    # Add each unique resource group name to the table
    for rg in resource_groups:
        row_cells = table.add_row().cells
        row_cells[0].text = rg

    doc.add_paragraph('\n')

def add_resource_tables(doc, data):
    objects = data['Objects']
    for subscription_id in objects:
        for user_name, resources in objects[subscription_id].items():
            # Group resources by resource group
            resource_groups = {}
            for resource in resources:
                # Extract resource group from id
                match = re.search(r'/resourceGroups/(.*?)/', resource['Details']['id'])
                if match:
                    resource_group = match.group(1)
                    if resource_group not in resource_groups:
                        resource_groups[resource_group] = []
                    resource_groups[resource_group].append(resource)

            # Iterate over each resource group
            for resource_group, resources in resource_groups.items():
                # Add a header with the resource group name
                doc.add_heading(resource_group, level=2)

                # Sort resources by ResourceType
                sorted_resources = sorted(resources, key=lambda x: x['ResourceType'])

                # Iterate over each resource for the current resource group
                for resource in sorted_resources:
                    # Check if there are any details for this resource
                    if resource['Details']:
                        # Add a subheader with the resource type
                        doc.add_heading(resource['ResourceType'], level=3)

                        # Create a new table with a header row
                        table = doc.add_table(rows=1, cols=2)
                        hdr_cells = table.rows[0].cells
                        hdr_cells[0].text = 'Attribute'
                        hdr_cells[1].text = 'Value'

                        # Add a row for each attribute of the resource
                        for attribute, value in resource['Details'].items():
                            row_cells = table.add_row().cells
                            row_cells[0].text = str(attribute)
                            row_cells[1].text = str(value)

                        # Add a line break after each table
                        doc.add_paragraph()

                    else:
                        print(f"No details found for resource: {resource}")



def generate_word_document(data, output_folder):
    doc = create_document()
    add_subscription_table(doc, data)
    add_resource_group_table(doc, data)
    add_resource_tables(doc, data)
    doc.save(f'{output_folder}/output.docx')