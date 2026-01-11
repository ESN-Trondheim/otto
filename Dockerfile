FROM ghcr.io/astral-sh/uv:python3.14-trixie

# Install browser used by html2image package
RUN apt-get update && apt-get install -y chromium

# Import project files
WORKDIR /app
COPY . /app

# Build project in production mode
ENV UV_NO_DEV=1
RUN uv sync --locked

CMD ["uv", "run", "main.py"]