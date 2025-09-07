// Types pour la recherche avancée d'audiobooks

export interface SearchFilters {
  genres?: string[];
  authors?: string[];
  narrators?: string[];
  language?: string;
  min_duration?: number;
  max_duration?: number;
  min_rating?: number;
  max_rating?: number;
  publish_year_from?: number;
  publish_year_to?: number;
  explicit?: boolean;
  abridged?: boolean;
  instances?: string[];
  quality_min?: number;
}

export interface SearchQuery {
  q: string;
  filters?: SearchFilters;
  sort_by?: 'relevance' | 'title' | 'author' | 'duration' | 'rating' | 'date';
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface SearchResult {
  audiobook_id: number;
  title: string;
  authors: string[];
  narrators: string[];
  duration: number;
  language: string;
  genres: string[];
  rating: number;
  publish_year?: number;
  instance_name: string;
  instance_id: number;
  cover_path?: string;
  score: number;
}

export interface SearchResults {
  query: string;
  total_count: number;
  results: SearchResult[];
  suggestions: string[];
  corrections: string[];
  page: number;
  limit: number;
  has_more: boolean;
  execution_time_ms: number;
  instances_searched: string[];
}

export interface SearchHistory {
  id: number;
  query: string;
  filters: string;
  results_count: number;
  execution_time_ms: number;
  is_suggestion: boolean;
  source: string;
  created_at: string;
  last_used_at: string;
}

export interface SearchSuggestion {
  id: number;
  suggestion: string;
  category?: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
  last_used_at: string;
}

export interface AutoCompleteSuggestion {
  text: string;
  type: 'title' | 'author' | 'genre' | 'narrator';
  count: number;
}

export interface AutoCompleteResponse {
  query: string;
  suggestions: AutoCompleteSuggestion[];
  total_count: number;
}

export interface SearchStats {
  total_searches: number;
  average_execution_time_ms: number;
  top_queries: Array<{
    query: string;
    count: number;
  }>;
}