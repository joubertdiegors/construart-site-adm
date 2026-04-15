from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


# 🏦 CAISSE D'ASSURANCE
class InsuranceFund(models.Model):

    name = models.CharField(_("Name"), max_length=255)

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

    notes = models.TextField(
        _("Notes"),
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Insurance Fund")
        verbose_name_plural = _("Insurance Funds")
        ordering = ['name']

    def __str__(self):
        return self.name


# 👥 CONTATOS DA CAISSE
class InsuranceFundContact(models.Model):

    fund = models.ForeignKey(
        InsuranceFund,
        on_delete=models.CASCADE,
        related_name='contacts'
    )

    name = models.CharField(_("Name"), max_length=255)

    role = models.CharField(
        _("Role"),
        max_length=100,
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

    notes = models.TextField(
        _("Notes"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Insurance Fund Contact")
        verbose_name_plural = _("Insurance Fund Contacts")

    def __str__(self):
        return f"{self.name} ({self.fund.name})"


# 👷 COLABORADOR
class Collaborator(models.Model):

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]

    company = models.ForeignKey(
        'subcontractors.Subcontractor',
        verbose_name=_("Company"),
        on_delete=models.PROTECT,
        related_name='collaborators'
    )

    insurance_fund = models.ForeignKey(
        InsuranceFund,
        verbose_name=_("Insurance Fund"),
        on_delete=models.PROTECT,
        related_name='collaborators',
        db_index=True,
        blank=True,
        null=True
    )

    name = models.CharField(
        _("Name"),
        max_length=255,
        db_index=True
    )

    role = models.CharField(
        _("Role"),
        max_length=100,
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

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )

    notes = models.TextField(
        _("Notes"),
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Collaborator")
        verbose_name_plural = _("Collaborators")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    # 🔥 pegar valor atual
    def get_current_hourly_rate(self):
        return self.hourly_rates.filter(end_date__isnull=True).first()

    # 🔥 definir novo valor (uso obrigatório)
    def set_new_hourly_rate(self, hourly_rate, start_date):

        current = self.hourly_rates.filter(end_date__isnull=True).first()

        if current:
            current.end_date = start_date
            current.save()

        CollaboratorHourlyRate.objects.create(
            collaborator=self,
            hourly_rate=hourly_rate,
            start_date=start_date
        )


# 💰 HISTÓRICO DE VALOR DA HORA
class CollaboratorHourlyRate(models.Model):

    collaborator = models.ForeignKey(
        Collaborator,
        on_delete=models.CASCADE,
        related_name='hourly_rates'
    )

    hourly_rate = models.DecimalField(
        _("Hourly Rate"),
        max_digits=10,
        decimal_places=2
    )

    start_date = models.DateField(_("Start Date"))

    end_date = models.DateField(
        _("End Date"),
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Hourly Rate")
        verbose_name_plural = _("Hourly Rates")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.collaborator.name} - {self.hourly_rate} ({self.start_date})"

    def clean(self):

        overlapping = CollaboratorHourlyRate.objects.filter(
            collaborator=self.collaborator
        ).exclude(pk=self.pk)

        for rate in overlapping:

            # se algum dos dois for aberto (ativo)
            if not self.end_date or not rate.end_date:
                raise ValidationError(_("There is already an active hourly rate."))

            # valida sobreposição de datas
            if self.start_date <= rate.end_date and (
                self.end_date is None or self.end_date >= rate.start_date
            ):
                raise ValidationError(_("Overlapping hourly rate periods are not allowed."))