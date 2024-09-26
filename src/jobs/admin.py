from django.contrib import admin
from .models import *

admin.site.register(Job)
admin.site.register(Category)
admin.site.register(JobResponse)


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'subcategory')
