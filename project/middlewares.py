class StripMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return response


    def process_request(self, request):
        # request.GET = request.GET.copy()
        request.GET._mutable = True
        for k, v in request.GET.items():
            request.GET[k] = request.GET[k].strip()
        request.GET._mutable = False

        # request.POST = request.POST.copy()
        request.POST._mutable = True
        for k, v in request.POST.items():
            request.POST[k] = request.POST[k].strip()
        request.POST._mutable = False
