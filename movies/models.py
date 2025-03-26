from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.JSONField()
    movie_id = models.IntegerField(unique=True)
    video_file = models.FileField(upload_to='movies/videos/', null=True, blank=True)


    def __str__(self):
        return self.title