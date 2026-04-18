from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class AccessProfile(models.Model):
    """
    Extends Django's built-in Group with display metadata.
    One-to-one with auth.Group — the Group holds the actual permissions,
    this model holds the label, description and colour for the UI.
    """
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name='access_profile',
        verbose_name=_("Grupo"),
    )
    description = models.TextField(_("Descrição"), blank=True)
    color = models.CharField(
        _("Cor"),
        max_length=20,
        default='gray',
        choices=[
            ('accent', _('Laranja')),
            ('green',  _('Verde')),
            ('amber',  _('Amarelo')),
            ('red',    _('Vermelho')),
            ('gray',   _('Cinzento')),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Perfil de Acesso")
        verbose_name_plural = _("Perfis de Acesso")
        ordering = ['group__name']

    def __str__(self):
        return self.group.name

    def get_badge_class(self):
        return {
            'accent': 'badge-accent',
            'green':  'badge-green',
            'amber':  'badge-amber',
            'red':    'badge-red',
            'gray':   'badge-gray',
        }.get(self.color, 'badge-gray')

    @property
    def user_count(self):
        return self.group.profile_users.filter(is_active=True).count()


class User(AbstractUser):
    phone = models.CharField(_("Telefone"), max_length=20, blank=True)

    # Primary access profile — drives group membership and permissions
    access_profile = models.ForeignKey(
        Group,
        verbose_name=_("Perfil de acesso"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profile_users',
    )

    class Meta:
        verbose_name = _("Utilizador")
        verbose_name_plural = _("Utilizadores")
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep Django group membership in sync with access_profile
        if self.access_profile_id:
            self.groups.set([self.access_profile_id])
        else:
            self.groups.clear()

    @property
    def is_manager(self):
        """Backward-compatible — true when user can manage projects."""
        return self.is_superuser or self.has_perm('projects.change_project')

    def get_profile_badge_class(self):
        try:
            return self.access_profile.access_profile.get_badge_class()
        except Exception:
            return 'badge-gray'

    def get_profile_name(self):
        try:
            return self.access_profile.name
        except Exception:
            return '—'