from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, Sum, Max
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce

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
    return TemplateResponse(request, "admin/movie_stats.html", context)

def user_stats_view(request):
    top_buyer = User.objects.annotate(total_movies=Coalesce(Sum('order__item__quantity'), 0)).order_by('-total_movies').first()
    context = dict(
        admin.site.each_context(request),
        title="Top Customer",
        top_buyer= top_buyer,
    )
    return TemplateResponse(request, "admin/user_stats.html", context)

def most_commented_user_view(request):
    counts = Review.objects.values('user__username').annotate(total=Count('id'))
    max_total = counts.aggregate(max_total=Max('total'))['max_total']
    top_users = []
    if max_total is not None:
        top_users = counts.filter(total=max_total).order_by('user__username')
    context = dict(
        admin.site.each_context(request),
        top_users = top_users,
        max_total = max_total,
    )
    return TemplateResponse(request, 'admin/most_commented_user.html', context)

original_get_urls = admin.site.get_urls
def get_urls():
    urls = original_get_urls() #the fix
    custom_urls =[
        path("movie-stats/", admin.site.admin_view(movie_stats_view), name="movie-stats"),
        path("user-stats/", admin.site.admin_view(user_stats_view), name="user-stats"),
        path("most-commented-user/", admin.site.admin_view(most_commented_user_view), name="most-commented-user"),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls