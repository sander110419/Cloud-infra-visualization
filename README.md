# Cloud-Infra-Visualization ☁️

Cloud-Infra-Visualization is an open-source tool designed to programmatically create infrastructure designs and diagrams for all major cloud vendors (current focus is Microsoft Azure). This project aims to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  

## ✅ Currently Implemented Features

### Trello Board:
You can view our progress and upcoming features on our [Github Project](https://github.com/users/sander110419/projects/2).

### Azure:
We currently support MOST Azure resourcetypes.

### What does it do (as of now):
- Get all or selected subscriptions
- Iterate over all these and gets all or selected resource groups
- Iterate over all or selected resource groups and gets all resources.
- Output an excel file with all technical configuration details of all resources
- Output a draw.io diagram which connects all resources to resource groups, DBs to servers, disks to VMs etc.
- Output a json file containing all the technical data to process in other tools.

## 🚀 How to Run

You can run the minimum script as follows:  
```python
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --output_xlsx --output_folder PATH_TO_OUTPUT_FOLDER
``` 
If you do not add a subscription ID, the script will iterate over all available subscriptions.  
The `--subscription_id` flag is optional, the script will only iterate over that subscription when added.  
The `--resource_group` flag is optional, the script will only iterate over that resource group when added.  
The `--output_xlsx` flag is optional and will output an xlsx overview of all resources and types when added.  
The `--output_folder` flag is optional, if this is omitted, it will write to an "output" folder in the current folder.  
The `--output_drawio` flag is optional, when added this will output a drawio file with your visualization.  

The full version with all features enabled would be:  
```python
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --subscription_id SUBSCRIPTION_ID --resource_group RESOURCE_GROUP --output_folder PATH_TO_OUTPUT_FOLDER --output_xlsx --output_drawio
``` 

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
docker run -v /path/to/your/output_folder:/app/output cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --resource_group "your_resource_group" --output_folder "/path/to/your/output_folder" --output_xlsx --output_drawio
```
Replace "/path/to/your/output_folder" with your actual output path.  
  
**The image is also available on  [DockerHub](https://hub.docker.com/r/sander110419/cloud-infra-visualization)**

To run directly from Docker hub:

```bash
docker run -v /path/to/your/output_folder:/app/output sander110419/cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --resource_group "your_resource_group" --output_xlsx --output_drawio
```
  
Replace "/path/to/your/output_folder" with your actual output path.

## 🖥️ GUI Usage

The project also includes a Graphical User Interface (GUI) for ease of use. The GUI is built using PyQt5 and provides an interactive way to input your Azure credentials, select subscriptions, and choose output options.

### How to Run the GUI

You can run the GUI by executing the following command:

```python
python frontend.py
```

### GUI Features

The GUI provides the following features:

1. **Load Identity**: This button allows you to load a previously saved identity. An identity consists of a Tenant ID, Client ID, and Client Secret.

2. **New Identity**: This button opens a dialog where you can enter a new identity. You will need to provide a Tenant ID, Client ID, and Client Secret. The identity gets safely stored in the keyring (Linux Keyring or Windows Credential storage)

3. **Subscription List**: This list shows all the subscriptions available for the loaded identity. You can select one or more subscriptions to be included in the visualization.

4. **Advanced Options**: This section allows you to specify additional options such as output format (Excel or DrawIO), resource group name, resource group tag key/value, resource tag key/value, and output folder.

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

Soon:

*- **Visio**: Visio format will also be supported for those who prefer using Microsoft's tool.*

*- **PDF**: For easy sharing and viewing, you will be able to export your diagrams to PDF.* 

*- **Markdown**: For simplicity and compatibility with platforms like GitHub, we will also support exporting diagrams in Markdown format.* 

## 🔮 Future

I'd love this to one day be a viable replacement for tools like Cloudockit, Holori or Lucidscale with a frontend for ease of use.

## 📜 License

This project is available under the GPL-3.0 license.