from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class WorkRegistrationType(models.Model):
    name = models.CharField(_("Name"), max_length=100)

    class Meta:
        verbose_name = _("Work Registration Type")
        verbose_name_plural = _("Work Registration Types")

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(_("Name"), max_length=255)

    client = models.ForeignKey(
        'clients.Client',
        verbose_name=_("Client"),
        on_delete=models.PROTECT,
        related_name='projects'
    )

    # 👤 Contatos do cliente responsáveis pelo projeto
    contacts = models.ManyToManyField(
        'clients.ClientContact',
        verbose_name=_("Contacts"),
        related_name='projects',
        blank=True
    )

    address = models.TextField(_("Address"))

    # 👥 Responsáveis
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Managers"),
        related_name='managed_projects',
        blank=True
    )

    # 📅 Datas
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"), blank=True, null=True)

    # 📝 Informações
    notes = models.TextField(_("Notes"), blank=True, null=True)

    # 🔐 Registro obrigatório
    has_work_registration = models.BooleanField(
        _("Has work registration"),
        default=False
    )

    # 🔗 Tipo de registro
    work_registration_type = models.ForeignKey(
        'projects.WorkRegistrationType',
        verbose_name=_("Registration type"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    # 🔢 Número do registro
    work_registration_number = models.CharField(
        _("Registration number"),
        max_length=100,
        blank=True,
        null=True
    )

    # 🔄 Status
    is_active = models.BooleanField(_("Is active"), default=True)

    # 🔐 Auditoria
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Created by"),
        on_delete=models.PROTECT,
        related_name='projects_created'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Updated by"),
        on_delete=models.PROTECT,
        related_name='projects_updated',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']

    def __str__(self):
        return self.name