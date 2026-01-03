# ============================================
# Dockerfile pour le Backend Flask
# LogStream Studio - E-Commerce Analytics
# ============================================

# Image de base Python légère
FROM python:3.14-slim

# Métadonnées
LABEL maintainer="DorraMn"
LABEL description="Flask Backend for LogStream Studio"
LABEL version="1.0"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer le dossier uploads avec les bonnes permissions
RUN mkdir -p /app/uploads && chmod 777 /app/uploads

# Exposer le port
EXPOSE 8000

# Healthcheck pour vérifier que l'app fonctionne (endpoint public)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Commande de démarrage
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
