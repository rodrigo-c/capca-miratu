from django.http import Http404, HttpResponse

from apps.public_queries.lib.exceptions import ObjectDoesNotExist


class UUIDObjectURL:
    url_active_status = None
    url_service = None
    url_service_field = "identifier"
    url_service_extra_kwargs = None

    def dispatch(self, request, uuid, *args, **kwargs) -> HttpResponse:
        extra_kwargs = self.get_url_service_extra_kwargs()
        try:
            object_data = self.__class__.url_service(
                **{self.url_service_field: uuid, **extra_kwargs}
            )
        except ObjectDoesNotExist:
            raise Http404
        self.object = object_data
        return super().dispatch(request, uuid, *args, **kwargs)

    def get_url_service_extra_kwargs(self):
        return self.url_service_extra_kwargs or {}

    def _get_page_num(self) -> int:
        if "page_num" in self.request.GET and self.request.GET["page_num"].isdecimal():
            return int(self.request.GET["page_num"])
        return 1
