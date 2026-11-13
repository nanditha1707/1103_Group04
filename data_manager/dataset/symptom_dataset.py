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
