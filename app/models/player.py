from neomodel import (
    StructuredNode,
    StringProperty,
    EmailProperty,
    DateProperty,
    RelationshipTo,
    UniqueIdProperty
)
from django.contrib.auth.hashers import make_password, check_password

class Player(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = EmailProperty(unique_index=True, required=True)
    password_hash = StringProperty(required=True)
    first_name = StringProperty()
    last_name = StringProperty()
    date_of_birth = DateProperty()
    registration_date = DateProperty(default_now=True)

    # Add relationships as needed
    # teams = RelationshipTo('Team', 'PLAYS_FOR')

    @classmethod
    def create(cls, username, email, password, **kwargs):
        """Create a new player with hashed password"""
        password_hash = make_password(password)
        return cls(username=username, email=email, password_hash=password_hash, **kwargs).save()

    def verify_password(self, password):
        """Verify the provided password against stored hash"""
        return check_password(password, self.password_hash)
