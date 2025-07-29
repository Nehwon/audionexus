"""
Service d'envoi d'emails pour l'application AudioNexus.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Envoie un email à un destinataire.
    
    Args:
        to_email: Adresse email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML de l'email
        text_content: Version texte de l'email (optionnel)
        
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    if not current_app.config.get('MAIL_ENABLED', False):
        logger.info("L'envoi d'emails est désactivé. Email non envoyé à %s", to_email)
        return False
    
    # Création du message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to_email
    
    # Ajout du contenu texte et HTML
    if text_content:
        part1 = MIMEText(text_content, 'plain')
        msg.attach(part1)
    
    part2 = MIMEText(html_content, 'html')
    msg.attach(part2)
    
    try:
        # Configuration du serveur SMTP
        with smtplib.SMTP(
            host=current_app.config['MAIL_SERVER'],
            port=current_app.config['MAIL_PORT'],
            timeout=10
        ) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            
            if current_app.config['MAIL_USERNAME'] and current_app.config['MAIL_PASSWORD']:
                server.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
            
            # Envoi de l'email
            server.send_message(msg)
            logger.info("Email envoyé avec succès à %s", to_email)
            return True
            
    except Exception as e:
        logger.error("Erreur lors de l'envoi de l'email à %s: %s", to_email, str(e), exc_info=True)
        return False

def send_password_reset_email(email: str, token: str) -> bool:
    """
    Envoie un email de réinitialisation de mot de passe.
    
    Args:
        email: Adresse email du destinataire
        token: Jeton de réinitialisation
        
    Returns:
        bool: True si l'email a été envoyé avec succès
    """
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
    
    subject = "Réinitialisation de votre mot de passe AudioNexus"
    
    html_content = f"""
    <html>
      <body>
        <h2>Réinitialisation de votre mot de passe</h2>
        <p>Bonjour,</p>
        <p>Vous avez demandé la réinitialisation de votre mot de passe AudioNexus.</p>
        <p>Veuillez cliquer sur le lien ci-dessous pour définir un nouveau mot de passe :</p>
        <p><a href="{reset_url}">Réinitialiser mon mot de passe</a></p>
        <p>Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
        <p>Cordialement,<br>L'équipe AudioNexus</p>
      </body>
    </html>
    """
    
    text_content = f"""
    Réinitialisation de votre mot de passe AudioNexus
    
    Bonjour,
    
    Vous avez demandé la réinitialisation de votre mot de passe AudioNexus.
    
    Veuillez copier-coller le lien suivant dans votre navigateur pour définir un nouveau mot de passe :
    {reset_url}
    
    Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.
    
    Cordialement,
    L'équipe AudioNexus
    """
    
    return send_email(email, subject, html_content, text_content)

def send_welcome_email(email: str, username: str) -> bool:
    """
    Envoie un email de bienvenue à un nouvel utilisateur.
    
    Args:
        email: Adresse email du nouvel utilisateur
        username: Nom d'utilisateur
        
    Returns:
        bool: True si l'email a été envoyé avec succès
    """
    subject = "Bienvenue sur AudioNexus !"
    
    html_content = f"""
    <html>
      <body>
        <h2>Bienvenue sur AudioNexus, {username} !</h2>
        <p>Merci de vous être inscrit sur AudioNexus.</p>
        <p>Vous pouvez dès maintenant vous connecter à votre compte et commencer à profiter de nos services.</p>
        <p>Cordialement,<br>L'équipe AudioNexus</p>
      </body>
    </html>
    """
    
    text_content = f"""
    Bienvenue sur AudioNexus, {username} !
    
    Merci de vous être inscrit sur AudioNexus.
    
    Vous pouvez dès maintenant vous connecter à votre compte et commencer à profiter de nos services.
    
    Cordialement,
    L'équipe AudioNexus
    """
    
    return send_email(email, subject, html_content, text_content)
