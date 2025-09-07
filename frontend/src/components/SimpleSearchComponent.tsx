import React, { useState } from 'react';
import { SearchResults, SearchResult } from '../types/search';
import './SearchComponent.css';

interface SimpleSearchComponentProps {
  onResultSelect?: (result: SearchResult) => void;
  placeholder?: string;
}

const SimpleSearchComponent: React.FC<SimpleSearchComponentProps> = ({
  onResultSelect,
  placeholder = "Rechercher des livres audio..."
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q: query, page: 1, limit: 20 })
      });

      if (!response.ok) throw new Error('Erreur de recherche');

      const data: SearchResults = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h${minutes}m` : `${minutes}m`;
  };

  return (
    <div className="search-component">
      {/* Barre de recherche */}
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-container">
          <div className="search-input-wrapper">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={placeholder}
              className="search-input"
              autoComplete="off"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="clear-button"
              >
                ✕
              </button>
            )}
          </div>

          <button type="submit" className="search-button" disabled={loading || !query.trim()}>
            {loading ? 'Recherche...' : 'Rechercher'}
          </button>
        </div>
      </form>

      {/* Messages d'erreur */}
      {error && (
        <div className="search-error">
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Indicateur de chargement */}
      {loading && (
        <div className="search-loading">
          Recherche en cours...
        </div>
      )}

      {/* Résultats */}
      {results && !loading && (
        <div className="search-results">
          {/* En-tête des résultats */}
          <div className="results-header">
            <div className="results-info">
              <span className="results-count">
                {results.total_count} résultat{results.total_count !== 1 ? 's' : ''}
              </span>
              <span className="results-time">
                en {results.execution_time_ms}ms
              </span>
            </div>
          </div>

          {/* Liste des résultats */}
          <div className="results-list">
            {results.results.map((result) => (
              <div
                key={result.audiobook_id}
                className="result-item"
                onClick={() => onResultSelect && onResultSelect(result)}
              >
                <div className="result-cover">
                  {result.cover_path ? (
                    <img src={result.cover_path} alt={result.title} />
                  ) : (
                    <div className="no-cover">📖</div>
                  )}
                </div>

                <div className="result-info">
                  <h3 className="result-title">{result.title}</h3>

                  <div className="result-meta">
                    <div className="result-authors">
                      👤 {result.authors.join(', ')}
                    </div>

                    <div className="result-details">
                      <span className="duration">🕐 {formatDuration(result.duration)}</span>
                      <span className="language">{result.language.toUpperCase()}</span>
                      {result.publish_year && (
                        <span className="year">📅 {result.publish_year}</span>
                      )}
                    </div>

                    <div className="result-rating">
                      ⭐ {result.rating.toFixed(1)}
                    </div>
                  </div>

                  {result.genres.length > 0 && (
                    <div className="result-genres">
                      {result.genres.slice(0, 3).map((genre, index) => (
                        <span key={index} className="genre-tag">{genre}</span>
                      ))}
                      {result.genres.length > 3 && (
                        <span className="genre-more">+{result.genres.length - 3}</span>
                      )}
                    </div>
                  )}

                  <div className="result-instance">
                    <span className="instance-badge">{result.instance_name}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {results.has_more && (
            <div className="results-pagination">
              <button
                onClick={() => {/* TODO: Implement page change */}}
                disabled={results.page === 1}
                className="pagination-button"
              >
                Précédent
              </button>

              <span className="pagination-info">
                Page {results.page}
              </span>

              <button
                onClick={() => {/* TODO: Implement page change */}}
                disabled={!results.has_more}
                className="pagination-button"
              >
                Suivant
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SimpleSearchComponent;