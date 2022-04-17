from django.contrib import admin
from main.models import SlackInstalledWorkspace

# Register your models here.


class SlackInstalledWorkspaceAdmin(admin.ModelAdmin):
    readonly_fields = ('workspace_url',)
    list_display = ('workspace_name', 'admin_user_name', 'admin_user_email')


admin.site.register(SlackInstalledWorkspace, SlackInstalledWorkspaceAdmin)