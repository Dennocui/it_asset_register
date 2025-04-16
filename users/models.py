from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    company = models.ForeignKey('companies.Company', on_delete=models.PROTECT, blank=True, null=True)
    department = models.ForeignKey('companies.Department', on_delete=models.SET_NULL, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_asset_manager = models.BooleanField(default=False)
    
    # Add related_name arguments to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",  # Changed from default
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",  # Changed from default
        related_query_name="user",
    )
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.company})"