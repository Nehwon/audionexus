#!/usr/bin/env python3
"""
Script de test de connectivité MySQL pour AudioNexus.

Ce script vérifie que la connexion à la base de données MySQL fonctionne correctement
et que tous les paramètres sont correctement configurés.
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mysql_connectivity():
    """Teste la connectivité MySQL en utilisant les paramètres d'environnement."""

    # Charger les variables d'environnement
    load_dotenv()

    # Récupérer les paramètres MySQL
    db_type = os.getenv('DB_TYPE', 'sqlite').lower()
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_user = os.getenv('DB_USER', 'audionexus')
    db_password = os.getenv('DB_PASSWORD', 'audionexus')
    db_name = os.getenv('DB_NAME', 'audionexus')

    logger.info("Configuration détectée:")
    logger.info(f"  Type DB: {db_type}")
    logger.info(f"  Host: {db_host}")
    logger.info(f"  Port: {db_port}")
    logger.info(f"  User: {db_user}")
    logger.info(f"  Database: {db_name}")

    if db_type != 'mysql':
        logger.warning(f"Le type de base de données est configuré sur '{db_type}', pas sur 'mysql'.")
        db_type = 'mysql'  # Force MySQL pour le test
        logger.info("Forçage du type MySQL pour le test de connectivité.")

    try:
        # Construire l'URL de connexion
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        logger.info(f"Test de connexion à: mysql+pymysql://{db_user}:***@{db_host}:{db_port}/{db_name}")

        # Créer le moteur SQLAlchemy
        engine = create_engine(database_url, echo=False)

        # Tester la connexion
        with engine.connect() as connection:
            # Exécuter une requête simple pour vérifier la connexion
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            logger.info(f"✅ Connexion réussie! Version MySQL: {version}")

            # Tester les informations de la base de données
            result = connection.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()[0]
            logger.info(f"✅ Base de données active: {current_db}")

            # Tester les tables existantes
            result = connection.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            logger.info(f"📋 Tables dans la base de données: {[table[0] for table in tables]}")

            # Tester les permissions (insertion)
            try:
                connection.execute(text("CREATE TABLE IF NOT EXISTS test_connectivity (id INT PRIMARY KEY, test_value VARCHAR(50))"))
                connection.execute(text("INSERT INTO test_connectivity (id, test_value) VALUES (1, 'test_value')"))
                connection.execute(text("DROP TABLE test_connectivity"))
                connection.commit()
                logger.info("✅ Permissions d'écriture vérifiées.")
            except Exception as e:
                logger.error(f"❌ Erreur lors du test d'écriture: {e}")
                return False

        logger.info("🎉 Test de connectivité MySQL réussi!")
        return True

    except SQLAlchemyError as e:
        logger.error(f"❌ Erreur SQLAlchemy: {e}")
        logger.info("\n🔧 Conseils de dépannage:")
        logger.info("1. Vérifiez que MySQL est en cours d'exécution:")
        logger.info("   sudo systemctl status mysql")
        logger.info("2. Vérifiez les paramètres de connexion dans .env:")
        logger.info(f"   - DB_HOST={db_host}")
        logger.info(f"   - DB_PORT={db_port}")
        logger.info(f"   - DB_USER={db_user}")
        logger.info(f"   - DB_NAME={db_name}")
        logger.info("3. Créez l'utilisateur MySQL si nécessaire:")
        logger.info(f"   CREATE USER '{db_user}'@'%' IDENTIFIED BY '{db_password}';")
        logger.info(f"   GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'%';")
        logger.info("   FLUSH PRIVILEGES;")
        return False

    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        return False

def main():
    """Fonction principale."""
    print("🔧 Test de connectivité MySQL pour AudioNexus")
    print("=" * 50)

    success = test_mysql_connectivity()

    if success:
        print("\n✅ Le test de connectivité MySQL s'est terminé avec succès!")
        print("Votre configuration MySQL est correcte.")
        sys.exit(0)
    else:
        print("\n❌ Le test de connectivité MySQL a échoué.")
        print("Vérifiez les messages d'erreur ci-dessus pour le dépannage.")
        sys.exit(1)

if __name__ == "__main__":
    main()