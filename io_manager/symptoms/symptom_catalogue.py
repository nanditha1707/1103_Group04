import difflib
from collections.abc import Iterable


class SymptomCatalogue:
    """
    The list of known symptom names, used to match what the patient types under "Other Symptoms".
    The list was grabbed and cleaned from the NIH UMLS Metathesaurus, 
    which is a large dataset of medical terms. 
    The list is preloaded in the data_manager, and passed to the IO manager at startup, 
    to ensure that IO manager does not infringe upon the responsibilities of the data manager.

    Since the file is copied by the dockerfile into the image, 
    it is not necessary to guard against an empty or missing list.
    """

    # How similar a typed symptom must be to suggest a close match. 
    # 0.6 is 60% similarity, which is a good balance between being too strict and too lenient.
    MATCH_CUTOFF = 0.6

    # Iterable as terms are only read once, 
    # and order does not play a role in the matching process.
    def __init__(
        self, terms: Iterable[str]
    ) -> None:
        self.__terms = tuple(terms)
        # Freezes the list of terms to speed up lookups.
        # The dataset does not change after being loaded so this is safe to do.
        self.__term_set = frozenset(self.__terms)

    def match(self, text: str) -> tuple[str | None, bool]:
        """
        Return (symptom, True) for an exact match, (closest symptom, False) for a close match, 
        or (None, False) for no match.
        """
        if text in self.__term_set:
            return text, True

        close_matches = difflib.get_close_matches(
            text, self.__terms, n=1, cutoff=self.MATCH_CUTOFF
        )
        if close_matches:
            return close_matches[0], False
        return None, False
