from django.db import models
from django.contrib.auth.models import User
from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty

class UserProfile(models.Model):
    """Django model for user profile, linked to Neo4j Player node"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    neo4j_player_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
