from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Area(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    area = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()

class Post(models.Model):
    startup = "Start-Up"
    club = "Club"
    event = "Event"
    organization = (
        (startup, "Start-Up"),
        (club, "Club"),
        (event, "Event"),
    )
    environment = "Environment"
    stem = "STEM"
    readwrite = "Reading/Writing"
    musicart = "Music/Art"
    other = "Other"
    interest = (
        (environment, "Environment"),
        (stem, "STEM"),
        (readwrite, "Reading/Writing"),
        (musicart, "Music/Art"),
        (other, "Other"),
    )
    inperson = "In-Person"
    online = "Online"
    communication = (
        (inperson, "In-Person"),
        (online, "Online"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255, blank=True)
    name_of_organization = models.CharField(max_length=255, unique=True)
    organization = models.CharField(max_length=255, choices=organization, default=startup)
    interest = models.CharField(max_length=255, choices=interest, default=environment)
    website = models.URLField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    communication = models.CharField(max_length=255, choices=communication, default=online)
    description = models.TextField(null=True, blank=False)
    looking = models.TextField(null=True, blank=False)
    update = models.TextField(null=True, blank=False)
    recentevent = models.CharField(max_length=255, null=True, blank=False)
    saved = models.ManyToManyField(User, related_name='saved', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name_of_organization