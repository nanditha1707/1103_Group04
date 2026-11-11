from .dataset import Dataset


class HsaDataset(Dataset):
    """The HSA dataset: registered drugs and their classification."""

    @property
    def _columns_to_keep(self) -> dict[str, str]:
        return {
            "Productname": "DrugName",
            "Dosageform": "Dosage",
            "Strength": "Strength",
            "Activeingredients": "ActiveIngredients",
            "ATCCode": "ATCCode",
            "Forensicclassification": "Classification"
        }

    @property
    def _columns_to_uppercase(self) -> tuple[str, ...]:
        return ("DrugName", "ActiveIngredients")
