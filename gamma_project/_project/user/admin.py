from django.contrib import admin

from .models import Sale, Payment

admin.site.register(Sale)
admin.site.register(Payment)