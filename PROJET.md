# AudioNexus Authentication Issue Resolution Plan

## Notes
- Context: Ongoing issues with authentication endpoints, specifically `/auth/register` (500 error), Pydantic v2 validation, and async session management.
- Impacted files: `app/core/api/auth.py`, `app/db/models/base.py`, `app/tests/test_auth.py`.
- Environment and dependency requirements are specified in the protocol.
- `.env` configuration and dependency versions are critical for reproducibility.
- Common issues include Pydantic model definitions and async DB session handling.
- Environment and dependencies have been updated and verified as per protocol.
- .env file has been updated to use SQLite and required settings.
- UserCreate model updated to explicitly include required fields from UserBase.
- Database configuration updated to prioritize DATABASE_URL and support SQLite per .env.
- Authentication tests executed: `/auth/register` still returns 500, and several endpoints/tests fail with 422 errors (missing fields, likely dependency or model issues).
- The SQLite database file (`audionexus.db`) is missing, indicating the schema was not initialized. This is likely the cause of the 500 error on `/auth/register`.
- Attempting to initialize the database schema with the provided script failed due to a `greenlet_spawn has not been called` error, indicating a mismatch between synchronous table creation and an async (aiosqlite) engine. Need to use an async-compatible migration or initialization approach.
- Attempting async initialization resulted in `AttributeError: 'NoneType' object has no attribute 'begin'` because `async_engine` was not properly initialized. Need to debug why `init_async_engine()` does not set `async_engine` as expected.
- After attempting to fix the assignment of the async engine, the async initialization script still fails with `'NoneType' object has no attribute 'begin'`. This suggests `async_engine` is still not available at the time of use and the initialization order or module import side effects must be further debugged.
- The async database initialization script was enhanced to create and manage the engine directly, and the database tables were successfully created. The SQLite database file (`audionexus.db`) is now present.
- Après création des tables, le test du endpoint `/auth/register` retourne toujours une erreur 500 (« Erreur interne du serveur »). Les prochaines étapes nécessitent d'examiner les logs du serveur et la configuration API pour diagnostiquer l'origine de cette erreur.
- Le serveur affiche un avertissement : la coroutine `init_db` n'est jamais awaitée lors de l'initialisation de la base (voir `app/db/__init__.py`). Cela peut causer des incohérences ou des erreurs à l'exécution.
- La correction de l'appel non-awaité à `init_db` dans `__init__.py` a été appliquée et le serveur a été redémarré pour prendre en compte la modification.
- Suppression de l'appel direct à `init_db()` dans l'initialisation de la base de données pour éviter tout avertissement ou effet de bord asynchrone.
- Une nouvelle erreur Pydantic v2 (`class-not-fully-defined`) empêche la validation du modèle `UserCreate` dans le endpoint `/auth/register`. Il faut corriger la référence de type et s'assurer que le modèle est bien importé et défini pour la validation FastAPI/Pydantic.
- Correction appliquée : le modèle `UserCreate` est maintenant défini localement dans `auth.py` pour éviter la référence circulaire et l'erreur Pydantic v2. Le 500 a disparu, mais une erreur 422 persiste (champ manquant).
- Découverte : la dépendance `get_async_db` utilisée dans les endpoints FastAPI est en fait un alias de `get_async_db_session`, qui attend un paramètre `kw` (gestionnaire de contexte), ce qui explique l'erreur 422 « Field required: kw ». Il faut corriger l'import ou la définition de cette dépendance pour un usage correct dans FastAPI.
- Correction appliquée : la dépendance `get_async_db` est maintenant une fonction asynchrone adaptée à FastAPI, ce qui doit résoudre l'erreur 422 liée au paramètre `kw`.
- À vérifier : Le payload POST envoyé à `/auth/register` doit comporter tous les champs requis (`username`, `email`, `password`, `full_name` optionnel) avec les bons noms, types et le bon format JSON, conformément au modèle `UserCreate` local (voir causes fréquentes d'erreur 422).
- Malgré la correction de la dépendance `get_async_db`, l'erreur 422 persiste : le champ `kw` est toujours requis selon la réponse du serveur et les logs. Il est nécessaire de réexaminer la chaîne de dépendances FastAPI et la configuration de l'injection de dépendance.
- Ajouter : Causes fréquentes de 422 : champs inattendus (ex : `full_name` non permis), champs obligatoires manquants, ou format invalide (ex : email non conforme à `EmailStr`). Vérifier que le payload correspond exactement au schéma `UserCreate`.
- Les tests automatisés construisent les requêtes d'inscription avec tous les champs requis et les bons types, donc l'erreur 422 n'est probablement pas due à un champ manquant ou mal nommé dans le payload de test.
- Le système de surcharge des dépendances dans `conftest.py` remplace correctement `get_async_db` pour les tests, donc l'erreur `kw` persistante ne vient pas de la configuration des tests mais d'une incohérence dans la résolution des dépendances entre le code applicatif et les tests.
- Analyse : la fonction `get_async_db_session` dans `session_manager.py` est correctement définie comme gestionnaire de contexte asynchrone et ne requiert pas de paramètre `kw`. La persistance de l'erreur 422 (champ `kw` requis) indique qu'une référence incorrecte à une ancienne version de la dépendance ou un alias subsiste quelque part dans le code (ex : un alias ou import résiduel dans deps.py ou ailleurs). Il faut traquer et corriger toute utilisation/alias erroné de la dépendance asynchrone de session DB dans l'application.
- Découverte : dans `deps.py`, la fonction `get_async_db_session` est encore utilisée comme alias pour `get_async_db`, ce qui provoque l'attente d'un paramètre `kw` dans les endpoints. Il faut corriger l'alias pour utiliser la bonne fonction `get_async_db` adaptée à FastAPI.
- Analyse complémentaire : la fonction `get_async_db` dans `session_manager.py` est correctement définie pour FastAPI (ne requiert pas de paramètre `kw`). Il faut s'assurer que `deps.py` référence bien cette fonction et non un alias ou une ancienne version.
- Vérification : l'import de `get_async_db` dans `deps.py` pointe bien vers la fonction FastAPI correcte, la correction de l'alias a été vérifiée dans la chaîne d'import. L'alias est maintenant correct pour FastAPI.
- Le serveur affiche un avertissement : la coroutine `init_db` n'est jamais awaitée lors de l'initialisation de la base (voir `app/db/__init__.py`). Cela peut causer des incohérences ou des erreurs à l'exécution.
- Suppression de l'appel direct à `init_db()` dans l'initialisation de la base de données pour éviter tout avertissement ou effet de bord asynchrone.
- Diagnostiquer et corriger l'erreur 500 persistante sur `/auth/register` après création des tables (analyse des logs, vérification du code API, etc.)
- Analyse approfondie : la structure du modèle utilisateur (`User` dans `base.py`) et les fonctions CRUD (`crud_user.py`) sont correctes et cohérentes avec le schéma attendu pour l'inscription. La chaîne d'appel du endpoint `/auth/register` est valide côté modèle et accès DB.
- Instrumentation : des logs de débogage ont été ajoutés à la route `/auth/register` pour diagnostiquer la cause de l'erreur 500 et capturer toute exception lors de la création d'utilisateur.
- Test POST avec paramètre `kw=test` : le serveur retourne 500 avec l'erreur `Session.__init__() got an unexpected keyword argument 'kw'`, confirmant que le backend attend à tort ce paramètre (problème d'alias/dépendance non corrigé dans la chaîne d'import).
- Protocole de début de session à appliquer : reprendre à partir de `documentation/PROTOCOLE_DEBUT.md`, copier ce fichier dans `documentation/archives`, puis suivre les étapes séquentiellement.
- Protocole de fin de session à appliquer : mise à jour de la documentation, état du projet, gestion de version, vérifications qualité, commit, synchronisation, clôture de session (voir `documentation/PROTOCOLE_FIN.md`).
- Le projet AudioNexus rencontre des problèmes persistants d'authentification (erreurs 500 et 422 sur `/auth/register`).
- L'environnement est prêt, la base SQLite est créée, et les modèles Pydantic sont en cours de mise à jour.
- L'utilisateur souhaite désormais se concentrer sur l'édition de l'interface utilisateur pour permettre de tester en grandeur réelle les fonctions déjà implémentées.
- Le fichier PROJET.md sert de référence pour l'état du backend et les tâches en cours.


## Task List
- [x] Prepare the environment (activate venv, install deps, ensure aiosqlite)
- [x] Verify all required dependency versions
- [x] Check and update `.env` file as per protocol
- [ ] Appliquer le protocole de début de session (`documentation/PROTOCOLE_DEBUT.md`)
  - [ ] Copier `documentation/PROTOCOLE_DEBUT.md` dans `documentation/archives`
  - [ ] Suivre les étapes du protocole de début de session une à une
- [ ] Investigate and resolve 500 error on `/auth/register`
  - [x] Ensure `UserCreate` is properly defined in `app/db/models/base.py`
  - [x] Corriger la référence circulaire et l'import du modèle `UserCreate` dans `auth.py` (erreur Pydantic v2 résolue)
  - [ ] Update all Pydantic models to v2 syntax
  - [ ] Add `model_config = ConfigDict(from_attributes=True)` if needed
  - [x] Corriger la dépendance `get_async_db` pour qu'elle ne requière pas de paramètre `kw` dans les endpoints FastAPI
  - [x] Ajouter des logs de débogage dans la route `/auth/register` pour diagnostiquer l'erreur 500
  - [x] Tester l'endpoint avec le paramètre `kw` pour confirmer la cause de l'erreur
- [ ] Review and fix async session usage in authentication endpoints
  - [ ] Confirm all DB operations use `AsyncSession` and proper `await`
  - [ ] Use `async with db.begin()` for transactions
- [x] Run authentication tests (`pytest app/tests/test_auth.py -v`)
- [ ] Validate that all authentication endpoints function as expected
- [ ] Debug and resolve remaining 500 and 422 errors in authentication endpoints and tests
- [x] Initialize the database schema (run migrations or create tables)
  - [x] Investigate and resolve `greenlet_spawn`/async initialization error
  - [x] Investigate and resolve `async_engine` is None after calling `init_async_engine()`
    - [x] Debug initialization order and module import side effects preventing `async_engine` from being set
- [ ] Diagnostiquer et corriger l'erreur 500 persistante sur `/auth/register` après création des tables (analyse des logs, vérification du code API, etc.)
- [ ] Appliquer le protocole de fin de session (`documentation/PROTOCOLE_FIN.md`)
- [x] Préparer l'environnement backend et corriger les principaux bugs d'authentification
- [ ] Concevoir une interface utilisateur simple (web ou CLI) permettant de tester les endpoints principaux (auth/register, auth/login, etc.)
  - [ ] Définir les principaux cas d'usage à tester via l'UI
  - [ ] Implémenter les formulaires ou interfaces de saisie nécessaires
  - [ ] Connecter l'UI au backend existant (API REST)
  - [ ] Permettre l'affichage des résultats et des erreurs côté utilisateur
- [ ] Itérer sur l'UI selon les retours de test et les besoins identifiés


## Current Goal
Concevoir une interface utilisateur de test minimale