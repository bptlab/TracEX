#!/bin/bash

sudo apt-get update && apt-get upgrade -y
sudo apt install python3 graphviz -y

# add Graphviz to the system path
echo 'export PATH=$PATH:/usr/local/bin/graphviz' >> ~/.bashrc
source ~/.bashrc

pip install -r requirements.txt
