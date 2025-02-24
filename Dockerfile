FROM python:3.11

WORKDIR /app

# Install system dependencies including Redis
RUN apt-get update && apt-get install -y \
    build-essential \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3657 6380

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]