from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from .models import AuditLog
from .utils import serialize_dict
from audit.middleware import get_current_user


# Apps que NÃO devem ser auditados
EXCLUDED_APPS = ['audit', 'admin']


def should_skip(sender):
    """
    Define se o modelo deve ser ignorado na auditoria
    """
    if sender._meta.app_label in ['audit', 'admin']:
        return True

    if sender.__name__ in ['LogEntry', 'AuditLog']:
        return True

    return False


@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    if should_skip(sender):
        return

    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_data = serialize_dict(model_to_dict(old_instance))
    new_data = serialize_dict(model_to_dict(instance))

    changes = {}

    for field in old_data:
        if old_data[field] != new_data[field]:
            changes[field] = {
                "old": old_data[field],
                "new": new_data[field]
            }

    if changes:
        instance._audit_changes = changes


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    if should_skip(sender):
        return

    user = get_current_user()

    if created:
        AuditLog.objects.create(
            user=user,
            action='create',
            model_name=sender.__name__,
            object_id=str(instance.pk),
            changes=serialize_dict(model_to_dict(instance))
        )
    else:
        changes = getattr(instance, '_audit_changes', None)

        if changes:
            AuditLog.objects.create(
                user=user,
                action='update',
                model_name=sender.__name__,
                object_id=str(instance.pk),
                changes=changes
            )


@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    if should_skip(sender):
        return

    user = get_current_user()

    AuditLog.objects.create(
        user=user,
        action='delete',
        model_name=sender.__name__,
        object_id=str(instance.pk),
        changes=serialize_dict(model_to_dict(instance))
    )