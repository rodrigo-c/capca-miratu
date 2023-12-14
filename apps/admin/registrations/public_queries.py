from django.conf import settings
from django.contrib import admin
from django.contrib.gis import forms
from django.contrib.gis.db import models
from django.contrib.gis.forms import OSMWidget
from django.urls import reverse
from django.utils.html import format_html

from nested_inline.admin import (
    NestedModelAdmin,
    NestedStackedInline,
    NestedTabularInline,
)

from apps.public_queries.models import (
    Answer,
    PublicQuery,
    Question,
    QuestionOption,
    Response,
)


class NestedModelAdmin(NestedModelAdmin):
    class Media:
        js = ("admin/js/inlines-nested%s.js" % ("" if settings.DEBUG else ".min"),)
        extend = False


class QuestionOptionInLine(NestedTabularInline):
    model = QuestionOption
    extra = 0


class QuestionInLine(NestedStackedInline):
    model = Question
    extra = 0
    ordering = ["order"]
    inlines = [QuestionOptionInLine]
    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 2})},
        models.CharField: {"widget": forms.Textarea(attrs={"rows": 2})},
    }


class PublicQueryAdmin(NestedModelAdmin):
    list_display = [
        "name",
        "view_url_code",
        "view_result",
        "kind",
        "start_at",
        "end_at",
        "active",
        "id",
        "created_by",
    ]
    search_fields = ["name"]
    ordering = ["created_at"]
    fieldsets = [
        (
            "System",
            {"fields": ["id", "created_at", "updated_at", "created_by", "url_code"]},
        ),
        ("Basic", {"fields": ["kind", "name", "description"]}),
        ("Activation", {"fields": ["active", "start_at", "end_at"]}),
        ("Visualization", {"fields": ["image"]}),
    ]
    inlines = [QuestionInLine]
    readonly_fields = ["id", "created_at", "created_by", "updated_at"]

    def view_url_code(self, obj):
        url = reverse("public_queries:submit", kwargs={"uuid": obj.url_code})
        return format_html(f"<a href='{url}'>{obj.url_code}</a>")

    def view_result(self, obj):
        url = reverse("public_queries:query-result", kwargs={"uuid": obj.url_code})
        return format_html(f"<a href='{url}' target='_blank'>Resultado</a>")

    def response_post_save_add(self, request, obj):
        obj.created_by_id = request.user.id
        obj.save()
        return self._response_post_save(request, obj)


class AnswerInLine(admin.StackedInline):
    model = Answer
    extra = 0
    fk_name = "response"
    ordering = ["question__order"]
    formfield_overrides = {models.PointField: {"widget": OSMWidget}}
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "question",
        "text",
        "image",
        "options",
        "point",
    ]

    def has_add_permission(self, request, obj=None):
        return False


class ResponseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "query_code",
        "edit_query",
        "send_at",
        "location",
        "email",
        "rut",
    ]
    inlines = [AnswerInLine]
    formfield_overrides = {models.PointField: {"widget": OSMWidget}}
    ordering = ["query_id", "-send_at"]
    fieldsets = [
        ("System", {"fields": ["id", "created_at", "updated_at"]}),
        ("Data", {"fields": ["send_at", "email", "rut", "location"]}),
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "send_at",
        "email",
        "rut",
        "location",
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def query_code(self, obj):
        url_code = obj.query.url_code
        url = reverse("public_queries:submit", kwargs={"uuid": url_code})
        return format_html(f"<a href='{url}'>{url_code}</a>")

    def edit_query(self, obj):
        url = f"/admin/public_queries/publicquery/{obj.query_id}"
        return format_html(f"<a href='{url}'>{obj.query_id}</a>")


public_queries_tuple_models = [
    (PublicQuery, PublicQueryAdmin),
    (Response, ResponseAdmin),
]
