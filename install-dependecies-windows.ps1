# install packages needed for using TracEX
winget install Python --accept-source-agreements --accept-package-agreements
winget install graphviz --accept-source-agreements --accept-package-agreements

# install python packages
pip install -r .\requirements.txt