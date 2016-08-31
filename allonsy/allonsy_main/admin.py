from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from mptt.admin import MPTTModelAdmin

from allonsy_main.models import UserExtension, Organization, Location, Epoch, RelationOrganizationUser, TreeOrganization, TreeLocation, UserProfile, UserAlert, UserInteractionTree, RelationUserConnection, WorkflowSet, RelationWorkflow, WorkflowItem, WorkflowTree, WFMetaData
from allonsy_schemas.models import Account


# Register your models here.
class UserExtensionInline(admin.StackedInline):
    model = UserExtension
    can_delete = False
    verbose_name_plural = 'Additional fields'


class WFMetaInline (admin.TabularInline):
    model = WFMetaData


class UserAdmin(BaseUserAdmin):
    inlines = (UserExtensionInline, )


class WorkflowTreeAdmin(admin.ModelAdmin):
    inlines = [WFMetaInline, ]

admin.site.unregister(User)
admin.site.register(TreeOrganization, MPTTModelAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(UserAlert)
admin.site.register(UserInteractionTree)
admin.site.register(Account)
admin.site.register(Organization)
admin.site.register(Location)
admin.site.register(Epoch)
admin.site.register(TreeLocation)
admin.site.register(RelationOrganizationUser)
admin.site.register(RelationUserConnection)
admin.site.register(WorkflowSet)
admin.site.register(RelationWorkflow)
admin.site.register(WorkflowItem)
admin.site.register(WorkflowTree)


