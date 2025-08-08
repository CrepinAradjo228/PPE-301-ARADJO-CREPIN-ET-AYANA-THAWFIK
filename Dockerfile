FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y gcc postgresql-client

# Copier les dépendances et installer les packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet dans /app
COPY . .

# Ouvrir le port 8000
EXPOSE 8000

# Lancer les migrations et le serveur gunicorn
CMD ["sh", "-c", "python PPE301/manage.py migrate && gunicorn PPE301.wsgi:application --bind 0.0.0.0:8000"]
