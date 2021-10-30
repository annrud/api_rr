FROM python:3.8.5

RUN mkdir /code

COPY requirements.txt /code

RUN python3 -m pip install --upgrade pip

RUN pip3 install -r /code/requirements.txt

COPY . /code

WORKDIR /code
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000