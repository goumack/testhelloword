FROM registry.access.redhat.com/ubi9/python-39

# Définir le répertoire de travail
WORKDIR /opt/app-root/src

# Copier les fichiers de l'application
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8080

# Définir la commande pour lancer l'application
CMD ["python", "app.py"]