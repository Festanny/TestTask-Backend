from . import constants


class UTMSaveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        new_utms = {}
        for q_name, q_value in request.GET.items():
            if q_name.lower().startswith("utm_"):
                new_utms[q_name] = q_value

        if new_utms:
            current_utms = request.session.get(constants.SessionKeys.UTM.value, {})
            current_utms.update(new_utms)

            request.session[constants.SessionKeys.UTM.value] = current_utms

        response = self.get_response(request)
        return response
