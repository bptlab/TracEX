# TracEX

[![GitHub stars](https://img.shields.io/github/stars/bptlab/TracEX)](https://github.com/bptlab/TracEX)
[![GitHub open issues](https://img.shields.io/github/issues/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub closed pull requests](https://img.shields.io/github/issues-closed/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub open pull requests](https://img.shields.io/github/issues-pr/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)

TracEX aims to extract event logs from unstructured text, specifically written patient experiences known as patient journeys. By leveraging Large Language Models (LLMs), TracEX can automatically identify and extract relevant events, activities, timestamps and further information from natural langauge text. This enables healthcare professionals and researchers to gain valuable insights into patient experiences, treatment pathways, and potential areas for improvement in healthcare delivery.

This project was initiated and completed as part of the team's bachelor's degree under the supervision of the Business Process Technology chair at the Hasso Plattner Institute. The project was conducted in cooperation with [mamahealth](https://www.mamahealth.com/).

## Key Features
- **Extraction Pipeline**: A robust pipeline to clean, process, and extract data from natural language text.
- **Patient Journey Generator**: Generates comprehensive patient journeys based on randomized cohort data.
- **Database**: Stores patient journeys and related extraction results for easy access and analysis.
- **Metrics and Evaluation Tool**: Evaluates the accuracy and effectiveness of the extraction process and allows for analysis of exctraction results.
- **Intuitive UI**: User-friendly interface for you to interact with the tool and visualize results.

## Requirements
To run TracEX successfully, it is essential to obtain an OpenAI API key with adequate credits. TracEX integrates the OpenAI API to leverage Large Language Models (LLMs) for extracting relevant information from unstructured text. Without a valid API key and sufficient balance, the extraction process cannot be performed.

## Installation using Docker
The easiest way to run a local instance of TracEX is using the provided Docker images.

1. **Install Docker**: Ensure that you have Docker installed on your system. If you haven't installed it yet, please follow the official Docker installation guide for your operating system: Docker Installation.
1. **Download the Latest Docker Image**: Download the latest TracEX Docker image from the provided link: [docker image](...).
1. **Load the Docker Image**: Open a terminal or command prompt and navigate to the directory where you downloaded the Docker image file. Run the following command to load the image: `sudo docker load -i tracex.tar`\
Note: Depending on your system configuration, you may need to run this command with sudo privileges.
1. **Run the Docker Container**: After the image is successfully loaded, run the following command to start the TracEX container: `sudo docker run -p 8000:8000 tracex`\
This command will start the container and map port 8000 from the container to port 8000 on your local machine. Again, you may need to use sudo depending on your system setup.
1. **Access TracEX**: Open a web browser and navigate to http://localhost:8000/. This will bring you to the TracEX application, where you can enter your OpenAI Key and start extracting event logs.

## Local Setup for Development

### Download

- Use git and run "git clone https://github.com/bptlab/TracEX" in the desired directory _(Using e.g. Git Bash)_

### Installation
- navigate to the root directory of TracEX in your terminal
- run `install-dependencies-unix.sh` or `install-dependencies-windows.ps1`, based on your operating system _(Using e.g. Terminal)_
- run `python tracex_project/manage.py migrate` to update the database and apply all changes stored in the `migrations` folder

### Execution
- Run `python tracex_project/manage.py runserver` in the root directory of TracEX _(Using e.g. Terminal)_

### Pre-Commit

- If you intend on expanding the code, please run `pre-commit install` in the root directory of TracEX _(Using e.g. Terminal)_

## Contributors

The main contributors to the project are the six members of the [2023/24 Bachelor Project](https://hpi.de/fileadmin/user_upload/hpi/dokumente/studiendokumente/bachelor/bachelorprojekte/2023_24/BA-Projekt_FG_Weske_Event_Log_Extraction_from_Patient_Experiences.pdf) of Professor Weske's [Business Process Technology Chair](https://bpt.hpi.uni-potsdam.de) at the [Hasso Plattner Institute](https://hpi.de):

- [Pit Buttchereit](https://github.com/PitButtchereit)
- [Frederic Rupprecht](https://github.com/FR-SON)
- [VanThang Nguyen](https://github.com/thangixd)
- [Nils Schmitt](https://github.com/nils-schmitt)
- [Soeren Schubert](https://github.com/soeren227)
- [Trung-Kien Vu](https://github.com/tkv29)

These six participants will push the project forward as part of their bachelor's degree until the summer of 2024.  
At the same time our commitment to open source means that we are enabling -in fact encouraging- all interested parties to contribute and become part of its developer community. 

## Project documentation

In the project wiki, you can find detailed documentation that covers various aspects of TracEX.
In the [architecture](https://github.com/bptlab/TracEX/wiki/Architecture) section, we provide an overview of the system's design and components. The [repository structure](https://github.com/bptlab/TracEX/wiki/Repository-Structure) is also outlined, making it easier for you to navigate and understand the organization of our codebase.
Most importantly, we have dedicated a significant portion of the wiki to explaining our [pipeline frameworks](https://github.com/bptlab/TracEX/wiki/Pipelines), which are the core of TracEX. These frameworks are responsible for processing and transforming the unstructured patient journey data into structured event logs.
