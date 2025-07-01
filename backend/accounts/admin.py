from django.contrib import admin

# Register your models here.
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'id')


admin.site.register(Profile, ProfileAdmin)