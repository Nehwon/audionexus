import React, { useState } from 'react';
import { SearchQuery, SearchResults, SearchResult } from '../types/search';
import './SearchComponent.css';

interface SearchComponentProps {
  onResultSelect?: (result: SearchResult) => void;
  placeholder?: string;
  showFilters?: boolean;
  showHistory?: boolean;
  compact?: boolean;
}

export const SearchComponent: React.FC<SearchComponentProps> = ({
  onResultSelect,
  placeholder = "Rechercher des livres audio...",
  showFilters = true,
  showHistory = true,
  compact = false
}) => {
  // États principaux
  const [query, setQuery] = useState<SearchQuery>({ q: '' });
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [searchHistory, setSearchHistory] = useState<SearchHistory[]>([]);
  const [showHistoryDropdown, setShowHistoryDropdown] = useState(false);
  const [autoCompleteSuggestions, setAutoCompleteSuggestions] = useState<any[]>([]);
  const [showAutoComplete, setShowAutoComplete] = useState(false);

  // Références
  const searchInputRef = useRef<HTMLInputElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout>();

  // Gestion de la recherche
  const handleSearch = useCallback(async (searchQuery: SearchQuery) => {
    if (!searchQuery.q.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchQuery)
      });

      if (!response.ok) throw new Error('Erreur de recherche');

      const data: SearchResults = await response.json();
      setResults(data);

      // Recharger l'historique après une recherche
      loadSearchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  }, []);

  // Gestion de l'auto-complétion
  const handleAutoComplete = useCallback(async (input: string) => {
    if (input.length < 2) {
      setAutoCompleteSuggestions([]);
      setShowAutoComplete(false);
      return;
    }

    try {
      const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(input)}`);
      const suggestions = await response.json();
      setAutoCompleteSuggestions(suggestions.suggestions || []);
      setShowAutoComplete(true);
    } catch (err) {
      console.error('Erreur auto-complétion:', err);
    }
  }, []);

  // Recherche avec debounce
  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      if (query.q) {
        handleAutoComplete(query.q);
      } else {
        setShowAutoComplete(false);
      }
    }, 300);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [query.q, handleAutoComplete]);

  // Charger l'historique des recherches
  const loadSearchHistory = async () => {
    if (!showHistory) return;

    try {
      const response = await fetch('/api/search/history');
      const history = await response.json();
      setSearchHistory(history);
    } catch (err) {
      console.error('Erreur chargement historique:', err);
    }
  };

  // Effets
  useEffect(() => {
    loadSearchHistory();
  }, [showHistory]);

  // Gestionnaires d'événements
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query);
    setShowAutoComplete(false);
  };

  const handleQueryChange = (value: string) => {
    setQuery(prev => ({ ...prev, q: value }));
  };

  const handleFilterChange = (filters: Partial<SearchFilters>) => {
    setQuery(prev => ({
      ...prev,
      filters: { ...prev.filters, ...filters }
    }));
  };

  const handleSortChange = (sort_by: string, sort_order: 'asc' | 'desc' = 'desc') => {
    const validSortBy = sort_by as 'relevance' | 'title' | 'author' | 'duration' | 'rating' | 'date';
    setQuery(prev => ({ ...prev, sort_by: validSortBy, sort_order }));
    if (query.q) handleSearch({ ...query, sort_by: validSortBy, sort_order });
  };

  const handlePageChange = (page: number) => {
    const newQuery = { ...query, page };
    setQuery(newQuery);
    handleSearch(newQuery);
  };

  const handleHistorySelect = (historyItem: SearchHistory) => {
    const searchQuery: SearchQuery = {
      q: historyItem.query,
      filters: historyItem.filters ? JSON.parse(historyItem.filters) : undefined
    };
    setQuery(searchQuery);
    handleSearch(searchQuery);
    setShowHistoryDropdown(false);
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setQuery(prev => ({ ...prev, q: suggestion }));
    handleSearch({ ...query, q: suggestion });
    setShowAutoComplete(false);
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  };

  return (
    <div className={`search-component ${compact ? 'compact' : ''}`}>
      {/* Barre de recherche principale */}
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-container">
          <div className="search-input-wrapper">
            <Search className="search-icon" size={20} />
            <input
              ref={searchInputRef}
              type="text"
              value={query.q}
              onChange={(e) => handleQueryChange(e.target.value)}
              placeholder={placeholder}
              className="search-input"
              autoComplete="off"
            />
            {query.q && (
              <button
                type="button"
                onClick={() => handleQueryChange('')}
                className="clear-button"
              >
                <X size={16} />
              </button>
            )}
          </div>

          {/* Boutons d'action */}
          <div className="search-actions">
            {showFilters && (
              <button
                type="button"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className={`filter-toggle ${showAdvancedFilters ? 'active' : ''}`}
              >
                <Filter size={16} />
                Filtres
                {showAdvancedFilters ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            )}

            {showHistory && searchHistory.length > 0 && (
              <div className="history-dropdown">
                <button
                  type="button"
                  onClick={() => setShowHistoryDropdown(!showHistoryDropdown)}
                  className="history-toggle"
                >
                  <Clock size={16} />
                  Historique
                  {showHistoryDropdown ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>

                {showHistoryDropdown && (
                  <div className="history-menu">
                    {searchHistory.slice(0, 10).map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleHistorySelect(item)}
                        className="history-item"
                      >
                        <span className="history-query">{item.query}</span>
                        <span className="history-date">
                          {new Date(item.created_at).toLocaleDateString()}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            <button type="submit" className="search-button" disabled={loading || !query.q.trim()}>
              {loading ? 'Recherche...' : 'Rechercher'}
            </button>
          </div>
        </div>

        {/* Auto-complétion */}
        {showAutoComplete && autoCompleteSuggestions.length > 0 && (
          <div className="autocomplete-menu">
            {autoCompleteSuggestions.slice(0, 8).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionSelect(suggestion.text)}
                className="autocomplete-item"
              >
                <span className="suggestion-text">{suggestion.text}</span>
                <span className="suggestion-type">{suggestion.type}</span>
                <span className="suggestion-count">({suggestion.count})</span>
              </button>
            ))}
          </div>
        )}
      </form>

      {/* Filtres avancés */}
      {showAdvancedFilters && (
        <AdvancedFilters
          filters={query.filters || {}}
          onFilterChange={handleFilterChange}
        />
      )}

      {/* Messages d'erreur */}
      {error && (
        <div className="search-error">
          <span>{error}</span>
          <button onClick={() => setError(null)}><X size={14} /></button>
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
        <SearchResults
          results={results}
          onResultSelect={onResultSelect}
          onPageChange={handlePageChange}
          onSortChange={handleSortChange}
          currentSort={query.sort_by}
          currentSortOrder={query.sort_order}
        />
      )}
    </div>
  );
};

// Composant des filtres avancés
interface AdvancedFiltersProps {
  filters: SearchFilters;
  onFilterChange: (filters: Partial<SearchFilters>) => void;
}

const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({ filters, onFilterChange }) => {
  const [localFilters, setLocalFilters] = useState<SearchFilters>(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleChange = (key: keyof SearchFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const addArrayItem = (key: 'genres' | 'authors' | 'narrators' | 'instances', value: string) => {
    const current = localFilters[key] || [];
    if (!current.includes(value)) {
      handleChange(key, [...current, value]);
    }
  };

  const removeArrayItem = (key: 'genres' | 'authors' | 'narrators' | 'instances', value: string) => {
    const current = localFilters[key] || [];
    handleChange(key, current.filter(item => item !== value));
  };

  return (
    <div className="advanced-filters">
      <div className="filters-grid">
        {/* Genres */}
        <div className="filter-group">
          <label>
            <HardDrive size={16} />
            Genres
          </label>
          <ArrayInput
            values={localFilters.genres || []}
            onAdd={(value) => addArrayItem('genres', value)}
            onRemove={(value) => removeArrayItem('genres', value)}
            placeholder="Ajouter un genre..."
          />
        </div>

        {/* Auteurs */}
        <div className="filter-group">
          <label>
            <Users size={16} />
            Auteurs
          </label>
          <ArrayInput
            values={localFilters.authors || []}
            onAdd={(value) => addArrayItem('authors', value)}
            onRemove={(value) => removeArrayItem('authors', value)}
            placeholder="Ajouter un auteur..."
          />
        </div>

        {/* Narrateurs */}
        <div className="filter-group">
          <label>
            <Mic size={16} />
            Narrateurs
          </label>
          <ArrayInput
            values={localFilters.narrators || []}
            onAdd={(value) => addArrayItem('narrators', value)}
            onRemove={(value) => removeArrayItem('narrators', value)}
            placeholder="Ajouter un narrateur..."
          />
        </div>

        {/* Langue */}
        <div className="filter-group">
          <label>
            <Globe size={16} />
            Langue
          </label>
          <select
            value={localFilters.language || ''}
            onChange={(e) => handleChange('language', e.target.value || undefined)}
          >
            <option value="">Toutes les langues</option>
            <option value="fr">Français</option>
            <option value="en">Anglais</option>
            <option value="es">Espagnol</option>
            <option value="de">Allemand</option>
            <option value="it">Italien</option>
          </select>
        </div>

        {/* Durée */}
        <div className="filter-group">
          <label>Durée (minutes)</label>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="Min"
              value={localFilters.min_duration ? localFilters.min_duration / 60 : ''}
              onChange={(e) => handleChange('min_duration', e.target.value ? parseInt(e.target.value) * 60 : undefined)}
            />
            <input
              type="number"
              placeholder="Max"
              value={localFilters.max_duration ? localFilters.max_duration / 60 : ''}
              onChange={(e) => handleChange('max_duration', e.target.value ? parseInt(e.target.value) * 60 : undefined)}
            />
          </div>
        </div>

        {/* Année de publication */}
        <div className="filter-group">
          <label>
            <Calendar size={16} />
            Année de publication
          </label>
          <div className="range-inputs">
            <input
              type="number"
              placeholder="De"
              min="1900"
              max={new Date().getFullYear()}
              value={localFilters.publish_year_from || ''}
              onChange={(e) => handleChange('publish_year_from', e.target.value ? parseInt(e.target.value) : undefined)}
            />
            <input
              type="number"
              placeholder="À"
              min="1900"
              max={new Date().getFullYear()}
              value={localFilters.publish_year_to || ''}
              onChange={(e) => handleChange('publish_year_to', e.target.value ? parseInt(e.target.value) : undefined)}
            />
          </div>
        </div>

        {/* Note */}
        <div className="filter-group">
          <label>
            <Star size={16} />
            Note minimum
          </label>
          <select
            value={localFilters.min_rating || ''}
            onChange={(e) => handleChange('min_rating', e.target.value ? parseFloat(e.target.value) : undefined)}
          >
            <option value="">Toutes les notes</option>
            <option value="4.5">4.5+ étoiles</option>
            <option value="4.0">4.0+ étoiles</option>
            <option value="3.5">3.5+ étoiles</option>
            <option value="3.0">3.0+ étoiles</option>
          </select>
        </div>

        {/* Autres options */}
        <div className="filter-group">
          <label>Autres</label>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={localFilters.explicit === false}
                onChange={(e) => handleChange('explicit', e.target.checked ? false : undefined)}
              />
              Sans contenu explicite
            </label>
            <label>
              <input
                type="checkbox"
                checked={localFilters.abridged === false}
                onChange={(e) => handleChange('abridged', e.target.checked ? false : undefined)}
              />
              Version intégrale seulement
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};

// Composant pour gérer les tableaux (genres, auteurs, etc.)
interface ArrayInputProps {
  values: string[];
  onAdd: (value: string) => void;
  onRemove: (value: string) => void;
  placeholder: string;
}

const ArrayInput: React.FC<ArrayInputProps> = ({ values, onAdd, onRemove, placeholder }) => {
  const [input, setInput] = useState('');

  const handleAdd = () => {
    if (input.trim()) {
      onAdd(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAdd();
    }
  };

  return (
    <div className="array-input">
      <div className="array-values">
        {values.map((value, index) => (
          <span key={index} className="array-value">
            {value}
            <button onClick={() => onRemove(value)}>
              <X size={12} />
            </button>
          </span>
        ))}
      </div>
      <div className="array-input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
        />
        <button type="button" onClick={handleAdd}>+</button>
      </div>
    </div>
  );
};

// Composant d'affichage des résultats
interface SearchResultsProps {
  results: SearchResults;
  onResultSelect?: (result: SearchResult) => void;
  onPageChange: (page: number) => void;
  onSortChange: (sortBy: string, sortOrder?: 'asc' | 'desc') => void;
  currentSort?: string;
  currentSortOrder?: 'asc' | 'desc';
}

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  onResultSelect,
  onPageChange,
  onSortChange,
  currentSort = 'relevance',
  currentSortOrder = 'desc'
}) => {
  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return hours > 0 ? `${hours}h${minutes}m` : `${minutes}m`;
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <Star
        key={i}
        size={14}
        className={i < Math.floor(rating) ? 'star-filled' : 'star-empty'}
        fill={i < Math.floor(rating) ? 'currentColor' : 'none'}
      />
    ));
  };

  return (
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

        <div className="results-actions">
          <select
            value={currentSort}
            onChange={(e) => onSortChange(e.target.value, currentSortOrder)}
          >
            <option value="relevance">Pertinence</option>
            <option value="title">Titre</option>
            <option value="author">Auteur</option>
            <option value="duration">Durée</option>
            <option value="rating">Note</option>
            <option value="date">Date</option>
          </select>

          <button
            onClick={() => onSortChange(currentSort, currentSortOrder === 'asc' ? 'desc' : 'asc')}
            className="sort-order-button"
          >
            {currentSortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
          </button>
        </div>
      </div>

      {/* Suggestions et corrections */}
      {(results.suggestions.length > 0 || results.corrections.length > 0) && (
        <div className="results-suggestions">
          {results.suggestions.length > 0 && (
            <div className="suggestions">
              <span>Suggestions: </span>
              {results.suggestions.map((suggestion, index) => (
                <button key={index} onClick={() => {/* TODO: Implement suggestion selection */}}>
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          {results.corrections.length > 0 && (
            <div className="corrections">
              <span>Corrections: </span>
              {results.corrections.map((correction, index) => (
                <button key={index} onClick={() => {/* TODO: Implement correction selection */}}>
                  {correction}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

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
                  <Users size={14} />
                  {result.authors.join(', ')}
                </div>

                {result.narrators.length > 0 && (
                  <div className="result-narrators">
                    <Mic size={14} />
                    {result.narrators.join(', ')}
                  </div>
                )}

                <div className="result-details">
                  <span className="duration">{formatDuration(result.duration)}</span>
                  <span className="language">{result.language.toUpperCase()}</span>
                  {result.publish_year && (
                    <span className="year">{result.publish_year}</span>
                  )}
                </div>

                <div className="result-rating">
                  {renderStars(result.rating)}
                  <span className="rating-text">({result.rating.toFixed(1)})</span>
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

            <div className="result-actions">
              <button className="result-menu-button">
                <MoreHorizontal size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {results.has_more && (
        <div className="results-pagination">
          <button
            onClick={() => onPageChange(results.page - 1)}
            disabled={results.page === 1}
            className="pagination-button"
          >
            Précédent
          </button>

          <span className="pagination-info">
            Page {results.page}
          </span>

          <button
            onClick={() => onPageChange(results.page + 1)}
            disabled={!results.has_more}
            className="pagination-button"
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchComponent;