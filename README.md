# TracEX

[![GitHub stars](https://img.shields.io/github/stars/bptlab/TracEX)](https://github.com/bptlab/TracEX)
[![GitHub open issues](https://img.shields.io/github/issues/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub closed pull requests](https://img.shields.io/github/issues-closed/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)
[![GitHub open pull requests](https://img.shields.io/github/issues-pr/bptlab/TracEX)](https://github.com/bptlab/TracEX/issues)


## Key Points

This bachelorproject focuses on event log extraction from patient journeys using large-language models.

Our project partner is mamahealth. More information about them can be found here: [mamahealth](https://www.mamahealth.io/)

More information about the project will be released soon.


## Set Up Guide

### Download

- Use git and run "git clone https://github.com/bptlab/TracEX" in the desired directory _(Using e.g. Git Bash)_

### Installation
- navigate to the root directory of TracEX in your terminal
- run `install-dependencies-unix.sh` or `install-dependencies-windows.ps1`, based on your operating system _(Using e.g. Terminal)_
- run `python tracex/manage.py migrate` to update the database and apply all changes stored in the `migrations` folder

### Execution

**Web-App:**
- Run `python tracex/manage.py runserver` in the root directory of TracEX _(Using e.g. Terminal)_

**Command-Line Tool:**
- Run `python command_line_tool.py` in the root directory of TracEX _(Using e.g. Terminal)_

### Pre-Commit

- If you intend on expanding the code, please run `pre-commit install` in the root directory of TracEX _(Using e.g. Terminal)_



## Set Up Guide

### Download

- Use git and run "git clone https://github.com/bptlab/TracEX" in the desired directory _(Using e.g. Git Bash)_

### Installation
- navigate to the root directory of TracEX in your terminal
- run `install-dependencies-unix.sh` or `install-dependencies-windows.ps1`, based on your operating system _(Using e.g. Terminal)_
- run `python tracex/manage.py migrate` to update the database and apply all changes stored in the `migrations` folder

### Execution

**Web-App:**
- Run `python tracex/manage.py runserver` in the root directory of TracEX _(Using e.g. Terminal)_

**Command-Line Tool:**
- Run `python command_line_tool.py` in the root directory of TracEX _(Using e.g. Terminal)_

### Pre-Commit

- If you intend on expanding the code, please run `pre-commit install` in the root directory of TracEX _(Using e.g. Terminal)_
