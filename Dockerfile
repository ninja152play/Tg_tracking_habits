FROM python:3.13

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

COPY . .

CMD ["bash"]