FROM python:3.11

WORKDIR /app

# Install system dependencies including Redis and ffmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    redis-server \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install pip dependencies and handle ffmpeg package issue
RUN pip install --upgrade pip && \
    pip install wheel setuptools setuptools-rust && \
    grep -v "^ffmpeg$" requirements.txt > requirements_without_ffmpeg.txt && \
    pip install --no-cache-dir -r requirements_without_ffmpeg.txt

COPY . .
EXPOSE 3657 6380

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]