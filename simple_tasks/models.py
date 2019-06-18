from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Task(models.Model):
    NEW_STATUS = 'new'
    IN_PROGRESS_STATUS = 'inprogress'
    COMPLETED_STATUS = 'completed'
    ARCHIVED_STATUS = 'archived'
    STATUS_ACTIVE_CHOICES = (
        (NEW_STATUS, 'New'),
        (IN_PROGRESS_STATUS, 'In progress'),
        (COMPLETED_STATUS, 'Completed'),
    )
    STATUS_CLOSED_CHOICES = (
        (ARCHIVED_STATUS, 'Archived'),
    )
    STATUS_CHOICES = STATUS_ACTIVE_CHOICES + STATUS_CLOSED_CHOICES
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=NEW_STATUS)
    created = models.DateTimeField(editable=False, default=datetime.now, blank=True)
    modified = models.DateTimeField(editable=False, default=datetime.now, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})

    def can_be_updated(self):
        return self.status in [choice[0] for choice in self.STATUS_ACTIVE_CHOICES]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.modified = datetime.now()
        super(Task, self).save(force_insert, force_update, using, update_fields)

    def delete(self):
        self.status = self.ARCHIVED_STATUS
        self.save()
