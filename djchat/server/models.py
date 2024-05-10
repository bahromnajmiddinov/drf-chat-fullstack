from django.db import models

from accounts.models import Account
from .validators import validate_icon_image_size, validate_image_file_extension


def channel_banner_upload_path(instance, filename):
    return f'channel/{instance.id}/channel_banner/{filename}'


def channel_icon_upload_path(instance, filename):
    return f'channel/{instance.id}/channel_icon/{filename}'


def category_icon_upload_path(instance, filename):
    return f'category/{instance.id}/category_icon/{filename}'


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.FileField(upload_to=category_icon_upload_path, null=True, blank=True)

    def __str__(self):
        return self.name


class Server(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,
                              related_name='server_owner')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='server_category')
    description = models.CharField(max_length=250, blank=True, null=True)
    members = models.ManyToManyField(Account, related_name='server_members')

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE,
                              related_name='channel_owner')
    topic = models.CharField(max_length=100)
    server = models.ForeignKey(Server, on_delete=models.CASCADE,
                               related_name='channel_server')
    banner = models.ImageField(upload_to=channel_banner_upload_path, null=True, blank=True, 
                               validators=[validate_image_file_extension])
    icon = models.FileField(upload_to=channel_icon_upload_path, null=True, blank=True, 
                            validators=[validate_icon_image_size, validate_image_file_extension])

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
