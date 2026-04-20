"""
Point d'entrée WSGI pour le déploiement de l'application AudioNexus.
"""
import os
from app import create_app

# Crée l'application en utilisant la configuration par défaut
app = create_app()

# Pour l'exécution directe avec Gunicorn
if __name__ == "__main__":
    # Pour le développement
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        debug=app.config["DEBUG"]
    )

# Pour Gunicorn
application = app
