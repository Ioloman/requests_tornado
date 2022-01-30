FROM python:3.10.2

WORKDIR /usr/src/requests_app

COPY . .

RUN pip install pipenv
RUN pipenv install

EXPOSE ${APP_PORT}

CMD pipenv run python server.py