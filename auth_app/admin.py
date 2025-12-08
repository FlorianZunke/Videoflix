from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

User = get_user_model()

# @admin.register(User)
# class CustomUserAdmin(DefaultUserAdmin):
# 	"""Use the default UserAdmin but make sure the model is registered.

# 	You can customise list_display, search_fields etc. here if needed.
# 	"""
# 	list_display = ("email", "is_staff", "is_active")
# 	search_fields = ("email")