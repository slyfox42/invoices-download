FROM python:3

WORKDIR /root

COPY Pipfile .
COPY Pipfile.lock .
RUN apt-get update

RUN apt-get update && apt-get -y install poppler-utils && apt-get clean

RUN pip install pipenv
RUN pipenv sync

COPY . .

CMD ["pipenv", "run", "python", "download.py"]
