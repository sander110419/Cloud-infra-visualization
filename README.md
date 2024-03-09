# Cloud-Infra-Visualization ☁️

Cloud-Infra-Visualization is an open-source tool designed to programmatically create infrastructure designs and diagrams for all major cloud vendors. This project aims to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

## ✅ Currently Implemented Features

### Trello Board:
You can view our progress and upcoming features on our [Trello board](https://trello.com/b/wuSdQR4P/cloud-visualization-project).

### Azure:
We currently support about 60 Azure resources.

## 🚀 How to Run

You can run the script as follows:  
```
main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --subscription_id SUBSCRIPTION_ID --output_xlsx
``` 
If you do not add a subscription ID, the script will iterate over all available subscriptions.  
The `--output_xlsx` flag is optional and will output an xlsx overview of all resources and types.  

To build and run the Docker container with the provided Dockerfile, follow these steps:

```bash
# Clone the repository
git clone https://github.com/sander110419/Cloud-infra-visualization.git

# Navigate into the cloned directory
cd Cloud-infra-visualization

# Build the Docker image
docker build -t cloud-infra-visualization .

# Run the Docker container
docker run -v /path/to/your/output_folder:/app/output_folder Cloud-infra-visualization --tenant_id "your_tenant_id" --client_id "your_client_id" --client_secret "your_client_secret" --subscription_id "your_subscription_id" --output_xlsx
```
Replace "/path/to/your/output_folder" with your actual output path.

## 📌 Roadmap

The roadmap for this project includes:

### Base

The base of the project will be developed first, setting up the foundation for the rest of the features.
The project will be written in Python and in the future contain a web front-end for ease-of-use.

### Providers

The aim is to support all major cloud providers. The following are currently on the roadmap:

- **Azure**: Support for Azure infrastructure.
- **AWS**: AWS infrastructure.
- **Google**: Google Cloud Platform infrastructure.

### Visualizations

Different types of visualizations will be supported. These include:

- **Draw.io**: You will be able to export your infrastructure diagrams to Draw.io (XML) format.
- **Visio**: Visio format will also be supported for those who prefer using Microsoft's tool.
- **PDF**: For easy sharing and viewing, you will be able to export your diagrams to PDF.
- **Markdown**: For simplicity and compatibility with platforms like GitHub, we will also support exporting diagrams in Markdown format.

## 🔮 Future

I'd love this to one day be a viable replacement for tools like Cloudockit, Holori or Lucidscale with a frontend for ease of use.

## 📜 License

This project is available under the GPL-3.0 license.