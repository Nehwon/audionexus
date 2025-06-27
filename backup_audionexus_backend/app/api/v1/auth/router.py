from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, User, Token, TokenData
from app.services.auth import AuthService
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
) -> Token:
    """
    Authentifie un utilisateur et renvoie des jetons d'accès et de rafraîchissement.
    
    Args:
        form_data: Données de formulaire contenant le nom d'utilisateur et le mot de passe
        db: Session de la base de données
        
    Returns:
        Token: Jetons d'accès et de rafraîchissement
        
    Raises:
        HTTPException: En cas d'échec de l'authentification
    """
    try:
        logger.info("Tentative de connexion", extra={"username": form_data.username})
        
        user = AuthService.authenticate_user(
            db, 
            email=form_data.username,  # OAuth2PasswordRequestForm utilise 'username' pour l'email
            password=form_data.password
        )
        
        if not user:
            logger.warning("Échec de l'authentification: identifiants invalides", 
                         extra={"username": form_data.username})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning("Tentative de connexion d'un compte désactivé", 
                         extra={"user_id": user.id, "email": user.email})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce compte est désactivé"
            )
        
        logger.info("Connexion réussie", extra={"user_id": user.id, "email": user.email})
        return AuthService.create_tokens(db, user)
        
    except HTTPException:
        raise  # Relance les erreurs HTTP déjà gérées
        
    except Exception as e:
        logger.error("Erreur inattendue lors de la connexion", 
                    exc_info=True, 
                    extra={"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors de l'authentification"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True, description="Jeton de rafraîchissement"),
    db: Annotated[Session, Depends(get_db)] = None
) -> Token:
    """
    Rafraîchit un jeton d'accès à l'aide d'un jeton de rafraîchissement.
    
    Args:
        refresh_token: Le jeton de rafraîchissement
        db: Session de la base de données
        
    Returns:
        Token: Nouveaux jetons d'accès et de rafraîchissement
        
    Raises:
        HTTPException: Si le jeton de rafraîchissement est invalide ou expiré
    """
    try:
        logger.debug("Tentative de rafraîchissement de jeton")
        
        user = AuthService.verify_refresh_token(db, refresh_token)
        if not user:
            logger.warning("Tentative de rafraîchissement avec un jeton invalide ou expiré")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Jeton de rafraîchissement invalide ou expiré",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Rafraîchissement de jeton réussi", 
                   extra={"user_id": user.id, "email": user.email})
        return AuthService.create_tokens(db, user)
        
    except HTTPException:
        raise  # Relance les erreurs HTTP déjà gérées
        
    except Exception as e:
        logger.error("Erreur lors du rafraîchissement du jeton", 
                    exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur est survenue lors du rafraîchissement du jeton"
        )

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Crée un nouvel utilisateur.
    
    Args:
        user_in: Données de l'utilisateur à créer
        db: Session de la base de données
        
    Returns:
        User: L'utilisateur créé avec ses informations
        
    Raises:
        HTTPException: En cas d'erreur de validation ou de contrainte
    """
    try:
        logger.info("Tentative d'enregistrement d'un nouvel utilisateur",
                  extra={"email": user_in.email, "username": user_in.username})
        
        # Par défaut, le premier utilisateur est un superutilisateur
        is_first_user = db.query(User).count() == 0
        
        # Création d'un dictionnaire des données pour la modification
        user_data = user_in.model_dump()
        user_data["is_superuser"] = is_first_user
        
        # Création d'une nouvelle instance UserCreate avec les données mises à jour
        user_to_create = UserCreate(**user_data)
        
        # Création de l'utilisateur via le service
        user = AuthService.create_user(db=db, user=user_to_create)
        
        logger.info("Utilisateur enregistré avec succès",
                   extra={"user_id": user.id, "email": user.email})
        
        return user
        
    except HTTPException as e:
        logger.warning("Échec de l'enregistrement - erreur HTTP",
                     extra={"status_code": e.status_code, "detail": e.detail})
        raise
        
    except Exception as e:
        logger.error("Erreur inattendue lors de l'enregistrement",
                   exc_info=True,
                   extra={"email": getattr(user_in, 'email', 'N/A')})
        
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(AuthService.get_current_user)]
) -> User:
    """
    Renvoie les informations de l'utilisateur actuellement connecté.
    
    Args:
        current_user: Utilisateur actuellement authentifié (injecté par la dépendance)
        
    Returns:
        User: Les informations de l'utilisateur connecté
    """
    try:
        logger.debug("Accès aux informations de l'utilisateur connecté",
                   extra={"user_id": current_user.id})
        return current_user
        
    except Exception as e:
        logger.error("Erreur lors de la récupération des informations utilisateur",
                   exc_info=True,
                   extra={"user_id": getattr(current_user, 'id', 'N/A')})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des informations utilisateur"
        )
