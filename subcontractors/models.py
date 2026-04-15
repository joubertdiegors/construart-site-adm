from django.db import models
from django.utils.translation import gettext_lazy as _


class Subcontractor(models.Model):

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('blocked', _('Blocked')),
    ]

    name = models.CharField(_("Name"), max_length=255, db_index=True)

    vat_number = models.CharField(
        _("VAT Number"),
        max_length=50,
        blank=True,
        null=False
    )

    contact_name = models.CharField(
        _("Contact Name"),
        max_length=255,
        blank=True,
        null=True
    )

    phone = models.CharField(
        _("Phone"),
        max_length=30,
        blank=True,
        null=True
    )

    email = models.EmailField(
        _("Email"),
        blank=True,
        null=True
    )

    address = models.TextField(
        _("Address"),
        blank=True,
        null=True
    )

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    notes = models.TextField(
        _("Notes"),
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Subcontractor")
        verbose_name_plural = _("Subcontractors")
        ordering = ['name']

        constraints = [
            models.UniqueConstraint(
                fields=['vat_number'],
                name='unique_vat_number',
                condition=~models.Q(vat_number="")
            )
        ]
    

    def __str__(self):
        return self.name