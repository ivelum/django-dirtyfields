from django.db import models
from dirtyfields import DirtyFieldsWithRelationshipChecksMixin


class TestModel(DirtyFieldsWithRelationshipChecksMixin, models.Model):
    """A simple test model to test dirty fields mixin with"""
    boolean = models.BooleanField(default=True)
    characters = models.CharField(blank=True, max_length=80)
    created = models.DateTimeField(auto_now_add=True)


class TestModelWithForeignKey(DirtyFieldsWithRelationshipChecksMixin, models.Model):
    fkey = models.ForeignKey(TestModel, blank=True, null=True)


class TestModelWithOneToOneField(DirtyFieldsWithRelationshipChecksMixin, models.Model):
    o2o = models.OneToOneField(TestModel)
