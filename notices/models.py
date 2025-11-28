"""
Notice Board Models
=================

This module defines the data models for the SITDS Notice Board system.
It implements a sophisticated notice management system with role-based
access control and view tracking capabilities.
"""

from typing import List, Optional, Union
from django.db import models
from django.core.files.uploadedfile import UploadedFile
from users.models import CustomUser, Class
import os
from django.utils import timezone
from datetime import datetime

def notice_file_path(instance: 'Notice', filename: str) -> str:
    """
    Generate a unique file path for notice attachments.
    
    Args:
        instance: The Notice instance the file is being attached to
        filename: Original filename of the uploaded file
        
    Returns:
        str: Unique file path within the media directory
    """
    return f'uploads/notices/user_{instance.author.id}/{filename}'

class NoticeView(models.Model):
    notice = models.ForeignKey('Notice', on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['notice', 'viewer']  # Each user can only view once
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.notice.title} viewed by {self.viewer.username}"


class Comment(models.Model):
    """Comments left by users on a Notice.

    Only users who are allowed to see a notice should be able to comment on it.
    """
    notice = models.ForeignKey('Notice', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.notice.title}"

    @property
    def visible_children(self):
        return self.children.filter(is_hidden=False)

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # You can target a single class (legacy), or multiple classes via target_classes.
    target_class = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)
    target_classes = models.ManyToManyField(Class, related_name='notices', blank=True)
    # When True the notice is public to everyone. Otherwise it may be targeted to classes and/or roles.
    is_public = models.BooleanField(default=True)
    # Store a list of role keys (e.g. ['STUDENT','CLASS_COMMANDER']) to target specific roles.
    target_roles = models.JSONField(null=True, blank=True, default=list)
    attachment = models.FileField(upload_to=notice_file_path, null=True, blank=True)
    attachment_name = models.CharField(max_length=255, null=True, blank=True)  # Original filename
    
    @property
    def view_count(self):
        return self.views.count()

    @property
    def recent_viewers(self):
        return self.views.select_related('viewer').order_by('-viewed_at')[:5]

    def __str__(self):
        return f"{self.title} - by {self.author.username}"

    class Meta:
        ordering = ['-created_at']
