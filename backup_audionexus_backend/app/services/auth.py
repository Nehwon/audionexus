import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import secrets

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate, Token, TokenData

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constantes pour JWT
ALGORITHM = "HS256"

class AuthService:
    """Service de gestion de l'authentification."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Génère un hash du mot de passe."""
        return pwd_context.hash(password)
    
    @staticmethod
    def get_user(db: Session, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur avec son email et mot de passe."""
        user = AuthService.get_user(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crée un jeton d'accès JWT.
        
        Args:
            data: Les données à encoder dans le jeton
            expires_delta: Durée de validité du jeton
            
        Returns:
            str: Le jeton JWT encodé
        """
        to_encode = data.copy()
        now = datetime.now(timezone.utc)
        
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=15)
            
        to_encode.update({
            "exp": expire,
            "iat": now,
            "iss": settings.PROJECT_NAME.lower(),
            "aud": "audionexus-api"
        })
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.SECRET_KEY,
                algorithm=ALGORITHM
            )
            return encoded_jwt
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création du jeton: {str(e)}"
            )
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: int) -> str:
        """
        Crée et stocke un jeton de rafraîchissement.
        
        Args:
            db: Session de la base de données
            user_id: ID de l'utilisateur
            
        Returns:
            str: Le jeton de rafraîchissement généré
            
        Raises:
            HTTPException: En cas d'erreur lors de la création du jeton
        """
        try:
            # Supprime les anciens jetons de rafraîchissement
            db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
            
            # Crée un nouveau jeton
            expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            token = RefreshToken(
                token=secrets.token_urlsafe(32),
                expires_at=expires_at,
                user_id=user_id
            )
            
            db.add(token)
            db.commit()
            db.refresh(token)
            return token.token
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création du jeton de rafraîchissement: {str(e)}"
            )
    
    @staticmethod
    def verify_refresh_token(db: Session, token: str) -> Optional[User]:
        """
        Vérifie un jeton de rafraîchissement et retourne l'utilisateur associé.
        
        Args:
            db: Session de la base de données
            token: Le jeton de rafraîchissement à vérifier
            
        Returns:
            Optional[User]: L'utilisateur associé au jeton ou None si invalide
        """
        try:
            refresh_token = (
                db.query(RefreshToken)
                .filter(RefreshToken.token == token)
                .first()
            )
            
            if not refresh_token:
                return None
                
            if refresh_token.is_expired:
                return None
                
            return refresh_token.user
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la vérification du jeton de rafraîchissement: {str(e)}"
            )
    
    @staticmethod
    def create_tokens(db: Session, user: User) -> Token:
        """
        Crée un jeton d'accès et un jeton de rafraîchissement.
        
        Args:
            db: Session de la base de données
            user: L'utilisateur pour lequel générer les jetons
            
        Returns:
            Token: Objet contenant les jetons d'accès et de rafraîchissement
            
        Raises:
            HTTPException: En cas d'erreur lors de la création des jetons
        """
        try:
            # Création du jeton d'accès
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = AuthService.create_access_token(
                data={"sub": user.email, "user_id": user.id, "username": user.username},
                expires_delta=access_token_expires
            )
            
            # Création du jeton de rafraîchissement
            refresh_token = AuthService.create_refresh_token(db, user.id)
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                refresh_token=refresh_token
            )
            
        except HTTPException:
            raise  # Relance les erreurs HTTP déjà gérées
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la création des jetons: {str(e)}"
            )
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """
        Récupère l'utilisateur actuel à partir du jeton JWT.
        
        Args:
            db: Session de la base de données
            token: Le jeton JWT d'authentification
            
        Returns:
            User: L'utilisateur authentifié
            
        Raises:
            HTTPException: Si le jeton est invalide ou l'utilisateur n'existe pas
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Décodage du jeton
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM],
                audience="audionexus-api",
                issuer=settings.PROJECT_NAME.lower()
            )
            
            # Vérification des champs obligatoires
            email: Optional[str] = payload.get("sub")
            if not email:
                raise credentials_exception
                
            # Création de l'objet TokenData avec validation
            try:
                token_data = TokenData(email=email)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Données de jeton invalides: {str(e)}"
                )
            
            # Récupération de l'utilisateur
            user = AuthService.get_user(db, email=token_data.email)
            if user is None or not user.is_active:
                raise credentials_exception
                
            return user
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erreur de validation du jeton: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @classmethod
    def create_user(cls, db: Session, user: UserCreate) -> User:
        """
        Crée un nouvel utilisateur dans la base de données.
        
        Args:
            db: Session de la base de données
            user: Objet UserCreate contenant les données du nouvel utilisateur
            
        Returns:
            User: L'utilisateur créé
            
        Raises:
            HTTPException: En cas d'erreur de validation ou de contrainte
        """
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Début de la création d'un nouvel utilisateur", 
                      extra={"email": user.email, "username": user.username})
            
            # Vérification de l'unicité de l'email et du nom d'utilisateur
            logger.debug("Vérification de l'unicité de l'email et du nom d'utilisateur")
            db_user = db.query(User).filter(
                (User.email == user.email) | (User.username == user.username)
            ).first()
            
            if db_user:
                if db_user.email == user.email:
                    error_msg = f"Cet email est déjà utilisé: {user.email}"
                    logger.warning("Email déjà utilisé", extra={"email": user.email})
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg
                    )
                
                if db_user.username == user.username:
                    error_msg = f"Ce nom d'utilisateur est déjà utilisé: {user.username}"
                    logger.warning("Nom d'utilisateur déjà utilisé", extra={"username": user.username})
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg
                    )
            
            # Hachage du mot de passe
            logger.debug("Hachage du mot de passe")
            hashed_password = cls.get_password_hash(user.password)
            
            # Création de l'utilisateur
            logger.debug("Création de l'objet utilisateur")
            db_user = User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                full_name=user.full_name,
                is_active=getattr(user, 'is_active', True),
                is_superuser=getattr(user, 'is_superuser', False)
            )
            
            # Ajout à la session et validation des contraintes
            logger.debug("Ajout de l'utilisateur à la session")
            db.add(db_user)
            
            # Validation des contraintes avant le commit
            logger.debug("Validation des contraintes")
            db.flush()
            
            # Commit des changements
            logger.debug("Commit des changements")
            db.commit()
            
            # Rafraîchissement de l'objet pour s'assurer qu'il est à jour
            db.refresh(db_user)
            
            logger.info("Utilisateur créé avec succès", 
                       extra={"user_id": db_user.id, "email": db_user.email})
            
            return db_user
            
        except HTTPException:
            # Relance les erreurs HTTP déjà gérées
            db.rollback()
            raise
            
        except Exception as e:
            # Gestion des erreurs inattendues
            db.rollback()
            logger.error(
                "Erreur lors de la création de l'utilisateur", 
                exc_info=True,
                extra={
                    "error": str(e),
                    "email": getattr(user, 'email', 'N/A'),
                    "username": getattr(user, 'username', 'N/A')
                }
            )
            
            # Message d'erreur générique pour l'utilisateur
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Une erreur est survenue lors de la création de l'utilisateur"
            )
