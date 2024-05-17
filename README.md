# Cloud-Infra-Visualization ☁️

Cloud-Infra-Visualization is an open-source tool designed to programmatically create infrastructure designs and diagrams for all major cloud vendors. This project aims to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=sander110419_Cloud-infra-visualization&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=sander110419_Cloud-infra-visualization)  


## ✅ Currently Implemented Features

### Trello Board:
You can view our progress and upcoming features on our [Trello board](https://trello.com/b/wuSdQR4P/cloud-visualization-project).

### Azure:
We currently support about 60 Azure resourcetypes.

## 🚀 How to Run

You can run the minimum script as follows:  
```
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --output_xlsx --output_folder PATH_TO_OUTPUT_FOLDER
``` 
If you do not add a subscription ID, the script will iterate over all available subscriptions.  
The `--subscription_id` flag is optional, the script will only iterate over that subscription when added.  
The `--resource_group` flag is optional, the script will only iterate over that resource group when added.  
The `--output_xlsx` flag is optional and will output an xlsx overview of all resources and types when added.  
The `--output_folder` flag is optional, if this is omitted, it will write to an "output" folder in the current folder.  
The `--output_drawio` flag is optional, when added this will output a drawio file with your visualization.  

The full version with all features enabled would be:  
```
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

```
docker run -v /path/to/your/output_folder:/app/output sander110419/cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --resource_group "your_resource_group" --output_xlsx --output_drawio
```
  
Replace "/path/to/your/output_folder" with your actual output path.


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
