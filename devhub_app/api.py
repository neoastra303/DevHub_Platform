from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def devhub_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {
                "ok": False,
                "error": {
                    "code": "server_error",
                    "message": "An unexpected error occurred.",
                    "details": {},
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data
    message = "Request failed."
    if isinstance(detail, dict):
        if "detail" in detail and isinstance(detail["detail"], str):
            message = detail["detail"]
        elif "non_field_errors" in detail and detail["non_field_errors"]:
            message = detail["non_field_errors"][0]
    elif isinstance(detail, list) and detail:
        message = str(detail[0])
        detail = {"non_field_errors": detail}
    else:
        message = str(detail)
        detail = {"detail": detail}

    response.data = {
        "ok": False,
        "error": {
            "code": f"http_{response.status_code}",
            "message": message,
            "details": detail,
        },
    }
    return response
