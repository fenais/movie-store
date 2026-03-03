from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
    @property
    def average_rating(self):
        avg = self.review_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else 0
    @property
    def rating_count(self):
        return self.review_set.count()
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField(choices=[(1,'1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'movie'], name='unique_movie_review')]
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name