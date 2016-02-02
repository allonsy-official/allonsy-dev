from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from allonsy_main.models import UserExtension, Account, Organization, Location, Epoch, RelationOrganizationTree, \
    RelationOrganizationUser, RelationLocationTree, RelationLocationOrganization, RelationLocationUserTransact, \
    RelationUserLocationStatic


# Register your models here.
class UserExtensionInline(admin.StackedInline):
    model = UserExtension
    can_delete = False
    verbose_name_plural = 'Additional fields'


class UserAdmin(BaseUserAdmin):
    inlines = (UserExtensionInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Organization)
admin.site.register(Location)
admin.site.register(Epoch)
