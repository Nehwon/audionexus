#!/usr/bin/env python3
"""
Exemple d'utilisation du client Audiobookshelf API.

Ce script montre comment utiliser le client pour interagir avec un serveur Audiobookshelf.
"""
import os
from dotenv import load_dotenv
from app.api.audiobookshelf import AudiobookshelfClient

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Configuration
    BASE_URL = os.getenv('AUDIOBOOKSHELF_URL', 'http://localhost:13378')
    USERNAME = os.getenv('AUDIOBOOKSHELF_USERNAME', 'admin')
    PASSWORD = os.getenv('AUDIOBOOKSHELF_PASSWORD', 'password')
    
    try:
        # Initialiser le client
        client = AudiobookshelfClient(BASE_URL, USERNAME, PASSWORD)
        print("✓ Connexion réussie à Audiobookshelf")
        
        # Afficher les informations de l'utilisateur connecté
        if client.user:
            print(f"\nUtilisateur connecté: {client.user.get('username')}")
            print(f"Rôle: {client.user.get('type')}")
        
        # Récupérer la liste des bibliothèques
        print("\nBibliothèques disponibles:")
        libraries = client.get_libraries()
        for lib in libraries:
            print(f"- {lib['name']} (ID: {lib['id']})")
        
        # Si des bibliothèques sont disponibles, afficher les livres récents
        if libraries:
            library_id = libraries[0]['id']
            print(f"\nLivres récemment ajoutés dans {libraries[0]['name']}:")
            recent_books = client.get_recently_added(limit=5)
            
            for i, book in enumerate(recent_books, 1):
                print(f"{i}. {book.get('title')} - {book.get('author')}")
        
        # Afficher les collections
        print("\nCollections disponibles:")
        collections = client.get_collections()
        for col in collections[:5]:  # Limiter à 5 collections
            print(f"- {col['name']} ({len(col.get('books', []))} livres)")
        
        # Afficher les tâches en cours
        print("\nTâches en cours:")
        tasks = client.get_tasks()
        for task in tasks:
            print(f"- {task['name']}: {task['status']}")
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"Réponse du serveur: {e.response.text}")

if __name__ == "__main__":
    main()
