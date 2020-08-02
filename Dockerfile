FROM python:2.7.16
WORKDIR /usr/local/bin
ADD . 
RUN pip install -r requirements_rasp.txt
RUN ['python', 'main.py']
