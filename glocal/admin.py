from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Información Personal', {'fields': ('nombre', 'apellido')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Personal', {'fields': ('nombre', 'apellido')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)