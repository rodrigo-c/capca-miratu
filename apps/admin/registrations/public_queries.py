from django.contrib.admin import ModelAdmin, StackedInline

from apps.public_queries.models import Answer, PublicQuery, Question, Response


class QuestionInLine(StackedInline):
    model = Question
    extra = 0


class PublicQueryAdmin(ModelAdmin):
    list_display = ["name", "id", "kind", "start_at", "end_at", "active", "created_by"]
    search_fields = ["name"]
    ordering = ["created_at"]
    fieldsets = [
        ("Basic", {"fields": ["kind", "name", "description", "created_by"]}),
        ("Activation", {"fields": ["active", "start_at", "end_at"]}),
        ("Visualization", {"fields": ["image"]}),
    ]
    inlines = [QuestionInLine]


class AnswerInLine(StackedInline):
    model = Answer
    fk_name = "response"
    ordering = ["query", "order"]


class ResponseAdmin(ModelAdmin):
    inlines = [AnswerInLine]


public_queries_tuple_models = [
    (PublicQuery, PublicQueryAdmin),
    (Response, ResponseAdmin),
]
