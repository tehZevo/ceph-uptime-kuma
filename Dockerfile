FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --progress-bar off -r requirements.txt

COPY . .

EXPOSE 80

CMD [ "python", "-u", "main.py" ]
