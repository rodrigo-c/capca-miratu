from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.public_queries.models import Answer, PublicQuery, Question, Response


class QuestionInLine(admin.StackedInline):
    model = Question
    extra = 0
    ordering = ["order"]


class PublicQueryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "view_url_code",
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
        ("Basic", {"fields": ["kind", "name", "description", "created_by"]}),
        ("Activation", {"fields": ["active", "start_at", "end_at"]}),
        ("Visualization", {"fields": ["url_code", "image"]}),
    ]
    inlines = [QuestionInLine]
    readonly_fields = ["id", "created_by", "updated_at"]

    @admin.display()
    def view_url_code(self, obj):
        url = reverse("public_queries:submit", kwargs={"uuid": obj.url_code})
        return format_html(f"<a href='{url}'>{obj.url_code}</a>")


class AnswerInLine(admin.StackedInline):
    model = Answer
    extra = 0
    fk_name = "response"
    ordering = ["question__order"]


class ResponseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "query_id",
        "send_at",
        "location",
        "email",
        "rut",
    ]
    inlines = [AnswerInLine]


public_queries_tuple_models = [
    (PublicQuery, PublicQueryAdmin),
    (Response, ResponseAdmin),
]
