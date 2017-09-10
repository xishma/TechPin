from django.http import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import exception_handler


class ApiResponse:
    @staticmethod
    def get_base_response(response_code=HTTP_200_OK, data=None, message=""):
        if data is None:
            data = {}

        if message:
            data['message'] = message
        response = {
            "status": response_code,
            "errors": {
                "general_errors": [
                ],
                "form_errors": {
                }
            },
            "data": data
        }

        return response

    @staticmethod
    def get_fail_response(response_code=HTTP_400_BAD_REQUEST, general_errors=None, form_errors=None):
        if form_errors is None:
            form_errors = {}
        if general_errors is None:
            general_errors = []
        response = ApiResponse.get_base_response(response_code)
        if not isinstance(general_errors, list):
            general_errors = [general_errors]
        response['errors']['general_errors'] = general_errors
        response['errors']['form_errors'] = form_errors

        return response

    @staticmethod
    def inspect_response_structure(data):
        if not isinstance(data, dict):
            return False
        for key in ['errors', 'data', 'status']:
            if key not in data:
                return False
        return True


ERROR_CODES = [400, 401, 402, 403, 404, 405, 415]
GENERAL_ERRORS = ['detail', 'non_field_errors']


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data

        if response.status_code in ERROR_CODES:
            if not ApiResponse.inspect_response_structure(data):
                error_data = response.data
                general_errors = []
                for general_error in GENERAL_ERRORS:
                    if general_error in error_data:
                        errors = error_data.pop(general_error)
                        if type(errors) not in [list, tuple]:
                            errors = [errors]
                        for error in errors:
                            general_errors.append(error)
                data = ApiResponse.get_fail_response(general_errors=general_errors, form_errors=error_data)

        data['status'] = response.status_code

        response.data = data

    return response


def handler404(request):
    return JsonResponse(ApiResponse.get_fail_response(HTTP_404_NOT_FOUND))


def handler500(request):
    return JsonResponse(ApiResponse.get_fail_response(HTTP_500_INTERNAL_SERVER_ERROR))
