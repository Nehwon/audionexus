# 🗺️ ROADMAP AudioNexus - Résolution Authentification & Dashboard

## 📋 Vue d'ensemble

Ce roadmap détaille la **résolution complète des problèmes de blocs de connexion et d'accès au dashboard** identifiés lors de la session Téléphone Rouge. Le projet a révélé que le **frontend n'était pas complètement intégré**, malgré des composants existants.

## 🎯 État Actuel (06/09/2025)

### ✅ COMPLÉTÉ (Session Téléphone Rouge)
- [x] **Débogage erreurs 422 FastAPI** - Dépendances unifiées
- [x] **Unification système get_db()** - Conflits résolus
- [x] **Stabilisation authentification** - VoidAuth backend OK
- [x] **Conflit MySQL/SQLite** - Strategy Pattern implémenté
- [x] **Règle de commit** - Processus documenté

### 🔍 DÉCOUVERTE : Frontend Partiellement Présent
Après la fusion git, découverte que :
- ✅ **Architecture frontend** créée (React/TypeScript/Vite)
- ✅ **Composants de base** présents (Login.tsx, Dashboard.tsx)
- ✅ **Services API** implémentés (authApi.ts, instancesApi.ts)
- ✅ **Contextes** configurés (AuthContext.tsx, ThemeContext.tsx)
- ✅ **Pages** existantes (Dashboard, Instances, Login, Sync)
- ⚠️ **Intégration VoidAuth** à vérifier/compléter
- ⚠️ **Configuration VoidAuth** frontend/backend à aligner
- ⚠️ **Connexion backend/frontend** à tester

---

## 🚀 PHASES DE RÉSOLUTION

### **PHASE 1 : DIAGNOSTIC & VALIDATION (Critique)** 🔴

#### A. **Validation État Frontend** 🔍
- [ ] Examiner le contenu des pages Login.tsx et Dashboard.tsx
- [ ] Vérifier la configuration AuthContext.tsx (VoidAuth)
- [ ] Tester les services API (authApi.ts, instancesApi.ts)
- [ ] Auditer la configuration VoidAuth frontend (`VITE_OIDC_*`)

#### B. **Configuration VoidAuth** ⚙️
- [ ] **Backend** : Vérifier configuration remplie dans `.env`
```env
VOIDAUTH_SERVER_URL=http://localhost:8080
VOIDAUTH_REALM=audionexus
VOIDAUTH_CLIENT_ID=audionexus-backend
```
- [ ] **Frontend** : Vérifier configuration dans `.env`/variables Vite
```env
VITE_API_URL=http://localhost:8000/api
VITE_OIDC_CLIENT_ID=audionexus-frontend
VITE_OIDC_AUTHORITY=http://localhost:8080/realms/audionexus
```

#### C. **Test Préliminaire** 🧪
- [ ] Lancer backend VoidAuth (probablement Keycloak)
- [ ] Tester endpoints backend `/auth/login` et `/auth/me`
- [ ] Vérifier configuration CORS (`BACKEND_CORS_ORIGINS`)

### **PHASE 2 : RÉSOLUTION LOGIN IMPOSSIBLE** 🔑

#### A. **Configuration VoidAuth Frontend** 📋
- [ ] Mettre à jour la page Login.tsx avec VoidAuth OIDC
- [ ] Implémenter flow d'authentification OIDC Connect
- [ ] Configurer redirect URI (`/auth/callback`)
- [ ] Gérer les tokens JWT (access + refresh)

#### B. **Intégration AuthContext** 🔗
- [ ] Compléter AuthContext.tsx avec VoidAuth
- [ ] Implémenter `login()`, `logout()`, `refreshToken()`
- [ ] Gérer l'état d'authentification global
- [ ] Persister la session utilisateur

#### C. **Gestion Erreurs Login** ⚠️
- [ ] Affichage erreurs utilisateur-friendly
- [ ] Gestion réseau et timeouts
- [ ] Messages pour mots de passe invalides
- [ ] Loading states pendant authentification

### **PHASE 3 : RÉSOLUTION DASHBOARD INACCESSIBLE** 📊

#### A. **Protection Routes** 🛡️
- [ ] Configurer React Router avec guards
- [ ] Implémenter `ProtectedRoute` component
- [ ] Redirections automatiques non-authentifié
- [ ] Gestion des rôles et permissions

#### B. **Intégration API Backend** 🔌
- [ ] Connecter Dashboard aux APIs instances
- [ ] Implémenter appels `/audiobookshelf/instances`
- [ ] Synchronisation données temps réel
- [ ] Gestion erreurs réseau et retries

#### C. **État Appli Frontend** 📊
- [ ] Implémenter React Query pour caching
- [ ] Gestion offline/online
- [ ] Loading states et skeletons
- [ ] Notifications utilisateur

### **PHASE 4 : TESTS D'INTÉGRATION** 🧪

#### A. **Tests Authentification** ✅
- [ ] Tests des flows VoidAuth (login/logout)
- [ ] Tests des protections de routes
- [ ] Tests des tokens et expiration
- [ ] Tests de resilience réseau

#### B. **Tests E2E** 🎭
- [ ] Tests avec Cypress/Playwright
- [ ] Scénarios complets (login → dashboard)
- [ ] Tests de déconnexion/expiration
- [ ] Tests multi-utilisateurs

### **PHASE 5 : OPTIMISATIONS & QUALITÉ** 🚀

#### A. **Performance** ⚡
- [ ] Optimisation chargement frontend
- [ ] Lazy loading des composants
- [ ] Caching intelligent des données
- [ ] Reduction bundle size

#### B. **Sécurité Additionnelle** 🔒
- [ ] Implementer HTTPS obligatoire
- [ ] Configure Content Security Policy
- [ ] Audit des dépendances vulnérables
- [ ] Rate limiting côté frontend

#### C. **Accessibilité** ♿
- [ ] Conformité WCAG 2.1
- [ ] Navigation clavier complète
- [ ] Support lecteurs d'écran
- [ ] Contrastes et tailles de police

---

## 🏛️ ARCHITECTURE CIBLE FINALE

### **Frontend Architecture**
```
frontend/
├── src/
│   ├── components/         # Composants UI réutilisables
│   ├── pages/             # Pages principales (Login.tsx, Dashboard.tsx, etc.)
│   ├── contexts/          # Gestion état global (AuthContext)
│   ├── services/          # Appels API (authApi.ts, instancesApi.ts)
│   ├── hooks/            # Hooks personnalisés
│   └── types/            # Typages TypeScript
```

### **Flux Authentification**
1. **Login** → VoidAuth OIDC Flow
2. **Callback** → Traitement tokens
3. **Dashboard** → Vérification autorisation
4. **API Calls** → Tokens dans headers Authorization
5. **Logout** → Invalidation tokens + nettoyage local

### **Technologies Retenues**
- **Framework** : React 18 + TypeScript
- **Build** : Vite (développement + production)
- **Auth** : VoidAuth OIDC Client
- **State** : React Contexts + React Query
- **UI** : Tailwind CSS + DaisyUI
- **Tests** : Vitest + Playwright
- **Linting** : ESLint + Prettier

---

## 📊 MÉTRIQUES DE SUCCÈS

### **Critères de Validation Phase 1**
- [ ] Backend VoidAuth répond `/auth/login`, `/auth/me`
- [ ] Variables d'environnement VoidAuth configurées
- [ ] Serveur VoidAuth accessible (port 8080)

### **Critères de Validation Phase 2**
- [ ] Page Login fonctionnelle avec VoidAuth
- [ ] AuthContext gère l'état utilisateur
- [ ] Tokens persistés et rafraîchis automatiquement

### **Critères de Validation Phase 3**
- [ ] Dashboard accessible après login
- [ ] Routes protégées fonctionnelles
- [ ] APIs instances connectées
- [ ] Gestion des erreurs utilisateur-friendly

### **Critères de Validation Phase 4**
- [ ] Tous tests d'authentification passent
- [ ] Scénarios E2E complets réussis
- [ ] Performance acceptable (< 3s login)

---

## 🚨 BLOCAGES PRÉVISIBLES

### **Blocage 1 : Configuration VoidAuth** ⚠️
- **Risque** : Serveur VoidAuth non configuré
- **Solution** : Guide de configuration dans documentation
- **Impact** : Bloque complètement l'authentification

### **Blocage 2 : CORS Misconfiguration** ⚠️
- **Risque** : Frontend ne peut pas contacter backend
- **Solution** : Vérification rigoureuse configuration CORS
- **Impact** : Authentification partiellement fonctionnelle

### **Blocage 3 : Tokens OIDC** ⚠️
- **Risque** : Flow OIDC mal implémenté
- **Solution** : Documentation VoidAuth détaillée
- **Impact** : Login possible mais tokens non gérés

---

## 🎯PROCHAINES ACTIONS RECOMMANDÉES

1. **IMMEDIAT** : Lire et documenter l'état réel des composants frontend
2. **COURT TERME** : Tester la connexion backend actuelle
3. **MOYEN TERME** : Compléter l'intégration VoidAuth si manquante
4. **LONG TERME** : Tests et optimisations de performance

### **Remarque Importante**
Un frontend complet a déjà été créé dans la branche fusionnée. Il est crucial de d'abord **auditer l'état actuel** avant de décider quoi implémenter/corriger.

---

*ROADMAP créé le 06/09/2025 - Mise à jour nécessaire après validation de l'état frontend actuel*