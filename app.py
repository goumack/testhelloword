#!/usr/bin/env python3
"""
Application de test pour déploiement OpenShift
Exemple de déploiement d'une application Python utilisant un modèle OCR ACCEL TECH
"""

from flask import Flask, render_template_string, request
import os
import base64
import requests
from datetime import datetime

app = Flask(__name__)

# Template HTML simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACCEL TECH OCR | Enterprise Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            --accel-green: #76b900;
            --primary-dark: #1a1a1a;
            --secondary-gray: #f8f9fa;
        }
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f4f6f9;
            color: #333;
        }
        .navbar {
            background-color: var(--primary-dark);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            color: white !important;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .brand-logo {
            color: var(--accel-green);
            font-size: 1.5rem;
        }
        .main-container {
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.05);
            margin-bottom: 30px;
            overflow: hidden;
        }
        .card-header {
            background-color: white;
            border-bottom: 1px solid #eee;
            padding: 20px 30px;
            font-weight: 600;
            font-size: 1.1rem;
        }
        .upload-zone {
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background-color: #fafafa;
        }
        .upload-zone:hover, .upload-zone.dragover {
            border-color: var(--accel-green);
            background-color: #f0f9eb;
        }
        .upload-icon {
            font-size: 3rem;
            color: #adb5bd;
            margin-bottom: 15px;
        }
        .btn-primary {
            background-color: var(--accel-green);
            border-color: var(--accel-green);
            padding: 10px 30px;
            font-weight: 600;
        }
        .btn-primary:hover {
            background-color: #66a300;
            border-color: #66a300;
        }
        .result-content {
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            border: 1px solid #eee;
        }
        .meta-badge {
            background-color: #e9ecef;
            color: #495057;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            margin-right: 10px;
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.9);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            flex-direction: column;
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
            color: var(--accel-green);
        }
        /* Markdown Styles */
        .markdown-body h1, .markdown-body h2 { border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
        .markdown-body table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        .markdown-body th, .markdown-body td { border: 1px solid #dfe2e5; padding: 6px 13px; }
        .markdown-body tr:nth-child(2n) { background-color: #f6f8fa; }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <img src="{{ url_for('static', filename='images/accel-logo.png') }}" alt="ACCEL TECH" style="height: 40px; background-color: white; padding: 5px; border-radius: 5px;">
            </a>
            <span class="navbar-text text-white-50">
                Powered by ACCEL TECH AI
            </span>
        </div>
    </nav>

    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner-border" role="status"></div>
        <h4 class="mt-3">Analyse en cours...</h4>
        <p class="text-muted">Le modèle ACCEL TECH Vision traite votre document</p>
    </div>

    <div class="main-container">
        
        <!-- Intro Section -->
        <div class="row mb-4">
            <div class="col-md-12 text-center">
                <h2 class="fw-bold mb-3">Extraction Intelligente de Documents</h2>
                <p class="text-muted lead">
                    Utilisez la puissance des modèles de vision générative pour extraire et structurer le contenu de vos documents.
                </p>
            </div>
        </div>

        <!-- Upload Card -->
        <div class="card">
            <div class="card-header">
                <i class="fas fa-cloud-upload-alt me-2"></i> Nouveau Document
            </div>
            <div class="card-body">
                <form method="post" enctype="multipart/form-data" id="uploadForm">
                    <div class="upload-zone" id="dropZone">
                        <i class="fas fa-file-image upload-icon"></i>
                        <h4>Glissez votre image ici</h4>
                        <p class="text-muted">ou cliquez pour parcourir vos fichiers</p>
                        <input type="file" name="image" id="fileInput" accept="image/*" style="display: none;" required>
                        <div id="fileName" class="mt-3 fw-bold text-primary"></div>
                    </div>
                    <div class="text-center mt-4">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="fas fa-magic me-2"></i> Lancer l'Analyse
                        </button>
                    </div>
                </form>
            </div>
        </div>

        {% if ocr_result %}
        <!-- Results Card -->
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span><i class="fas fa-poll-h me-2"></i> Résultat de l'Analyse</span>
                <span class="badge bg-success">Confiance: {{ "%.0f"|format(ocr_result.confidence_score * 100) }}%</span>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-12">
                        <div class="result-content markdown-body" id="markdownResult">
                            {{ ocr_result.detected_text }}
                        </div>
                    </div>
                </div>
                
                <hr class="my-4">
                
                <div class="row g-3">
                    <div class="col-md-3">
                        <small class="text-muted d-block">Modèle</small>
                        <strong>{{ ocr_result.model }}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Technologie</small>
                        <strong>ACCEL TECH AI</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Temps de traitement</small>
                        <strong>{{ current_time }}</strong>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Statut</small>
                        <span class="text-success"><i class="fas fa-check-circle"></i> Terminé</span>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

    </div>

    <script>
        // Drag and Drop Logic
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileName = document.getElementById('fileName');
        const uploadForm = document.getElementById('uploadForm');
        const loadingOverlay = document.getElementById('loadingOverlay');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileName();
            }
        });

        fileInput.addEventListener('change', updateFileName);

        function updateFileName() {
            if (fileInput.files.length) {
                fileName.textContent = 'Fichier sélectionné : ' + fileInput.files[0].name;
            }
        }

        uploadForm.addEventListener('submit', () => {
            if (fileInput.files.length) {
                loadingOverlay.style.display = 'flex';
            }
        });

        // Render Markdown if result exists
        const markdownResult = document.getElementById('markdownResult');
        if (markdownResult) {
            const rawText = markdownResult.textContent;
            markdownResult.innerHTML = marked.parse(rawText);
        }
    </script>
</body>
</html>
"""


def process_ocr_with_accel(image_bytes, filename):
    """
    Fonction pour l'intégration ACCEL TECH OCR via VLM.
    Utilise un modèle de vision (Llama 3.2 Vision) pour extraire le texte.
    
    Args:
        image_bytes (bytes): Contenu de l'image
        filename (str): Nom du fichier
        
    Returns:
        dict: Résultat de l'OCR
    """
    # Clé API fournie ou depuis l'environnement
    api_key = os.environ.get("ACCEL_API_KEY", "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")
    
    # Endpoint pour Llama 3.2 11B Vision Instruct (excellent pour l'OCR)
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    # Encodage de l'image en base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    payload = {
        "model": "meta/llama-3.2-11b-vision-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract all text from this image. Output only the detected text, nothing else."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
        "top_p": 1.00
    }
    
    print(f"Envoi de la requête à ACCEL TECH: {invoke_url}")
    
    try:
        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        detected_text = result['choices'][0]['message']['content']
        
        return {
            "status": "success",
            "model": "meta/llama-3.2-11b-vision-instruct",
            "detected_text": detected_text,
            "confidence_score": 0.95 # Estimation pour VLM
        }
    except Exception as e:
        print(f"Erreur lors de l'appel API: {str(e)}")
        return {
            "status": "error",
            "model": "meta/llama-3.2-11b-vision-instruct",
            "detected_text": f"Erreur lors de l'analyse: {str(e)}",
            "confidence_score": 0.0
        }

@app.route('/', methods=['GET', 'POST'])
def hello():
    """Page d'accueil avec message de bienvenue et traitement OCR"""
    import sys
    import socket
    import flask

    ocr_result = None
    if request.method == 'POST':
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                # Lecture du contenu de l'image pour l'envoi à l'API
                image_bytes = image_file.read()
                ocr_result = process_ocr_with_accel(image_bytes, image_file.filename)

    return render_template_string(
        HTML_TEMPLATE,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        hostname=socket.gethostname(),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ocr_result=ocr_result
    )

@app.route('/health')
def health():
    """Endpoint de santé pour les health checks OpenShift"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Application is running'
    }, 200

@app.route('/ready')
def ready():
    """Endpoint de readiness pour OpenShift"""
    return {
        'status': 'ready',
        'timestamp': datetime.now().isoformat()
    }, 200

if __name__ == '__main__':
    # Port par défaut : 8080 (OpenShift standard)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
