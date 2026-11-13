# Cloud-Infra-Visualization ☁️

Cloud-Infra-Visualization is an open-source tool that enables you to create infrastructure designs and diagrams for major cloud vendors programmatically. The current focus of this project is Microsoft Azure. The goal of this project is to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  

For more detailed information, please refer to our [documentation](https://github.com/sander110419/Cloud-infra-visualization/wiki).

## Project Board:
You can view our progress and upcoming features on our [Github Project](https://github.com/users/sander110419/projects/2).

## ✅ Currently Implemented Features

### Azure:
**Every Azure resource type is supported.** Resources are read through Azure Resource Graph and the generic Azure Resource Manager API instead of one SDK per Azure service. There is no list of supported services to keep up to date: if it exists in your subscription, it ends up in the output with its full configuration, including resource types that did not exist when this tool was written.

### What does it do (as of now):
- Retrieves all or selected subscriptions.
- Iterates over these subscriptions and gets all or selected resource groups.
- Iterates over all or selected resource groups and retrieves all resources, of every type, with all their properties.
- Adds the child resources Azure does not list by itself: subnets and peerings, blob containers, file shares, storage queues and tables, Service Bus queues and topics, Event Hubs, functions, Cosmos DB / PostgreSQL / MySQL / SQL Managed Instance databases, backup items, Front Door and CDN endpoints, API Management APIs and virtual hub connections.
- Collects the Azure Advisor recommendations for all resources.
- Outputs an excel file with all technical configuration details of all resources, one sheet per resource type.
- Outputs a draw.io diagram with a page per subscription and a network topology page (see below).
- Outputs a mermaid.js (HTML) diagram which connects all resources to resource groups, DBs to servers, etc.
- Outputs a Word document with the configuration of every resource.
- Outputs a json file containing all the technical data to process in other tools.

### The draw.io diagrams

![Network topology page](example%20output/network-topology.png)

- **A page per subscription**: subscription → resource groups → resources, drawn with the official Azure icons. Resources that belong together share a box: a VM with its NIC, disks, public IP and extensions, a SQL server with its databases, an App Service plan with its apps and functions, a private endpoint with its NIC. Every other relationship found in the configuration (identities, Key Vaults, workspaces, alerts, private endpoints, ...) is drawn as a link. Links are grouped in layers (network, data, identity & security, monitoring, other) that you can switch on and off under *View > Layers*.
- **A network topology page**: virtual networks → subnets → everything deployed into them with its IP addresses. Subnets show their NSG, route table, NAT gateway and delegation. VNet peerings (also to networks outside the documented scope), VPN / ExpressRoute connections and the service behind each private endpoint are included.
- Hover over a shape, or use *Edit Data*, to see its type, SKU, location, tags and resource ID. Every shape links to the resource in the Azure portal.
- A coloured badge on a resource shows how many Azure Advisor recommendations it has; hover over it to read them.
- Relationships are worked out from resource IDs rather than from a list of known resource types, so resources this tool has never heard of are drawn and linked as well.

A subscription page looks like [this](example%20output/subscription-page.png). The [example output](example%20output) folder has the complete files.

Icons are embedded in the .drawio file by default, so it displays correctly anywhere. With `--drawio_icons library` the diagram refers to the Azure icons that ship with draw.io instead, which makes the file less than half the size (useful for large environments).

The diagram can be rebuilt from an existing `output.json` without contacting Azure:
```
python main.py --input_json output/output.json --output_drawio
```

## 🚀 How to Run

Install the requirements first (Python 3.9 or newer, developed and tested on 3.12):
```
pip install -r requirements.txt
```
The identity you log in with needs the **Reader** role on the subscriptions you want to document.

You can run the minimum script as follows:  
```python
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --output_xlsx --output_folder PATH_TO_OUTPUT_FOLDER
``` 
If you do not add a subscription ID, the script will iterate over all available subscriptions.  
The `--subscription_id` flag is optional, the script will only iterate over that subscription when added. Repeat it, or separate IDs with commas, for several subscriptions.  
The `--resource_group` flag is optional, the script will only iterate over that resource group when added.  
The `--rgtag_key` / `--rgtag_value` flags are optional and only include resource groups with that tag.  
The `--rtag_key` / `--rtag_value` flags are optional and only include resources with that tag.  
The `--output_xlsx` flag is optional and will output an xlsx overview of all resources and types when added.  
The `--output_folder` flag is optional, if this is omitted, it will write to an "output" folder in the current folder.  
The `--output_drawio` flag is optional, when added this will output a drawio file with your visualization.  
The `--output_docx` flag is optional, when added this will output a Word document.  
The `--output_html` flag is optional, when added this will output a HTML file with your visualization.

Instead of passing them as arguments you can set the `AZURE_TENANT_ID`, `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET` environment variables. This keeps the secret out of your shell history.

You can alternatively authenticate using your user account, interactively to an app registration, device code or with a client certificate.  
`--use_device_code` Allows you to log in using a device code that will be generated  
`--interactive_login` Allows you to log in using interactive login to a client that supports this.  
`--user_login` Allows you to log in using your own microsoft account.  
`--use_cli` Uses the account you are logged in with in the Azure CLI (`az login`).  
`--certificate_path` Allows you to set the path to your certificate to log in to the client app.  

The full version with all features enabled would be:  
```python
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --subscription_id SUBSCRIPTION_ID --resource_group RESOURCE_GROUP --output_folder PATH_TO_OUTPUT_FOLDER --output_xlsx --output_drawio --output_docx --output_html
``` 

Options you will rarely need:  
`--engine auto|graph|arm` How resources are read. `auto` (default) uses Azure Resource Graph, checks the result against Resource Manager and falls back to Resource Manager when Resource Graph is not available. `arm` only uses Resource Manager, which is slower.  
`--skip_children` Do not collect child resources (subnets, queues, containers, ...).  
`--skip_advisor` Do not collect Azure Advisor recommendations.  
`--workers N` Number of parallel requests to Azure (default 8).  
`--arm_endpoint URL` Resource Manager endpoint for sovereign clouds, e.g. `https://management.usgovcloudapi.net`.  
`--log_level LEVEL` Level of detail in `CloudInfraViz.log`.

To build and run the Docker container with the provided Dockerfile, follow these steps:

```bash
# Clone the repository
git clone https://github.com/sander110419/Cloud-infra-visualization.git

# Navigate into the cloned directory
cd Cloud-infra-visualization

# Build the Docker image
docker build -t cloud-infra-visualization .
```
```bash
# Run the Docker container
docker run -v /path/to/your/output_folder:/app/output cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --resource_group "your_resource_group" --output_folder "/path/to/your/output_folder" --output_xlsx --output_drawio --output_mermaid
```
Replace "/path/to/your/output_folder" with your actual output path.  
  
**The image is also available on  [DockerHub](https://hub.docker.com/r/sander110419/cloud-infra-visualization)**

To run directly from Docker hub:

```bash
docker run -v /path/to/your/output_folder:/app/output sander110419/cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --resource_group "your_resource_group" --output_xlsx --output_drawio --output_mermaid
```
  
Replace "/path/to/your/output_folder" with your actual output path.

## 🖥️ GUI Usage

The project also includes a Graphical User Interface (GUI) for ease of use. The GUI is built using PyQt5 and provides an interactive way to input your Azure credentials, select subscriptions, and choose output options.

### How to Run the GUI

You can run the GUI by executing the following commands:

```python
pip install -r requirements-gui.txt
python frontend.py
```

### GUI Features

The GUI provides the following features:

1. **Load Identity**: This button allows you to load a previously saved identity. An identity consists of a Tenant ID, Client ID, and Client Secret.

2. **New Identity**: This button opens a dialog where you can enter a new identity. You will need to provide a Tenant ID, Client ID, and Client Secret. The identity gets safely stored in the keyring (Linux Keyring or Windows Credential storage)

3. **Subscription List**: This list shows all the subscriptions available for the loaded identity. You can select one or more subscriptions to be included in the visualization.

4. **Advanced Options**: This section allows you to specify additional options such as output format (Excel, DrawIO, Word or HTML), resource group name, resource group tag key/value, resource tag key/value, and output folder.

5. **Start Document Generation**: This button starts the document generation process. The output will be displayed in the text area below the button, after which you can choose to open the output folder.

## 📌 Roadmap

The roadmap for this project includes:

### Base

The base of the project will be developed first, setting up the foundation for the rest of the features.
The project will be written in Python and in the future contain a web front-end for ease-of-use.

### Providers

Currently the aim is to fully support Azure, with any other providers in the future. 

### Visualizations

Different types of visualizations will be supported. These include:

- **Draw.io**: You will be able to export your infrastructure diagrams to Draw.io (XML) format.
- **HTML**: You will be able to export your infrastructure diagrams to Mermaid.js (Markdown) format.

Soon:

*- **Visio**: Visio format will also be supported for those who prefer using Microsoft's tool.*

*- **PDF**: For easy sharing and viewing, you will be able to export your diagrams to PDF.* 

*- **Markdown**: For simplicity and compatibility with platforms like GitHub, we will also support exporting diagrams in Markdown format.* 

## 🔮 Future

I'd love this to one day be a viable replacement for tools like Cloudockit, Holori or Lucidscale with a frontend for ease of use.

## 🧪 Development

The tests run against a small fake of the Azure API (`tests/fake_azure.py`), so no Azure account is needed:
```
pip install -r requirements-dev.txt
python -m pytest
```
`python -m tests.fake_azure "example output"` regenerates the example output from that fake environment.

## 📜 License

This project is available under the GPL-3.0 license.

## Contribute

Feel like contributing to the project? [More info here](https://github.com/sander110419/Cloud-infra-visualization/blob/main/CONTRIBUTING.md)  
You can get also contact me via the project Discord Channel [HERE](https://discord.gg/MurEkZQBEb)