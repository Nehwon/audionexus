-- Initialisation de la base de données AudioNexus

-- Assurez-vous d'utiliser le bon encodage
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Création de la base de données si elle n'existe pas déjà
-- La base de données est déjà créée par les variables d'environnement, mais nous pouvons la sélectionner
USE `${MYSQL_DATABASE}`;

-- Désactiver temporairement les contraintes de clé étrangère
SET FOREIGN_KEY_CHECKS = 0;

-- Suppression des tables si elles existent déjà (pour les réinitialisations)
-- Ces commandes sont commentées pour éviter les suppressions accidentelles
-- DÉCOMMENTER UNIQUEMENT POUR LES NOUVELLES INSTALLATIONS
-- DROP TABLE IF EXISTS `users`;
-- DROP TABLE IF EXISTS `roles`;
-- DROP TABLE IF EXISTS `user_roles`;
-- DROP TABLE IF EXISTS `refresh_tokens`;
-- Ajoutez ici d'autres tables à supprimer si nécessaire

-- Table des rôles
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_superuser` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table de liaison utilisateurs-rôles
CREATE TABLE IF NOT EXISTS `user_roles` (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des tokens de rafraîchissement
CREATE TABLE IF NOT EXISTS `refresh_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` varchar(512) NOT NULL,
  `user_id` int NOT NULL,
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `refresh_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Réactiver les contraintes de clé étrangère
SET FOREIGN_KEY_CHECKS = 1;

-- Insertion des rôles par défaut (si la table est vide)
INSERT IGNORE INTO `roles` (`name`, `description`) VALUES
('admin', 'Administrateur système avec tous les droits'),
('user', 'Utilisateur standard avec des droits limités'),
('moderator', 'Modérateur avec des droits étendus');

-- Insertion d'un administrateur par défaut (mot de passe: admin123)
-- REMARQUE : Dans un environnement de production, utilisez un mot de passe fort et ne le stockez pas en clair
-- Le mot de passe sera haché par l'application avant d'être stocké
-- L'email et le mot de passe doivent être remplacés par des valeurs d'environnement
-- INSERT IGNORE INTO `users` (`email`, `hashed_password`, `full_name`, `is_active`, `is_superuser`)
-- VALUES ('admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Administrateur', 1, 1);

-- Attribution du rôle admin à l'utilisateur admin
-- INSERT IGNORE INTO `user_roles` (`user_id`, `role_id`)
-- SELECT u.id, r.id FROM `users` u, `roles` r WHERE u.email = 'admin@example.com' AND r.name = 'admin';

-- Message de fin
SELECT 'Base de données AudioNexus initialisée avec succès' AS message;
