#!/bin/bash

sudo apt-get update && apt-get upgrade -y

sudo apt install python3 graphviz -y

pip install -r requirements.txt

