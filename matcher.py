import re
from typing import Optional, Set
from rapidfuzz import fuzz
from question_bank import PREDEFINED_QUESTIONS, QuestionEntry

# Common negation terms to check against
NEGATION_WORDS: Set[str] = {
    "without", "not", "except", "excluding", "never", "no", "instead", "don't", "doesn't"
}

# Verbs/synonyms to standardize during normalization
SYNONYM_MAP = {
    "show": "display",
    "list": "display",
    "give": "display",
    "fetch": "display",
    "find": "display",
    "get": "display",
    "select": "display"
}

class Matcher:
    """
    Handles Case 1 fuzzy matching for predefined questions using RapidFuzz,
    synonym normalization, and a strict Negation Guard safety check.
    """

    def __init__(self, threshold: float = 90.0):
        self.threshold = threshold

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalizes input text by lowering case, stripping non-alphanumeric chars,
        and mapping common query verb synonyms to standard terms.
        """
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        words = text.split()
        normalized_words = [SYNONYM_MAP.get(word, word) for word in words]
        return " ".join(normalized_words)

    @staticmethod
    def extract_negations(text: str) -> Set[str]:
        """Extracts any negation words present in the text, safely ignoring function parentheses/symbols."""
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        words = set(clean_text.split())
        return words.intersection(NEGATION_WORDS)

    def match(self, user_question: str) -> Optional[QuestionEntry]:
        """
        Matches a user question against the 70 predefined questions.
        
        Returns the QuestionEntry if fuzzy score >= threshold and Negation Guard passes.
        Returns None otherwise (falling through to Case 2).
        """
        normalized_user = self.normalize_text(user_question)
        user_negations = self.extract_negations(user_question)

        best_match: Optional[QuestionEntry] = None
        highest_score: float = 0.0

        for entry in PREDEFINED_QUESTIONS:
            stored_q = entry["question"]
            normalized_stored = self.normalize_text(stored_q)

            # Compute fuzzy token sort ratio
            score = fuzz.token_sort_ratio(normalized_user, normalized_stored)

            if score > highest_score:
                highest_score = score
                best_match = entry

        # Check threshold requirement
        if highest_score < self.threshold or best_match is None:
            return None

        # Negation Guard Check:
        # If user question has a negation word that the matched question lacks (or vice-versa), reject match
        stored_negations = self.extract_negations(best_match["question"])
        if user_negations != stored_negations:
            return None

        return best_match

# Singleton instance for export
matcher = Matcher(threshold=90.0)