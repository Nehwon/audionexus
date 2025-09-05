"""
Routes d'authentification pour l'API utilisant VoidAuth (OIDC).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.services.voidauth_service import voidauth_service
from app.services.audit_service import audit_service
from app.core.dependencies import get_current_user
from app.db.models.base import UserInDB, UserCreate, Token
from app.core.security import generate_csrf_token, verify_csrf_token
from app.core.rate_limit import limiter
from app.db.session import get_db
from pydantic import BaseModel
from fastapi import Header, Depends
from sqlalchemy.orm import Session
from time import time

router = APIRouter(prefix="/auth", tags=["auth"])

# Stockage temporaire des tokens CSRF (en production, utiliser Redis)
csrf_tokens = set()

# Modèles de données supplémentaires
class TokenWithRefresh(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class CSRFToken(BaseModel):
    csrf_token: str

def get_csrf_token() -> str:
    """
    Dépendance pour vérifier et valider un token CSRF depuis le header X-CSRF-Token.

    Returns:
        str: Le token CSRF s'il est valide

    Raises:
        HTTPException: Si le token CSRF est manquant ou invalide
    """
    def _verify_csrf_token(csrf_token: str = Header(None, alias="X-CSRF-Token")):
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token CSRF manquant dans le header X-CSRF-Token"
            )

        if csrf_token not in csrf_tokens:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token CSRF invalide"
            )

        # Supprimer le token après utilisation (usage unique)
        csrf_tokens.discard(csrf_token)
        return csrf_token

    return _verify_csrf_token

@router.get("/csrf-token", response_model=CSRFToken)
@limiter.limit("20/minute")
async def get_csrf_token_endpoint(request: Request):
    """
    Génère et retourne un nouveau token CSRF pour les opérations POST sensibles.

    Le token doit être inclus dans le header X-CSRF-Token des requêtes POST
    vers /login, /login/access-token et /register.
    """
    token = generate_csrf_token()
    csrf_tokens.add(token)

    return {"csrf_token": token}

@router.post("/login", response_model=TokenWithRefresh)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    csrf_token: str = Depends(get_csrf_token()),
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur et renvoie des tokens JWT."""
    start_time = time() * 1000  # Timestamp en millisecondes
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    try:
        tokens = await voidauth_service.authenticate_user(
            username=form_data.username,
            password=form_data.password
        )

        if not tokens:
            # Log de l'échec d'authentification
            await audit_service.log_security_event(
                db=db,
                action="login_failed",
                resource="auth",
                method="POST",
                ip_address=ip_address,
                username=form_data.username,
                status_code=401,
                user_agent=user_agent,
                request_data={"username": form_data.username},
                severity="warning",
                compliance_flags={"gdpr": True, "sox": True}
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Calcul de la durée
        duration = int((time() * 1000) - start_time)

        # Log du succès d'authentification
        await audit_service.log_security_event(
            db=db,
            action="login_success",
            resource="auth",
            method="POST",
            ip_address=ip_address,
            username=form_data.username,
            status_code=200,
            user_agent=user_agent,
            duration_ms=duration,
            severity="info",
            compliance_flags={"gdpr": True, "sox": True}
        )

        return {
            "access_token": tokens["access_token"],
            "token_type": "bearer",
            "refresh_token": tokens["refresh_token"]
        }

    except HTTPException:
        raise
    except Exception as e:
        # Log des erreurs système
        await audit_service.log_security_event(
            db=db,
            action="login_error",
            resource="auth",
            method="POST",
            ip_address=ip_address,
            username=form_data.username,
            status_code=500,
            user_agent=user_agent,
            severity="error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'authentification"
        )

@router.post("/login/access-token", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Depends(get_csrf_token())
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
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    csrf_token: str = Depends(get_csrf_token())
):
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
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté."""
    return UserInDB.from_orm(current_user)

@router.get("/login/test-token")
async def test_token(current_user = Depends(get_current_user)):
    """
    Teste la validité d'un token et retourne les informations utilisateur.

    Cette endpoint permet de vérifier qu'un token d'accès est valide
    et de récupérer les informations de l'utilisateur associé.
    """
    return UserInDB.from_orm(current_user)
