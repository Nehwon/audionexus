from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate, User as UserSchema, Token, TokenData

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
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un jeton d'accès JWT."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: int) -> str:
        """Crée et stocke un jeton de rafraîchissement."""
        # Supprime les anciens jetons de rafraîchissement
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        # Crée un nouveau jeton
        token = RefreshToken(
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_id=user_id
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token.token
    
    @staticmethod
    def verify_refresh_token(db: Session, token: str) -> Optional[User]:
        """Vérifie un jeton de rafraîchissement et retourne l'utilisateur associé."""
        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if not refresh_token:
            return None
        if refresh_token.is_expired:
            return None
        return refresh_token.user
    
    @staticmethod
    def create_tokens(db: Session, user: User) -> Token:
        """Crée un jeton d'accès et un jeton de rafraîchissement."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        refresh_token = AuthService.create_refresh_token(db, user.id)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token
        )
    
    @staticmethod
    def get_current_user(
        db: Session, 
        token: str
    ) -> Optional[User]:
        """Récupère l'utilisateur actuel à partir du jeton JWT."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception
            
        user = AuthService.get_user(db, email=token_data.email)
        if user is None:
            raise credentials_exception
        return user
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Crée un nouvel utilisateur."""
        # Vérifie si l'email est déjà utilisé
        db_user = db.query(User).filter(
            (User.email == user.email) | (User.username == user.username)
        ).first()
        
        if db_user:
            if db_user.email == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Cet email est déjà utilisé"
                )
            elif db_user.username == user.username:
                raise HTTPException(
                    status_code=400,
                    detail="Ce nom d'utilisateur est déjà utilisé"
                )
        
        # Crée l'utilisateur
        hashed_password = AuthService.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
