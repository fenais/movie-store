from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from cart.models import Order, Item

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie).order_by('-date')
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, id=id)
        review = Review.objects.filter(user=request.user, movie=movie).first()
        if review is None:
            review = Review()
            review.user = request.user
            review.movie = movie
        review.rating = request.POST['rating']
        review.comment = request.POST.get('comment', '')
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST.get('comment', '')
        review.rating = request.POST['rating']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def local_popularity_map(request):
    states = [
        "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA",
        "ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
        "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"
    ]

    template_data = {
        "title": "Local Popularity Map",
        "states": states,
    }
    return render(request, "movies/local_popularity_map.html", {"template_data": template_data})

@login_required
def local_popularity_data(request):
    state = request.GET.get("state", "GA").upper()

    qs = (
        Item.objects
        .filter(order__state=state)
        .values("movie__id", "movie__name")
        .annotate(total_purchased=Sum("quantity"))
        .order_by("-total_purchased")
    )

    top = list(qs[:5])

    return JsonResponse({
        "state": state,
        "top": top
    })