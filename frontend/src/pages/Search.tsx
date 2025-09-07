import React from 'react';
import SimpleSearchComponent from '../components/SimpleSearchComponent';
import { SearchResult } from '../types/search';

const Search: React.FC = () => {
  const handleResultSelect = (result: SearchResult) => {
    // TODO: Implement navigation to audiobook detail page
    console.log('Selected result:', result);
  };

  return (
    <div className="search-page">
      <div className="container">
        <h1>Recherche avancée</h1>
        <p className="page-description">
          Recherchez des livres audio dans toutes vos instances Audiobookshelf
        </p>

        <SimpleSearchComponent
          onResultSelect={handleResultSelect}
          placeholder="Titre, auteur, narrateur..."
        />
      </div>
    </div>
  );
};

export default Search;