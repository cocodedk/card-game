from neomodel import StructuredNode, StringProperty, DateTimeProperty
from django.contrib.auth.hashers import make_password, check_password
import uuid
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

class UserProfile(StructuredNode):
    """Neo4j model for user profile, linked to Django User"""
    __module__ = 'backend.authentication.models'
    uid = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    username = StringProperty(unique_index=True)
    email = StringProperty(index=True)
    first_name = StringProperty(default="")
    last_name = StringProperty(default="")
    password = StringProperty()  # Will store hashed password
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)

    # Django authentication system compatibility properties
    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True

    @property
    def is_anonymous(self):
        """Always return False for authenticated users"""
        return False

    @property
    def is_active(self):
        """Return True to indicate this user is active"""
        return True

    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.username}'s profile"
