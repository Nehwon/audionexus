"""
Routes d'authentification pour l'API.
"""

from flask import current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields, reqparse

from app import db
from app.core.security import create_access_token as create_jwt_token
from app.db.models import Role, User
from app.exceptions import InvalidCredentialsError, UserAlreadyExistsError

# Création du namespace pour les routes d'authentification
api = Namespace("auth", description="Opérations d'authentification")

# Modèles de données pour la documentation Swagger
user_model = api.model(
    "User",
    {
        "id": fields.Integer(
            readonly=True, description="Identifiant unique de l'utilisateur"
        ),
        "username": fields.String(required=True, description="Nom d'utilisateur"),
        "email": fields.String(required=True, description="Adresse email"),
        "is_active": fields.Boolean(description="Indique si le compte est actif"),
        "is_superuser": fields.Boolean(
            description="Indique si l'utilisateur est administrateur"
        ),
    },
)

token_model = api.model(
    "Token",
    {
        "access_token": fields.String(required=True, description="JWT d'accès"),
        "token_type": fields.String(
            required=True, default="bearer", description="Type de token"
        ),
    },
)

login_parser = reqparse.RequestParser()
login_parser.add_argument("username", type=str, required=True, help="Nom d'utilisateur")
login_parser.add_argument("password", type=str, required=True, help="Mot de passe")

register_parser = reqparse.RequestParser()
register_parser.add_argument(
    "username", type=str, required=True, help="Nom d'utilisateur"
)
register_parser.add_argument("email", type=str, required=True, help="Adresse email")
register_parser.add_argument("password", type=str, required=True, help="Mot de passe")
register_parser.add_argument("full_name", type=str, required=False, help="Nom complet")


# Fonctions utilitaires
def _get_user_roles(user):
    """Récupère les rôles d'un utilisateur."""
    return [role.name for role in user.roles] if user.roles else []


def _create_user(
    username: str, email: str, password: str, full_name: str = None
) -> User:
    """Crée un nouvel utilisateur."""
    if User.query.filter((User.username == username) | (User.email == email)).first():
        raise UserAlreadyExistsError("Nom d'utilisateur ou email déjà utilisé")

    user = User(username=username, email=email, full_name=full_name, is_active=True)
    user.set_password(password)

    user_role = Role.query.filter_by(name="user").first()
    if user_role:
        user.roles.append(user_role)

    db.session.add(user)
    db.session.commit()

    return user


def _authenticate_user(username: str, password: str) -> User:
    """Authentifie un utilisateur."""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        raise InvalidCredentialsError("Identifiants invalides")
    if not user.is_active:
        raise InvalidCredentialsError("Compte désactivé")
    return user


# Routes d'API
@api.route("/login")
class Login(Resource):
    @api.doc("login")
    @api.expect(login_parser)
    @api.response(200, "Connexion réussie", token_model)
    @api.response(400, "Identifiants invalides")
    def post(self):
        """Connexion d'un utilisateur et génération d'un token JWT."""
        args = login_parser.parse_args()
        user = _authenticate_user(args["username"], args["password"])

        access_token = create_jwt_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}


@api.route("/register")
class Register(Resource):
    @api.doc("register")
    @api.expect(register_parser)
    @api.response(201, "Utilisateur créé avec succès")
    @api.response(400, "Données invalides ou utilisateur existant")
    def post(self):
        """Création d'un nouvel utilisateur."""
        args = register_parser.parse_args()

        user = _create_user(
            username=args["username"],
            email=args["email"],
            password=args["password"],
            full_name=args.get("full_name"),
        )

        access_token = create_jwt_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}, 201


@api.route("/me")
class UserInfo(Resource):
    @api.doc("get_user_info", security="Bearer")
    @api.response(200, "Succès", user_model)
    @api.response(401, "Non authentifié")
    @jwt_required()
    def get(self):
        """
        Récupère les informations de l'utilisateur connecté.

        Cette route nécessite une authentification JWT valide.
        Le token doit être fourni dans le header Authorization: Bearer <token>
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return {"message": "Utilisateur non trouvé"}, 404

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "roles": [role.name for role in user.roles] if user.roles else [],
        }


# Routes pour la réinitialisation du mot de passe
reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument(
    "email", type=str, required=True, help="Adresse email de l'utilisateur"
)

new_password_parser = reqparse.RequestParser()
new_password_parser.add_argument(
    "token", type=str, required=True, help="Jeton de réinitialisation"
)
new_password_parser.add_argument(
    "new_password", type=str, required=True, help="Nouveau mot de passe"
)


@api.route("/forgot-password")
class ForgotPassword(Resource):
    @api.doc("forgot_password")
    @api.expect(reset_password_parser)
    @api.response(200, "Si l'email existe, un lien de réinitialisation a été envoyé")
    def post(self):
        """Demande de réinitialisation de mot de passe."""
        args = reset_password_parser.parse_args()
        email = args["email"]

        user = User.query.filter_by(email=email).first()
        if user and user.is_active:
            # Envoi d'email désactivé pour le moment
            current_app.logger.info(
                "Envoi d'email de réinitialisation désactivé (fonctionnalité non prioritaire)"
            )
            # Note: L'envoi d'email sera implémenté ultérieurement

        # Ne pas révéler si l'email existe ou non pour des raisons de sécurité
        return {
            "message": "Si votre email est enregistré, vous recevrez un lien de réinitialisation"
        }


@api.route("/reset-password")
class ResetPassword(Resource):
    @api.doc("reset_password")
    @api.expect(new_password_parser)
    @api.response(200, "Mot de passe mis à jour avec succès")
    @api.response(400, "Jeton invalide ou expiré")
    def post(self):
        """Réinitialisation du mot de passe avec un jeton valide."""
        args = new_password_parser.parse_args()
        token = args["token"]
        new_password = args["new_password"]

        # Vérification du token désactivée pour le moment
        email = None  # À implémenter : vérification du token de réinitialisation
        if not email:
            return {"message": "Jeton invalide ou expiré"}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {"message": "Utilisateur non trouvé"}, 400

        # Mettre à jour le mot de passe
        user.set_password(new_password)
        db.session.commit()

        return {"message": "Mot de passe mis à jour avec succès"}
