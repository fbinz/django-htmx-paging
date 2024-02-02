from urllib.parse import urlparse, urlunparse, urlencode
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.contrib import admin
from django.urls import path
from faker import Faker
from django.core.paginator import Paginator

fake = Faker()


all_contacts = [{"name": fake.name(), "email": fake.email()} for _ in range(100)]

from urllib.parse import urlparse, urlunparse, urlencode
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.core.paginator import Paginator

class BoundPaginator(Paginator):
    """A paginator that can generate URLs for the current page and the next and previous pages.

    Unlike Django's built-in Paginator, this one can generate URLs by being passed a request and
    a base URL. It also allows you to specify which query parameters to preserve when generating
    URLs.
    """

    def __init__(
        self,
        *args,
        page_param: str,
        preserve: list[str],
        request: HttpRequest,
        base_url: str = "",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.base_url = base_url
        self.page_param = page_param
        self.preserve = preserve
        self.request = request

    def current_page(self):
        number = self.current_page_number()
        return self.page(number)

    def current_page_number(self) -> int:
        number = self.request.GET.get(self.page_param) or 1
        return int(number)

    def next_page_url(self):
        page = self.current_page()
        if page.has_next():
            return self.page_url_for_number(page.next_page_number())

    def previous_page_url(self):
        page = self.current_page()
        if page.has_previous():
            return self.page_url_for_number(page.previous_page_number())

    def page_url_for_number(self, number):
        result = urlparse(self.request.get_full_path())

        query_dict = {}
        for param in self.preserve:
            if value := self.request.GET.get(param):
                query_dict[param] = value

        if number != 1:
            query_dict[self.page_param] = number

        result = result._replace(
            path=self.base_url,
            query=urlencode(query_dict, doseq=True),
        )

        return urlunparse(result)


def contacts_naive(request):
    contacts = all_contacts
    if q := request.GET.get("q"):
        contacts = [c for c in all_contacts if q in c["name"]]

    paginator = Paginator(
        object_list=contacts,
        per_page=10,
    )
    page = paginator.get_page(request.GET.get("page"))
    context = {"contacts": page}
    return TemplateResponse(request, "contacts_naive.html", context)


def contacts_form(request):
    contacts = all_contacts
    if q := request.GET.get("q"):
        contacts = [c for c in all_contacts if q in c["name"]]

    paginator = Paginator(
        object_list=contacts,
        per_page=10,
    )
    page = paginator.current_page()
    context = {"contacts": page}
    return TemplateResponse(request, "contacts_form.html", context)


def contacts_link(request):
    contacts = all_contacts
    if q := request.GET.get("q"):
        contacts = [c for c in all_contacts if q in c["name"]]

    paginator = Paginator(
        object_list=contacts,
        per_page=10,
    )
    page = paginator.current_page()
    context = {"contacts": page}
    return TemplateResponse(request, "contacts_link.html", context)


def contacts_custom_paginator(request):
    contacts = all_contacts
    if q := request.GET.get("q"):
        contacts = [c for c in all_contacts if q in c["name"]]

    paginator = BoundPaginator(
        object_list=contacts,
        per_page=10,
        request=request,
        base_url="/contacts/",
        page_param="page",
        preserve=["q"],
    )
    page = paginator.current_page()
    context = {"contacts": page}
    return TemplateResponse(request, "contacts_custom_paginator.html", context)


urlpatterns = [
    path("contacts-naive/", contacts_naive),
    path("contacts-link/", contacts_link),
    path("contacts-form/", contacts_form),
    path("contacts-custom-paginator/", contacts_custom_paginator),
    path("admin/", admin.site.urls),
]
