# base image
FROM ubuntu:latest

# set environment variables
ENV PYTHONUNBUFFERED=1

# set working directory
ENV DockerHOME=/home/app/TracEX
RUN mkdir -p $DockerHOME 
WORKDIR $DockerHOME

# copy source files
COPY . $DockerHOME 

# expose port
EXPOSE 8000

# install dependencies
RUN apt-get update && apt-get install -y python3 graphviz python3-pip
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

# start server  
CMD ["python3", "tracex_project/manage.py", "runserver", "0.0.0.0:8000"]