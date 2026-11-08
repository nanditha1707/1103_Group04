from typing import override

import phonenumbers

from io_manager import messages
from io_manager.validators.validator import Validator


class PhoneNumberValidator(Validator):
    """Checks a phone number with Google's libphonenumber. Numbers
    without a country code are read as the default region.
    
    Form libphonenumber, .parse() is to first parse the user input, and
    .is_valid_number() checks whether the parsed number is a theoretically
    valid phone number based on the country code entered."""

    DEFAULT_REGION = "SG"

    @override
    def validate(self, answer: str) -> str | None:
        # Parsing ignores spaces, so "+65 88880000" and "+6588880000"
        # are both accepted. A parse failure means the format is wrong.
        try:
            parsed_number = phonenumbers.parse(answer, self.DEFAULT_REGION)
        except phonenumbers.NumberParseException:
            return messages.PHONE_FORMAT_ERROR

        if phonenumbers.is_valid_number(parsed_number):
            return None
        return messages.PHONE_INVALID_ERROR