FROM python:3.7

# Set workspace
WORKDIR /app

# Install python dependencies
COPY requirements.txt . 
RUN pip install -r requirements.txt 

# Copy local files
COPY . .

RUN python main.py
