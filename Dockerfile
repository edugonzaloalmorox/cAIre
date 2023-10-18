FROM python:3.11

WORKDIR /caire-app

COPY pyproject.toml poetry.lock /

RUN pip install poetry 

COPY . /src ./src/


EXPOSE 5000

CMD ["poetry", "run", "python", "./src/test.py"]