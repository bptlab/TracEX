# TracEX

[![GitHub stars](https://img.shields.io/github/stars/bptlab/TracEX)](https://github.com/bptlab/TracEX)
[![GitHub open issues](https://img.shields.io/github/issues/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub closed pull requests](https://img.shields.io/github/issues-closed/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub open pull requests](https://img.shields.io/github/issues-pr/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)

TracEX aims to extract event logs from unstructured text, specifically written patient experiences known as patient journeys. By leveraging Large Language Models (LLMs), TracEX can automatically identify and extract relevant events, activities, timestamps and further information from natural langauge text. This enables healthcare professionals and researchers to gain valuable insights into patient experiences, treatment pathways, and potential areas for improvement in healthcare delivery.

This project was initiated and completed as part of the team's bachelor's degree under the supervision of the Business Process Technology chair at the Hasso Plattner Institute. The project was conducted in cooperation with [mamahealth](https://www.mamahealth.io/).

## Key Features
- **Extraction Pipeline**: A robust pipeline to clean, process, and extract data from natural language text.
- **Patient Journey Generator**: Generates comprehensive patient journeys based on randomized cohort data.
- **Database**: Stores patient journeys and related extraction results for easy access and analysis.
- **Metrics and Evaluation Tool**: Evaluates the accuracy and effectiveness of the extraction process and allows for analysis of exctraction results.
- **Intuitive UI**: User-friendly interface for you to interact with the tool and visualize results.

## Installation using Docker
The easiest way to run a local instance of Ark is using the provided Docker images.

1. Make sure you have Docker installed and running.
1. Download the latest [docker image](...).
1. In your console, navigate to the directory of the downloaded file and run `docker-compose up`. You can add a `-d` to run Ark in the background.
1. [Install](https://github.com/bptlab/ark_automate_local#setup) and run the local client.
1. Navigate to http://localhost:3000/ to access the front-end and to start modeling RPA bots!
1. Do you already know our [tutorial](https://github.com/bptlab/ark_automate/wiki/tutorial)? It will guide you through the creation of your first RPA bot using Ark Automate!


## Local Setup for Development

### Download

- Use git and run "git clone https://github.com/bptlab/TracEX" in the desired directory _(Using e.g. Git Bash)_

### Installation
- navigate to the root directory of TracEX in your terminal
- run `install-dependencies-unix.sh` or `install-dependencies-windows.ps1`, based on your operating system _(Using e.g. Terminal)_
- run `python tracex/manage.py migrate` to update the database and apply all changes stored in the `migrations` folder

### Execution

**Web-App:**
- Run `python tracex/manage.py runserver` in the root directory of TracEX _(Using e.g. Terminal)_

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
In the [architecture](https://github.com/bptlab/TracEX/wiki/Architecture) section, we provide an overview of the system's design and components. The [repository structure] (https://github.com/bptlab/TracEX/wiki/Repository-Structure) is also outlined, making it easier for you to navigate and understand the organization of our codebase.
Most importantly, we have dedicated a significant portion of the wiki to explaining our [pipeline frameworks] (https://github.com/bptlab/TracEX/wiki/Pipelines), which are the core of TracEX. These frameworks are responsible for processing and transforming the unstructured patient journey data into structured event logs.
