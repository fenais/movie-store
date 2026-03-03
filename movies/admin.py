from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, Sum

from .models import Movie, Review
from cart.models import Item


class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']


admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)


def movie_stats_view(request):
    most_reviewed = (
        Review.objects
        .values("movie__name")
        .annotate(times=Count("id"))
        .order_by("-times", "movie__name")
        .first()
    )

    most_bought = (
        Item.objects
        .values("movie__name")
        .annotate(times=Sum("quantity"))
        .order_by("-times", "movie__name")
        .first()
    )

    context = dict(
        admin.site.each_context(request),
        most_reviewed=most_reviewed,
        most_bought=most_bought,
    )
    return TemplateResponse(request, "movies/admin/movie_stats.html", context)

original_get_urls = admin.site.get_urls
def get_urls():
    urls = original_get_urls() #the fix
    custom_urls =[
        path("movie-stats/", admin.site.admin_view(movie_stats_view), name="movie-stats"),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls