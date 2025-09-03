import os
import multiprocessing

# Nom de l'application WSGI
wsgi_app = "wsgi:app"

# Nombre de workers
workers = multiprocessing.cpu_count() * 2 + 1

# Nombre de threads par worker
threads = 2

# Adresse et port d'écoute
bind = "0.0.0.0:8000"

# Désactiver le rechargement automatique en production
reload = False

# Niveau de log
loglevel = "info"

# Fichiers de log
accesslog = "-"
errorlog = "-"

# Configuration du timeout
timeout = 30
keepalive = 2

# Configuration pour les connexions
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Configuration du worker
worker_class = "gthread"
worker_tmp_dir = "/dev/shm"

# Configuration de sécurité
# Empêche l'exécution de code arbitraire
preload_app = True

# Configuration des en-têtes HTTP optimisée pour la sécurité
# Restreindre les IPs autorisées pour les proxies (à configurer selon l'environnement)
forwarded_allow_ips = os.getenv('FORWARDED_ALLOW_IPS', '127.0.0.1,localhost')
proxy_allow_ips = os.getenv('PROXY_ALLOW_IPS', '127.0.0.1,localhost')
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTOCOL': 'https',
    'X-FORWARDED-SSL': 'on'
}
