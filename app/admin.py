from django.contrib import admin
from .models import Vote, Args, Profile, Comment

# Register your models here.

admin.site.register(Vote)
admin.site.register(Args)
admin.site.register(Profile)
admin.site.register(Comment)
