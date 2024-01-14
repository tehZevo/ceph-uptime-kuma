FROM python:3.10

WORKDIR /app

RUN mkdir -p /app/models

RUN apt-get update
RUN apt-get update && apt-get install libgl1 -y
RUN apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev -y
RUN apt-get install git -y
RUN pip install --upgrade pip
COPY requirements.txt .
#TODO: split some requirements out as this pulls in torch+cudnn etc all in this one line...
RUN pip install -r requirements.txt

COPY . .

EXPOSE 80
VOLUME ["/app/models"]

CMD [ "python", "-u", "main.py" ]
