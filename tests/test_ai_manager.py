import json
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai_manager import Action, AIManager, AIModel, EmptyReplyError, ErrorClassifier, ModelFallback
from ai_manager.constants import CONTACT_SUPPORT_MESSAGE
from ai_manager.output_validator import OutputValidator
from ai_manager.prompt_builder import PromptBuilder
from ai_manager.reply_parser import ReplyParser
from fakes import FakeAIProvider


class TestAIManager:
    ICD_DF = pd.DataFrame({"Code": ["CA00"], "DiseaseName": ["COMMON COLD"]})
    HSA_DF = pd.DataFrame({"DrugName": ["PARACETAMOL"], "ActiveIngredients": ["PARACETAMOL"]})
    ANSWERS = {"gender": "F", "age": "20", "current_symptoms": ["COUGH"]}

    @staticmethod
    def __reply():
        return json.dumps({
            "primary_diagnosis_ICD11_Title": "common cold",
            "primary_diagnosis_ICD11_Code": "ca00",
            "primary_diagnosis_explanation": "Cold symptoms",
            "primary_diagnosis_medicine_1": "paracetamol",
            "primary_diagnosis_medicine_2": "paracetamol",
            "secondary_diagnosis_ICD11_Title": "common cold",
            "secondary_diagnosis_ICD11_Code": "ca00",
            "secondary_diagnosis_explanation": "Cold symptoms",
            "secondary_diagnosis_medicine_1": "paracetamol",
            "secondary_diagnosis_medicine_2": "paracetamol",
            "ai_confidence_score": 90
        })

    def __manager(self, models):
        return AIManager(
            PromptBuilder("System context", {"type": "object"}),
            ReplyParser(),
            OutputValidator(self.ICD_DF, self.HSA_DF),
            ModelFallback(models, ErrorClassifier(), 60, 2, sleep=lambda _: None)
        )

    def test_falls_back_to_next_provider(self):

        claude = FakeAIProvider([RuntimeError("401 invalid API key")], Action.SWITCH_PROVIDER)
        gemini = FakeAIProvider([self.__reply()])
        manager = self.__manager([
            AIModel(claude, "claude-opus"),
            AIModel(claude, "claude-sonnet"),
            AIModel(gemini, "gemini-flash")
        ])

        result = manager.get_ai_output(self.ANSWERS)

        print("\nSCENARIO: Claude Key Invalid, Gemini Replies")
        print("Expected: claude-sonnet skipped, Gemini's checked output returned")
        print("Actual:", claude.models_sent, gemini.models_sent, result)

        assert claude.models_sent == ["claude-opus"]
        assert gemini.models_sent == ["gemini-flash"]
        assert result["primary_diagnosis_ICD11_Title"] == "COMMON COLD"
        assert result["primary_diagnosis_medicine_1"] == "PARACETAMOL"
        assert "- gender: F" in gemini.requests[0].prompt

    def test_every_model_fails(self):

        claude = FakeAIProvider([RuntimeError("401 invalid API key")], Action.SWITCH_PROVIDER)
        gemini = FakeAIProvider([EmptyReplyError("Reply blocked by a safety filter")])
        manager = self.__manager([AIModel(claude, "claude-opus"), AIModel(gemini, "gemini-flash")])

        result = manager.get_ai_output(self.ANSWERS)

        print("\nSCENARIO: Every Model Fails")
        print("Expected:", {"error": CONTACT_SUPPORT_MESSAGE})
        print("Actual:", result)

        assert result == {"error": CONTACT_SUPPORT_MESSAGE}
