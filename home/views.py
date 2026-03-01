from django.shortcuts import render, redirect
from django.db.models import Count, Max
from movies.models import Review
def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {'template_data': template_data})
def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})
def most_commented_user(request):
    if not request.user.is_staff:
        return redirect('home.index')
    counts = Review.objects.values('user__username').annotate(total=Count('id'))
    max_total = counts.aggregate(max_total=Max('total'))['max_total']
    top_users = []
    if max_total is not None:
        top_users = counts.filter(total=max_total).order_by('user__username')
    return render(request, 'home/most_commented_user.html', {
        'max_total': max_total,
        'top_users': top_users,
    })