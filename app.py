from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
        <head><title>Hello OpenShift</title></head>
        <body style="text-align: center; padding: 50px; font-family: Arial;">
            <h1>🎉 Hello World from OpenShift! 🎉</h1>
            <p>Application déployée avec succès par l'Agent IA</p>
            <p>Version Python: 3.11</p>
        </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
