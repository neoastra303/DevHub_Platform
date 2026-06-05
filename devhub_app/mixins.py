from rest_framework.exceptions import ValidationError


class QueryValidationMixin:
    @staticmethod
    def validate_choice_param(param_name, value, allowed_values, message=None):
        if value and value not in allowed_values:
            raise ValidationError({param_name: [message or f"Unsupported {param_name} '{value}'."]})

