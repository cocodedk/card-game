from django.contrib.auth.models import User
from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, UniqueIdProperty
from django.contrib.auth.hashers import make_password, check_password

class UserProfile(StructuredNode):
    """Neo4j model for user profile, linked to Django User"""
    uid = UniqueIdProperty()
    user_id = IntegerProperty(unique_index=True)
    username = StringProperty(unique_index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(default="")
    last_name = StringProperty(default="")
    password = StringProperty()  # Will store hashed password
    created_at = DateTimeProperty(default_now=True)

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.username}'s profile"
