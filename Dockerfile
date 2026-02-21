FROM python:3.12-slim

# Reduce RAM usage (important for Back4app free tier)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy all your files into the container
COPY . /app

# Install Telethon only (very small)
RUN pip install --no-cache-dir -r requirements.txt

# Start your bridge
CMD ["python", "bridge.py"]

EXPOSE 80
