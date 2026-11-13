FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY main.py ./
COPY front-init ./front-init

EXPOSE 3000 5000

CMD ["uv", "run", "main.py"]
