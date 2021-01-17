FROM python:3.9-alpine
LABEL maintainer="Josef Vogt"

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./ipupdater.py" ]
