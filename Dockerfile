# ============================================
# Dockerfile - Agent OpenShift IA (Accel Tech)
# Application: app_claude_v2.py
# ============================================

# --- Stage 1: Build (installation des dépendances) ---
FROM registry.access.redhat.com/ubi9/python-39 AS builder

WORKDIR /opt/app-root/src

# Copier et installer les dépendances Python
COPY requirements-app-claude.txt .
RUN pip install --no-cache-dir -r requirements-app-claude.txt

# --- Stage 2: Runtime ---
FROM registry.access.redhat.com/ubi9/python-39

LABEL maintainer="Accel Tech" \
      description="Agent OpenShift IA - Deploiement intelligent sur OpenShift" \
      version="2.0"

# Installer le client OpenShift (oc) en tant que root
USER 0
RUN curl -sL https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz \
    | tar xz -C /usr/local/bin oc kubectl \
    && chmod +x /usr/local/bin/oc /usr/local/bin/kubectl

WORKDIR /opt/app-root/src

# Copier les packages Python installés depuis le builder
COPY --from=builder /opt/app-root/lib /opt/app-root/lib

# Copier le fichier d'environnement
COPY .env .

# Copier le code source Python
COPY app_claude_v2.py .
COPY nvidia_nim_claude_agent.py .
COPY nvidia_nim_claude_agent_100_percent_ai.py .
COPY error_analyzer.py .

# Copier les fichiers statiques et templates
COPY static/ ./static/
COPY templates/ ./templates/

# Créer les dossiers nécessaires (permissions compatibles OpenShift / non-root)
RUN mkdir -p generated-deployments flask_session \
    && chown -R 1001:0 /opt/app-root/src \
    && chmod -R 775 generated-deployments flask_session \
    && chmod -R 755 static/ templates/

# Repasser en utiliscurlateur non-root (requis par OpenShift)
USER 1001

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    CLAUDE_PORT=5002

# Port exposé
EXPOSE 5002

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:5002/api/status || exit 1

# Lancement
CMD ["python", "app_claude_v2.py"]