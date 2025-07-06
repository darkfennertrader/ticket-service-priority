FROM python:3.12.11

# Prevent Python from writing .pyc files and buffering stdout/err
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /srv

# Install system packages only if you need them (none for this demo).
# RUN apt-get update && apt-get install -y gcc build-essential ...

# ---------- Python deps ----------
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---------- Application code -----
COPY ./app ./app

# Uvicorn will listen on 0.0.0.0:8000 inside the container
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]