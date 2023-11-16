from model_bakery.recipe import Recipe, foreign_key

from apps.public_queries.lib.constants import PublicQueryConstants, QuestionConstants

public_query_recipe = Recipe(
    "public_queries.PublicQuery",
    kind=PublicQueryConstants.KIND_OPEN,
)

question_recipe = Recipe(
    "public_queries.Question",
    kind=QuestionConstants.KIND_TEXT,
    query=foreign_key(public_query_recipe),
)
