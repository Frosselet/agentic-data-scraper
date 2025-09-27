"""
SKOS Vocabulary Expansion System

Integrates public SKOS vocabularies to enhance semantic coverage for business
and technical terms. Implements a fallback chain: local → public → fuzzy matching.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import json
import aiohttp
from dataclasses import dataclass
from urllib.parse import quote_plus
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


@dataclass
class VocabularySource:
    """Configuration for a public SKOS vocabulary source"""
    name: str
    base_url: str
    search_endpoint: str
    concept_endpoint: str
    headers: Dict[str, str]
    languages: List[str]
    categories: List[str]  # technology, data_quality, business, etc.


@dataclass
class ConceptMatch:
    """Matched concept from vocabulary expansion"""
    term: str
    preferred_label: str
    concept_uri: str
    source: str
    confidence: float
    definition: Optional[str] = None
    alt_labels: List[str] = None
    broader_concepts: List[str] = None


class SKOSVocabularyExpander:
    """
    Expands SKOS vocabulary coverage using public resources.

    Provides comprehensive semantic term resolution with fallback chain:
    1. Local SKOS vocabulary (existing)
    2. Public vocabularies (Wikidata, DBpedia, etc.)
    3. Fuzzy matching with similarity scoring
    4. Term suggestion system
    """

    def __init__(self, cache_dir: str = "data/vocabulary_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Configure public vocabulary sources
        self.vocabulary_sources = self._configure_vocabulary_sources()

        # Cache for resolved terms
        self.term_cache = {}
        self.load_cache()

    def _configure_vocabulary_sources(self) -> List[VocabularySource]:
        """Configure public SKOS vocabulary sources"""
        return [
            # Wikidata - comprehensive knowledge base
            VocabularySource(
                name="wikidata",
                base_url="https://www.wikidata.org",
                search_endpoint="/w/api.php",
                concept_endpoint="/entity/{entity_id}",
                headers={"User-Agent": "SKOS-Expander/1.0"},
                languages=["en", "tr", "es", "fr", "de"],
                categories=["technology", "business", "general"]
            ),

            # DBpedia - Wikipedia-based structured data
            VocabularySource(
                name="dbpedia",
                base_url="https://dbpedia.org",
                search_endpoint="/sparql",
                concept_endpoint="/resource/{resource_name}",
                headers={"Accept": "application/json"},
                languages=["en"],
                categories=["technology", "software", "business"]
            ),

            # Library of Congress Subject Headings via LOC API
            VocabularySource(
                name="loc_subjects",
                base_url="https://id.loc.gov",
                search_endpoint="/search/",
                concept_endpoint="/authorities/subjects/{subject_id}",
                headers={"Accept": "application/json"},
                languages=["en"],
                categories=["business", "general", "data_quality"]
            ),

            # EU Vocabularies (EuroVoc)
            VocabularySource(
                name="eurovoc",
                base_url="https://op.europa.eu/en/web/eu-vocabularies",
                search_endpoint="/sparql",
                concept_endpoint="/resource/{concept_id}",
                headers={"Accept": "application/rdf+xml"},
                languages=["en", "tr", "es", "fr", "de"],
                categories=["business", "technology", "general"]
            )
        ]

    async def expand_term(self, term: str, language: str = "en") -> Optional[ConceptMatch]:
        """
        Expand a term using public vocabularies with fallback chain.

        Args:
            term: Term to expand
            language: Target language for results

        Returns:
            ConceptMatch if found, None otherwise
        """
        # Check cache first
        cache_key = f"{term.lower()}_{language}"
        if cache_key in self.term_cache:
            return self.term_cache[cache_key]

        # Clean term for better matching
        cleaned_term = self._clean_term(term)

        try:
            # Try each vocabulary source
            for source in self.vocabulary_sources:
                if language in source.languages:
                    match = await self._search_vocabulary_source(
                        cleaned_term, source, language
                    )
                    if match and match.confidence > 0.7:  # High confidence threshold
                        self.term_cache[cache_key] = match
                        await self._save_cache()
                        return match

            # Fuzzy matching as fallback
            fuzzy_match = await self._fuzzy_term_matching(cleaned_term, language)
            if fuzzy_match and fuzzy_match.confidence > 0.6:  # Lower threshold for fuzzy
                self.term_cache[cache_key] = fuzzy_match
                await self._save_cache()
                return fuzzy_match

            return None

        except Exception as e:
            logger.warning(f"Vocabulary expansion failed for '{term}': {e}")
            return None

    async def _search_vocabulary_source(
        self,
        term: str,
        source: VocabularySource,
        language: str
    ) -> Optional[ConceptMatch]:
        """Search a specific vocabulary source for the term"""

        if source.name == "wikidata":
            return await self._search_wikidata(term, language)
        elif source.name == "dbpedia":
            return await self._search_dbpedia(term, language)
        elif source.name == "loc_subjects":
            return await self._search_loc_subjects(term, language)
        elif source.name == "eurovoc":
            return await self._search_eurovoc(term, language)

        return None

    async def _search_wikidata(self, term: str, language: str) -> Optional[ConceptMatch]:
        """Search Wikidata for term"""
        try:
            async with aiohttp.ClientSession() as session:
                # Wikidata search API
                search_url = f"https://www.wikidata.org/w/api.php"
                params = {
                    'action': 'wbsearchentities',
                    'search': term,
                    'language': language,
                    'format': 'json',
                    'limit': 5,
                    'type': 'item'
                }

                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'search' in data and data['search']:
                            entity = data['search'][0]  # Take first result

                            return ConceptMatch(
                                term=term,
                                preferred_label=entity.get('label', term),
                                concept_uri=f"https://www.wikidata.org/entity/{entity['id']}",
                                source="wikidata",
                                confidence=self._calculate_similarity(term, entity.get('label', '')),
                                definition=entity.get('description'),
                                alt_labels=entity.get('aliases', [])
                            )
            return None
        except Exception as e:
            logger.debug(f"Wikidata search failed for '{term}': {e}")
            return None

    async def _search_dbpedia(self, term: str, language: str) -> Optional[ConceptMatch]:
        """Search DBpedia for term"""
        try:
            async with aiohttp.ClientSession() as session:
                # DBpedia SPARQL endpoint
                sparql_query = f"""
                SELECT DISTINCT ?resource ?label ?comment WHERE {{
                    ?resource rdfs:label ?label .
                    OPTIONAL {{ ?resource rdfs:comment ?comment }}
                    FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{term}")))
                    FILTER(LANG(?label) = "{language}")
                }} LIMIT 5
                """

                sparql_url = "https://dbpedia.org/sparql"
                params = {
                    'query': sparql_query,
                    'format': 'json'
                }

                async with session.get(sparql_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'results' in data and 'bindings' in data['results']:
                            bindings = data['results']['bindings']
                            if bindings:
                                result = bindings[0]
                                label = result['label']['value']

                                return ConceptMatch(
                                    term=term,
                                    preferred_label=label,
                                    concept_uri=result['resource']['value'],
                                    source="dbpedia",
                                    confidence=self._calculate_similarity(term, label),
                                    definition=result.get('comment', {}).get('value')
                                )
            return None
        except Exception as e:
            logger.debug(f"DBpedia search failed for '{term}': {e}")
            return None

    async def _search_loc_subjects(self, term: str, language: str) -> Optional[ConceptMatch]:
        """Search Library of Congress Subject Headings"""
        try:
            async with aiohttp.ClientSession() as session:
                # LOC search API
                search_url = f"https://id.loc.gov/search/"
                params = {
                    'q': term,
                    'format': 'json',
                    'count': 5,
                    'rdftype': 'Concept'
                }

                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list) and data:
                            result = data[0]

                            return ConceptMatch(
                                term=term,
                                preferred_label=result.get('title', term),
                                concept_uri=result.get('uri', ''),
                                source="loc_subjects",
                                confidence=self._calculate_similarity(term, result.get('title', '')),
                                definition=result.get('description')
                            )
            return None
        except Exception as e:
            logger.debug(f"LOC Subjects search failed for '{term}': {e}")
            return None

    async def _search_eurovoc(self, term: str, language: str) -> Optional[ConceptMatch]:
        """Search EuroVoc thesaurus"""
        try:
            async with aiohttp.ClientSession() as session:
                # EuroVoc SPARQL endpoint (simplified approach)
                sparql_query = f"""
                SELECT DISTINCT ?concept ?prefLabel ?definition WHERE {{
                    ?concept skos:prefLabel ?prefLabel .
                    OPTIONAL {{ ?concept skos:definition ?definition }}
                    FILTER(CONTAINS(LCASE(STR(?prefLabel)), LCASE("{term}")))
                    FILTER(LANG(?prefLabel) = "{language}")
                }} LIMIT 5
                """

                # Note: This is a simplified implementation
                # In production, you'd use the actual EuroVoc SPARQL endpoint
                return None

        except Exception as e:
            logger.debug(f"EuroVoc search failed for '{term}': {e}")
            return None

    async def _fuzzy_term_matching(self, term: str, language: str) -> Optional[ConceptMatch]:
        """Perform fuzzy matching against cached terms and common vocabulary"""

        # Create a simple knowledge base for common terms
        common_terms = self._get_common_terms_kb()

        best_match = None
        best_score = 0.0

        for kb_term, kb_data in common_terms.items():
            similarity = self._calculate_similarity(term.lower(), kb_term.lower())
            if similarity > best_score and similarity > 0.6:
                best_score = similarity
                best_match = ConceptMatch(
                    term=term,
                    preferred_label=kb_data['label'],
                    concept_uri=kb_data['uri'],
                    source="fuzzy_kb",
                    confidence=similarity,
                    definition=kb_data.get('definition'),
                    alt_labels=kb_data.get('alt_labels', [])
                )

        return best_match

    def _get_common_terms_kb(self) -> Dict[str, Dict]:
        """Get knowledge base of common business/technical terms"""
        return {
            # Technology terms
            "aws": {
                "label": "Amazon Web Services",
                "uri": "http://vocab.example.org/tech/aws",
                "definition": "Cloud computing platform by Amazon",
                "alt_labels": ["Amazon Web Services", "AWS"]
            },
            "snowflake": {
                "label": "Snowflake Data Platform",
                "uri": "http://vocab.example.org/tech/snowflake",
                "definition": "Cloud-based data warehousing platform",
                "alt_labels": ["Snowflake", "Snowflake DB"]
            },
            "dbt": {
                "label": "Data Build Tool",
                "uri": "http://vocab.example.org/tech/dbt",
                "definition": "SQL-based data transformation tool",
                "alt_labels": ["dbt", "Data Build Tool"]
            },
            "datadog": {
                "label": "Datadog Monitoring",
                "uri": "http://vocab.example.org/tech/datadog",
                "definition": "Cloud monitoring and analytics platform",
                "alt_labels": ["Datadog"]
            },

            # Data quality terms
            "accuracy": {
                "label": "Data Accuracy",
                "uri": "http://vocab.example.org/quality/accuracy",
                "definition": "Degree to which data correctly represents real-world values",
                "alt_labels": ["accuracy", "correctness"]
            },
            "completeness": {
                "label": "Data Completeness",
                "uri": "http://vocab.example.org/quality/completeness",
                "definition": "Measure of missing or null values in dataset",
                "alt_labels": ["completeness", "coverage"]
            },
            "currency": {
                "label": "Data Currency",
                "uri": "http://vocab.example.org/quality/currency",
                "definition": "How up-to-date or fresh the data is",
                "alt_labels": ["currency", "freshness", "timeliness"]
            },

            # Time series terms
            "time series": {
                "label": "Time Series Data",
                "uri": "http://vocab.example.org/analytics/timeseries",
                "definition": "Sequence of data points indexed in time order",
                "alt_labels": ["time series", "temporal data", "chronological data"]
            }
        }

    def _clean_term(self, term: str) -> str:
        """Clean and normalize term for better matching"""
        # Remove leading hyphens and whitespace
        cleaned = term.strip().lstrip('- ')

        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Convert to lowercase for matching
        return cleaned.lower()

    def _calculate_similarity(self, term1: str, term2: str) -> float:
        """Calculate similarity between two terms using sequence matching"""
        if not term1 or not term2:
            return 0.0

        # Basic sequence matching
        similarity = SequenceMatcher(None, term1.lower(), term2.lower()).ratio()

        # Boost exact matches
        if term1.lower() == term2.lower():
            similarity = 1.0
        # Boost if one term contains the other
        elif term1.lower() in term2.lower() or term2.lower() in term1.lower():
            similarity = min(0.9, similarity + 0.2)

        return similarity

    def load_cache(self):
        """Load term cache from disk"""
        cache_file = self.cache_dir / "term_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Convert dict back to ConceptMatch objects
                    for key, data in cache_data.items():
                        if isinstance(data, dict) and 'term' in data:
                            self.term_cache[key] = ConceptMatch(**data)
            except Exception as e:
                logger.warning(f"Failed to load term cache: {e}")

    async def _save_cache(self):
        """Save term cache to disk"""
        cache_file = self.cache_dir / "term_cache.json"
        try:
            # Convert ConceptMatch objects to dicts for JSON serialization
            cache_data = {}
            for key, match in self.term_cache.items():
                if isinstance(match, ConceptMatch):
                    cache_data[key] = {
                        'term': match.term,
                        'preferred_label': match.preferred_label,
                        'concept_uri': match.concept_uri,
                        'source': match.source,
                        'confidence': match.confidence,
                        'definition': match.definition,
                        'alt_labels': match.alt_labels,
                        'broader_concepts': match.broader_concepts
                    }

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Failed to save term cache: {e}")

    async def suggest_terms(self, partial_term: str, limit: int = 5) -> List[str]:
        """Suggest terms based on partial input"""
        suggestions = []

        # Check cached terms
        for cached_match in self.term_cache.values():
            if isinstance(cached_match, ConceptMatch):
                if partial_term.lower() in cached_match.preferred_label.lower():
                    suggestions.append(cached_match.preferred_label)

        # Check common terms knowledge base
        common_terms = self._get_common_terms_kb()
        for term, data in common_terms.items():
            if partial_term.lower() in term.lower() or partial_term.lower() in data['label'].lower():
                suggestions.append(data['label'])

        # Remove duplicates and limit results
        suggestions = list(set(suggestions))[:limit]
        return sorted(suggestions)

    async def batch_expand_terms(
        self,
        terms: List[str],
        language: str = "en"
    ) -> Dict[str, Optional[ConceptMatch]]:
        """Expand multiple terms in batch for efficiency"""

        # Create tasks for concurrent processing
        tasks = [self.expand_term(term, language) for term in terms]

        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build results dictionary
        expanded_terms = {}
        for term, result in zip(terms, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to expand term '{term}': {result}")
                expanded_terms[term] = None
            else:
                expanded_terms[term] = result

        return expanded_terms

    def get_expansion_statistics(self) -> Dict[str, int]:
        """Get statistics about vocabulary expansion usage"""
        stats = {
            'cached_terms': len(self.term_cache),
            'sources_configured': len(self.vocabulary_sources)
        }

        # Count by source
        source_counts = {}
        for match in self.term_cache.values():
            if isinstance(match, ConceptMatch):
                source = match.source
                source_counts[source] = source_counts.get(source, 0) + 1

        stats['by_source'] = source_counts
        return stats