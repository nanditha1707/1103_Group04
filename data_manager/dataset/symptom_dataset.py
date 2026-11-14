from .dataset import Dataset


class SymptomDataset(Dataset):
    @property
    def _columns_to_keep(self) -> dict[str, str]:
        return {
            "term": "term"
        }

    @property
    def _columns_to_uppercase(self) -> tuple[str, ...]:
        return ("term",)

    def load_terms(self) -> list[str]:
        symptoms_df = self.load_cleaned()
        if symptoms_df is None:
            return []

        return symptoms_df["term"].tolist()
