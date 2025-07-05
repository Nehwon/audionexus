from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
import asyncio

# Ajouter le répertoire de l'application au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importer les modèles SQLAlchemy et la configuration
from app.db.models.base import Base
from app.config import settings
from app.db.session_manager import async_engine, init_async_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpréter le fichier de configuration pour la journalisation Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Définir les métadonnées cibles pour 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # S'assurer que le moteur asynchrone est initialisé
    if async_engine is None:
        init_async_engine()
    
    # Utiliser le moteur asynchrone de session_manager
    connectable = async_engine
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Run migrations in the current transaction."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
