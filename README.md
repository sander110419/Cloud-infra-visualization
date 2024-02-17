# Cloud-infra-visualization

Cloud-infra-visualization is an open-source tool designed to programmatically create infrastructure designs and diagrams for all major cloud vendors. This project aims to simplify the process of visualizing your cloud infrastructure, making it easier to understand and manage.

## Currently implemented

Azure:
- [x] Authentication
- [x] Resource
- [x] Subscription
- [x] Network
- [x] Compute
- [x] Recoveryservices
- [x] Recoveryservicesback
- [x] Sql
- [x] Web
- [x] Keyvault
- [x] Loganalytics
- [x] Storage
- [x] Containerservice
- [x] Apimanagement
- [x] Batch
- [x] Botservice
- [x] Containerregistry
- [x] Datafactory
- [x] Datalake-store
- [x] Eventhub
- [x] Iothub
- [x] Logic
- [x] Machinelearningservi
- [x] Redis
- [x] Search
- [x] Servicebus
- [x] Signalr
- [x] Streamanalytics
- [x] Trafficmanager
- [x] Cosmosdb
- [x] Servicefabric
- [x] Cdn
- [x] Cognitiveservices
- [x] Devtestlabs
- [x] Media
- [x] Monitor
- [x] Relay
- [x] Scheduler
- [x] Dns

Output:
- [x] Draw.IO
- [ ] Visio
- [ ] PDF


## Roadmap

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

## Future

I'd love this to one day be a viable replacement for tools like Cloudockit, Holori or Lucidscale with a frontend for ease of use.

## License

This project is available under the GPL-3.0 license.