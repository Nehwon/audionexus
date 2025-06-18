from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, User, Token
from app.services.auth import AuthService
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et renvoie des jetons d'accès et de rafraîchissement.
    """
    user = AuthService.authenticate_user(
        db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est désactivé"
        )
    
    return AuthService.create_tokens(db, user)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Rafraîchit un jeton d'accès à l'aide d'un jeton de rafraîchissement.
    """
    user = AuthService.verify_refresh_token(db, refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton de rafraîchissement invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return AuthService.create_tokens(db, user)

@router.post("/register", response_model=User)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel utilisateur.
    """
    # Par défaut, le premier utilisateur est un superutilisateur
    is_first_user = db.query(User).count() == 0
    user_in.is_superuser = is_first_user
    
    try:
        return AuthService.create_user(db=db, user=user_in)
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(AuthService.get_current_user)
):
    """
    Renvoie les informations de l'utilisateur actuellement connecté.
    """
    return current_user
