FROM python:3.10.4

ENV POETRY_VIRTUALENVS_CREATE=false
ENV JISHAKU_NO_UNDERSCORE=true

RUN apt-get update; \
    apt-get upgrade -y; \
    apt-get install neofetch -y; \
    pip install --upgrade pip; \
    pip install "poetry==1.1.13"; \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*;

WORKDIR /bot/

COPY ./pyproject.toml /bot/

RUN poetry install;

COPY . .

ENTRYPOINT [ "python", "main.py" ]