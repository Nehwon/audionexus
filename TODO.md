# 📋 TODO AudioNexus - Tâches en Attente

## 🎯 État Actuel : Containers Docker Stabilisés ✅

Au 07/09/2025, AudioNexus v0.8.0 présente une infrastructure containerisée fonctionnelle avec :
- ✅ Construction réussie des images Docker frontend et backend
- ✅ Démarrage automatique : Redis (1.4s), MySQL (7s), Backend (6.6s), Frontend (6.8s)
- ✅ Élimination de la lenteur de copie des fichiers frontend (~26s → ~157s build optimisé)

---

## 🔄 Fonctionnalités Frontend à Implémenter

### [`frontend/src/pages/Search.tsx:7`](frontend/src/pages/Search.tsx:7)
**Navigation vers Page Détail Audiobook**
- Implémenter la logique de navigation vers la page de détail des livres audio
- Créer le composant `AudiobookDetail` avec:
  - Affichage complet des métadonnées
  - Lecteur audio intégré
  - Gestion des marque-pages
  - Téléchargement/lecture en streaming

```typescript
// TODO: Étape A - Créer la logique de navigation
const handleResultSelect = (result: SearchResult) => {
  // Navigation vers /audiobooks/{result.audiobook_id}
  navigate(`/audiobooks/${result.audiobook_id}`);
};
```

### [`frontend/src/components/SimpleSearchComponent.tsx:172`](frontend/src/components/SimpleSearchComponent.tsx:172)
**Pagination Précédente**
- Implémenter le fonctionnement du bouton "Précédent" dans la pagination
- Gestion des états de page et rechargements des données

### [`frontend/src/components/SimpleSearchComponent.tsx:184`](frontend/src/components/SimpleSearchComponent.tsx:184)
**Pagination Suivante**
- Implémenter le fonctionnement du bouton "Suivant" dans la pagination
- Validation des limites de résultats disponibles

```typescript
// TODO: Implémentation commune pour les deux boutons
const handlePageChange = (newPage: number) => {
  setLoading(true);
  // Requête API avec page = newPage
  // Mise à jour des résultats
  // Gestion des erreurs
};
```

### [`frontend/src/components/SearchComponent.tsx:616`](frontend/src/components/SearchComponent.tsx:616)
**Gestion des Suggestions**
- Implémenter la sélection des suggestions de recherche
- Remplacement automatique de la requête en cours
- Maintien du contexte de recherche

```typescript
const handleSuggestionSelect = (suggestion: string) => {
  // TODO: À implémenter
  setQuery({ ...query, q: suggestion });
  handleSearch({ ...query, q: suggestion });
};
```

### [`frontend/src/components/SearchComponent.tsx:626`](frontend/src/components/SearchComponent.tsx:626)
**Gestion des Corrections**
- Implémenter la sélection des corrections orthographiques
- Application automatique via API de corrections
- Confirmation utilisateur pour les corrections majeures

```typescript
const handleCorrectionSelect = (correction: string) => {
  // TODO: À implémenter
  setQuery({ ...query, q: correction });
  handleSearch({ ...query, q: correction });
  // Fermeture de la liste de corrections
};
```

---

## 📈 Priorisation des Tâches

### **Semaine 1 (Priorité Haute)**
1. Implémenter pagination ([`SimpleSearchComponent.tsx`](frontend/src/components/SimpleSearchComponent.tsx))
2. Créer page détail audiobook ([`Search.tsx`](frontend/src/pages/Search.tsx))

### **Semaine 2 (Priorité Moyenne)**
3. Intégrer suggestions de recherche ([`SearchComponent.tsx`](frontend/src/components/SearchComponent.tsx))
4. Ajouter corrections orthographiques

### **Semaine 3 (Priorité Basse)**
5. Tests d'intégration complets
6. Optimisations performance
7. Documentation utilisateur

---

## 🔧 État Technique

### ✅ **Infrastructure Stabilisée**
- Docker containers opérationnels
- Services démarrés automatiquement
- Timeouts et healthchecks configurés
- Optimisation build images

### 🔄 **Fonctionnalités Core Fonctionnelles**
- Authentification VoidAuth opérationnelle
- Dashboard administrateur fonctionnel
- API REST complète et documentée
- Recherche de base opérationnelle

### 📋 **Prochaines Fonctionnalités**
- Gestion complète du cycle de vie des audiobooks
- Interfaces utilisateur enhancées
- Synchronisation multi-instances
- Gestion des collections

---

## 🎯 Métriques de Succès

**Objectif Semaine 1 :**
- Interface recherche 100% fonctionnelle
- Navigation fluide vers les détails
- Pagination performante (>50% de satisfaction utilisateur)

**Objectif Semaine 2 :**
- Suggestions contextuelles efficaces (>80% d'acceptation)
- Corrections transparentes
- UX améliorée significativement

**Voir [`ROADMAP.md`](ROADMAP.md) pour l'évolution stratégique complète**

*Document mis à jour le 07/09/2025 après stabilisation containers Docker*