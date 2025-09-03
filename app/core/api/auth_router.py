"""
Routes d'authentification pour l'API utilisant VoidAuth (OIDC).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.services.voidauth_service import voidauth_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# Modèles de données
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None

class UserInDB(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authentifie un utilisateur et renvoie des tokens JWT."""
    tokens = await voidauth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
        "refresh_token": tokens["refresh_token"]
    }

@router.post("/login/access-token", response_model=LoginResponse)
async def login_access_token(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Authentifie un utilisateur et renvoie un token d'accès.

    Cette endpoint utilise les données form-data pour l'authentification
    et retourne uniquement le token d'accès et son type.
    """
    tokens = await voidauth_service.authenticate_user(
        username=username,
        password=password
    )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserInDB)
async def register(user_data: UserCreate):
    """Crée un nouvel utilisateur dans VoidAuth."""
    try:
        user = await voidauth_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            firstName=user_data.full_name or user_data.username,
            enabled=True,
            emailVerified=False,
            requiredActions=["VERIFY_EMAIL"]
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserInDB)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté."""
    return current_user

@router.get("/login/test-token")
async def test_token(current_user: dict = Depends(get_current_user)):
    """
    Teste la validité d'un token et retourne les informations utilisateur.

    Cette endpoint permet de vérifier qu'un token d'accès est valide
    et de récupérer les informations de l'utilisateur associé.
    """
    return current_user
