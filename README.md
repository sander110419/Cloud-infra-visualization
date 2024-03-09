# Cloud-infra-visualization :cloud:

Cloud-infra-visualization is an open-source tool designed to programmatically create infrastructure designs and diagrams for all major cloud vendors. This project aims to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

## :white_check_mark: Currently implemented

### Trello board:
[Click here](https://trello.com/b/wuSdQR4P/cloud-visualization-project)

### Azure:
About 60 resources are already supported

### Output:
- [x] Draw.IO
- [ ] Visio
- [ ] PDF

## :rocket: How to run

You can run the script as following:  
`main.py --tenant_id TENANT_ID --client_id CLIENT_ID --client_secret CLIENT_SECRET --subscription_id SUBSCRIPTION_ID --output_xlsx` 
If you do not add a subscription ID it will iterate over all avalable subscriptions.  
--output_xlsx is optional and will output an xlsx overview of all resources and types.  

## :pushpin: Roadmap

The roadmap for this project includes:

### Base

The base of the project will be developed first, setting up the foundation for the rest of the features.
The project will be written in python and in the future contain a web front-end for ease-of-use

### Providers

The aim is to support all major cloud providers. The following are currently on the roadmap:

- **Azure**: Support for Azure infrastructure
- **AWS**: AWS infrastructure
- **Google**: Google Cloud Platform infrastructure

### Visualisations

Different types of visualizations will be supported. These include:

- **Draw.io**: You will be able to export your infrastructure diagrams to Draw.io (XML) format.
- **Visio**: Visio format will also be supported for those who prefer using Microsoft's tool.
- **PDF**: For easy sharing and viewing, you will be able to export your diagrams to PDF.
- **Markdown**: For simplicity and compatibility with platforms like GitHub, we will also support exporting diagrams in Markdown format.

## :crystal_ball: Future

I'd love this to one day be a viable replacement for tools like Cloudockit, Holori or Lucidscale with a frontend for ease of use.

## :page_with_curl: License

This project is available under the GPL-3.0 license.
