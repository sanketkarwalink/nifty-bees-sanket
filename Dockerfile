FROM python:3.11-slim

# Avoid Python writing .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install tzdata so logs use IST by default (adjust if you prefer a different TZ)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Bring the app code and config (config can still be overridden by env vars)
COPY nifty_tracker.py web_runner.py config.json README.md email_setup_guide.md ./

# Default to headless for server environments
ENV HEADLESS=true

# Web entrypoint provides a health endpoint for Render free web service
CMD ["python", "web_runner.py"]
