from django.contrib import admin

from .models import Channel, Server, Category


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    class Meta:
        verbose_name_plural = 'categories'


admin.site.register(Channel)
admin.site.register(Server)
