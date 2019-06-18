from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

class Task(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created = models.DateTimeField(editable=False, default=datetime.now, blank=True)
    modified = models.DateTimeField(editable=False, default=datetime.now, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    deleted = models.BooleanField(default=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.modified = datetime.now()
        super(Task, self).save(force_insert, force_update, using, update_fields)

    def delete(self):
        self.deleted = True
        self.save()