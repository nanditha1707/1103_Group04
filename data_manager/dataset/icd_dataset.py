from .dataset import Dataset


class IcdDataset(Dataset):
    """The ICD-11 dataset: disease codes and names."""

    @property
    def _columns_to_keep(self) -> dict[str, str]:
        return {
            "Code": "Code",
            "Title": "DiseaseName"
        }

    @property
    def _columns_to_uppercase(self) -> tuple[str, ...]:
        return ("Code", "DiseaseName")
