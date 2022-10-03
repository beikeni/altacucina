FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app/
RUN pip install -r requirements.txt
COPY . /opt/app/
