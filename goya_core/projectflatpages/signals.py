from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.flatpages.models import FlatPage
from communicator.views import generic_notify_workspace_admins


@receiver(post_save, sender=FlatPage)
def notify_admins(sender, instance, created, **kwargs):
    if instance.url == '/privacy/':
        message = 'The BeyondMachines Privacy Policy has been updated.\n Please read the Privacy Policy at https://beyondmachines.net/privacy/'
        generic_notify_workspace_admins(message)
    if instance.url == '/terms/':
        message = 'The BeyondMachines Terms of Service has been updated.\n Please read the Terms of Service at https://beyondmachines.net/terms/'
        generic_notify_workspace_admins(message)

    # def create_post(sender, instance, created, **kwargs):
    # content_type = ContentType.objects.get_for_model(instance)
    # try:
    #     post = Post.objects.get(content_type=content_type,
    #                             object_id=instance.id)
    # except Post.DoesNotExist:
    #     post = Post(content_type=content_type, object_id=instance.id)
    # post.save()