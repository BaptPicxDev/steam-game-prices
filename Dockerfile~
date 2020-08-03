FROM python:2.7.16
RUN apt-get update

# Install python dependencies
COPY requirements_rasp.txt requirements_rasp.txt 
RUN pip install -r ./requirements_rasp.txt 

# Environment
ENV APP_HOME /app

# Set workspace
WORKDIR ${APP_HOME}

# Copy local files
COPY . .

RUN ['python', 'main.py']
