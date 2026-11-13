from enum import Enum

class Classification(Enum):
    """
    HSA medicine classifications. The classifications to be ranked will come from another file or class.

    IMPORTANT!: the members are written from LEAST to MOST restrictive.
    That order is the single place that decides which classification is stricter, 
    so do not reorder them. 
    A new classification must be inserted at the position that matches how strict it is.
    """

    GENERAL_SALE_LIST = "General Sale List"
    PHARMACY_ONLY = "Pharmacy Only"
    PRESCRIPTION_ONLY = "Prescription Only"

    @classmethod
    def from_text(cls, text) -> "Classification | None":
        """
        Turn text from the HSA dataset into a Classification.
        """
        try:
            cleaned_text = str(text).strip()
            return cls(cleaned_text)
        except ValueError:
            return None


    @classmethod
    def least_restrictive(
        cls, classifications: list["Classification"]
    ) -> "Classification | None":
        """
        Return the least restrictive classification in the list, 
        or None if the list is empty.
        """

        # Members are written least to most restrictive, 
        # so the first one found in the list is the least restrictive.
        for classification in cls:
            if classification in classifications:
                return classification
        return None


    @classmethod
    def most_restrictive(
        cls, classifications: list["Classification"]
    ) -> "Classification | None":
        """Return the most restrictive classification in the list, or
        None if the list is empty."""

        # Starts from the last value instead,
        # so the first one found in the list is the most restrictive.
        for classification in reversed(cls):
            if classification in classifications:
                return classification
        return None
