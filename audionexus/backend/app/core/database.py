import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ne pas ajouter de gestionnaires supplémentaires s'ils existent déjà
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.propagate = False  # Éviter la propagation vers le logger racine pour éviter les doublons

# URL de connexion à la base de données
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Création du moteur SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles
Base = declarative_base()

def get_db():
    """
    Fournit une session de base de données pour chaque requête.
    La session est automatiquement fermée après utilisation.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    À utiliser avec précaution en production.
    """
    print("\n" + "="*80)
    print("DÉBUT DE L'INITIALISATION DE LA BASE DE DONNÉES")
    print("="*80 + "\n")
    
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Création des tables terminée avec succès\n")
    
    # Afficher les informations de connexion pour le débogage
    print(f"Informations de connexion à la base de données:")
    print(f"- URL: {settings.DATABASE_URL}")
    print(f"- Email admin: {settings.FIRST_SUPERUSER_EMAIL}")
    print(f"- Mot de passe admin: {'*' * len(settings.FIRST_SUPERUSER_PASSWORD) if settings.FIRST_SUPERUSER_PASSWORD else 'Non défini'}\n")
    
    # Créer l'utilisateur admin si nécessaire
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.services.auth import AuthService
        from app.schemas.user import UserCreate
        
        print(f"Recherche de l'utilisateur admin avec l'email: {settings.FIRST_SUPERUSER_EMAIL}")
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        
        if not admin:
            print("Aucun admin trouvé, création d'un nouvel utilisateur admin...")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Admin",
                is_superuser=True,
                is_active=True
            )
            print(f"Données de l'utilisateur à créer: {user_in}")
            
            try:
                print("Appel de AuthService.create_user...")
                admin_user = AuthService.create_user(db, user_in)
                print("Commit des changements...")
                db.commit()  # S'assurer que les changements sont bien commités
                print(f"✓ Utilisateur admin créé avec succès: {admin_user}")
                
                # Vérifier que l'utilisateur a bien été créé
                admin_verif = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
                if admin_verif:
                    print(f"✓ Vérification réussie: utilisateur {admin_verif.email} existe dans la base de données")
                else:
                    print("✗ ERREUR: L'utilisateur n'a pas été trouvé après création")
                    
            except Exception as create_error:
                print(f"✗ ERREUR lors de la création de l'utilisateur admin: {create_error}")
                import traceback
                traceback.print_exc()
                db.rollback()  # Annuler les changements en cas d'erreur
                raise
        else:
            print(f"✓ Utilisateur admin existant trouvé: {admin.email} (ID: {admin.id})")
            
    except Exception as e:
        print(f"\n✗ ERREUR CRITIQUE lors de l'initialisation de la base de données: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
        print("\n" + "="*80)
        print("FIN DE L'INITIALISATION DE LA BASE DE DONNÉES")
        print("="*80 + "\n\n")
