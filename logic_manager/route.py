from enum import Enum

class Route(Enum):
    """
    Where a patient can be sent after triage.
    """

    EMERGENCY = "EMERGENCY"
    DOCTOR = "Doctor"
    PHARMACIST = "Pharmacist"
    RETAIL = "Retail"
