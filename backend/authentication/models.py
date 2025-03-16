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


class BlacklistedToken(StructuredNode):
    """Neo4j model for storing blacklisted JWT tokens"""
    __module__ = 'backend.authentication.models'
    uid = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    token = StringProperty(unique_index=True)  # The actual token string
    user_uid = StringProperty(index=True)  # UID of the user who owned this token
    blacklisted_at = DateTimeProperty(default_now=True)
    expires_at = DateTimeProperty()  # When the token would have expired

    @classmethod
    def is_blacklisted(cls, token_string):
        """Check if a token is blacklisted"""
        try:
            cls.nodes.get(token=token_string)
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens from the blacklist"""
        now = datetime.now()
        # Find all expired tokens
        expired_tokens = cls.nodes.filter(expires_at__lt=now)
        # Delete them
        for token in expired_tokens:
            token.delete()
        return len(expired_tokens)
