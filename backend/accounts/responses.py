from rest_framework import status
from rest_framework.views import Response


class SuccessResponse(Response):
    def __init__(self, data=None, status=status.HTTP_200_OK):
        response_data = {
            "status": status,
            "data": data
        }
        super().__init__(response_data, status=status)

class ErrorResponse(Response):
    def __init__(self, error, status=status.HTTP_400_BAD_REQUEST):
        response_data = {
            "status": status,
            "error": error
        }
        super().__init__(response_data, status=status)