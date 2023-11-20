from django.contrib.admin import ModelAdmin

from apps.public_queries.models import PublicQuery, Question


class PublicQueryAdmin(ModelAdmin):
    list_display = ["name", "id", "kind", "start_at", "end_at", "active", "created_by"]
    search_fields = ["name"]
    ordering = ["created_at"]
    fieldsets = [
        ("Basic", {"fields": ["kind", "name", "description", "created_by"]}),
        ("Activation", {"fields": ["active", "start_at", "end_at"]}),
        ("Visualization", {"fields": ["image"]}),
    ]


class QuestionAdmin(ModelAdmin):
    list_display = [
        "name",
        "kind",
        "query",
        "order",
        "required",
        "max_answers",
        "text_max_length",
    ]
    ordering = ["query", "order"]


public_queries_tuple_models = [
    (PublicQuery, PublicQueryAdmin),
    (Question, QuestionAdmin),
]
