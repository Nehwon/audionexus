"""
Routes d'authentification pour l'API.
"""
from __future__ import annotations
from datetime import timedelta
from typing import Any, Dict, TYPE_CHECKING, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.config import settings

# Import différé pour éviter les imports circulaires
if TYPE_CHECKING:
    from app.db.models.base import User, UserInDB, Token
    from app import crud, models

# Modèle UserCreate local pour éviter les imports circulaires
class UserCreate(BaseModel):
    """Modèle Pydantic pour la création d'un utilisateur."""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "securepassword",
                "full_name": "John Doe"
            }
        }
    }

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login/access-token", response_model=Dict[str, str])
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(deps.get_async_db)
) -> Dict[str, str]:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Accepts both form data and JSON input.
    """
    content_type = request.headers.get("Content-Type", "")
    
    if "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
    else:
        try:
            json_data = await request.json()
            login_data = LoginRequest(**json_data)
            username = login_data.username
            password = login_data.password
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid request data format"
            )
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required"
        )
    
    user = await crud.crud_user.authenticate_user(
        db, username=username, password=password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/login/test-token", response_model='UserInDB')
async def test_token(current_user: 'models.User' = Depends(deps.get_current_user)) -> Any:
    """
    Test access token.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Test token endpoint called with user: {current_user.username}")
    return current_user

import logging

logger = logging.getLogger(__name__)

@router.post("/register", response_model=Dict[str, Any])
async def create_user(
    request: Request,
    user_in: UserCreate = Body(...),
    db: AsyncSession = Depends(deps.get_async_db_session),
) -> Dict[str, Any]:
    """
    Create new user.
    """
    import inspect
    import logging
    
    # Configuration du logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Création d'un handler pour afficher les logs dans la console
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("=== DÉBUT DE LA FONCTION CREATE_USER ===")
    logger.info(f"URL de la requête: {request.url}")
    logger.info(f"Méthode de la requête: {request.method}")
    logger.info(f"En-têtes de la requête: {request.headers}")
    logger.info(f"Données de l'utilisateur: {user_in.dict()}")
    
    # Vérification de la session de base de données
    if db is None:
        logger.error("La session de base de données est None!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur de configuration de la base de données"
        )
    
    logger.info(f"Type de la session DB: {type(db)}")
    logger.info(f"ID de la session DB: {id(db)}")
    logger.info(f"Signature de la fonction de dépendance: {inspect.signature(deps.get_async_db_session)}")
    logger.info(f"Type du user_in: {type(user_in)}")
    
    try:
        # Vérifier si l'email existe déjà
        logger.info("Vérification de l'unicité de l'email...")
        try:
            existing_user = await crud.crud_user.get_user_by_email(db, email=user_in.email)
            logger.info(f"Résultat de la recherche par email: {existing_user}")
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par email: {str(e)}", exc_info=True)
            raise
        if existing_user:
            logger.warning(f"Tentative de création d'un utilisateur avec un email existant: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
            
        # Vérifier si le nom d'utilisateur existe déjà
        logger.info("Vérification de l'unicité du nom d'utilisateur...")
        try:
            existing_user = await crud.crud_user.get_user_by_username(db, username=user_in.username)
            logger.info(f"Résultat de la recherche par nom d'utilisateur: {existing_user}")
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par nom d'utilisateur: {str(e)}", exc_info=True)
            raise
        if existing_user:
            logger.warning(f"Tentative de création d'un utilisateur avec un nom d'utilisateur existant: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this username already exists in the system.",
            )
        
        # Créer un nouvel utilisateur
        logger.info("Création du nouvel utilisateur...")
        try:
            logger.info(f"Données de l'utilisateur avant création: {user_in.dict()}")
            user = await crud.crud_user.create_user(db=db, user=user_in)
            logger.info(f"Utilisateur créé avec succès: ID={user.id}, Email={user.email}")
            logger.info(f"Détails de l'utilisateur créé: {vars(user)}")
        except Exception as e:
            logger.error(f"ERREUR CRITIQUE lors de la création de l'utilisateur: {str(e)}", exc_info=True)
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Une erreur est survenue lors de la création de l'utilisateur: {str(e)}"
            )
        
        # Convertir l'utilisateur en dictionnaire pour la réponse
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        }
        
        logger.info(f"Utilisateur enregistré avec succès: {user_dict}")
        
        # Valider que l'utilisateur est bien en base de données
        try:
            db_user = await crud.crud_user.get_user(db=db, user_id=user.id)
            if db_user:
                logger.info("VÉRIFICATION: L'utilisateur a bien été trouvé en base de données après création")
            else:
                logger.error("ERREUR: L'utilisateur n'a pas été trouvé en base de données après création!")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'utilisateur en base de données: {str(e)}")
        
        logger.info("=== FIN DE LA FONCTION CREATE_USER AVEC SUCCÈS ===")
        return user_dict
        
    except HTTPException as he:
        # On relance les HTTPException telles qu'elles
        logger.error(f"ERREUR HTTP {he.status_code} lors de la création de l'utilisateur: {he.detail}")
        logger.info("=== FIN DE LA FONCTION CREATE_USER AVEC ERREUR HTTP ===")
        await db.rollback()
        raise he
    except Exception as e:
        # On capture toutes les autres exceptions pour éviter une fuite d'informations
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"ERREUR INATTENDUE lors de la création de l'utilisateur: {str(e)}\n{error_traceback}")
        logger.info("=== FIN DE LA FONCTION CREATE_USER AVEC ERREUR INATTENDUE ===")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur inattendue est survenue lors de la création de l'utilisateur: {str(e)}"
        )
