# install packages needed for using TracEX
winget install Python --accept-source-agreements --accept-package-agreements
winget install graphviz --accept-source-agreements --accept-package-agreements


# add Graphviz to the system path
$graphvizPath = "C:\Program Files\Graphviz\bin"
$envPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
if (-not ($envPath).Contains($graphvizPath)) {
    [Environment]::SetEnvironmentVariable("Path", $envPath + ";" + $graphvizPath, [EnvironmentVariableTarget]::Machine)
}

# install python packages
pip install -r .\requirements.txt
