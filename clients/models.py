from django.db import models


class Client(models.Model):

    CATEGORY_CHOICES = [
        ('private', 'Privé'),
        ('professional', 'Professionnel'),
    ]

    LEGAL_FORM_CHOICES = [
        ('mr', 'Monsieur'),
        ('mrs', 'Madame'),
        ('company', 'Entreprise'),
    ]

    # Cadastro base
    name = models.CharField(max_length=255, verbose_name="Raison sociale")
    trade_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom commercial")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True)
    legal_form = models.CharField(max_length=20, choices=LEGAL_FORM_CHOICES, null=True, blank=True)

    vat_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="TVA")
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taxe TVA (%)")

    responsible = models.CharField(max_length=255, blank=True, null=True, verbose_name="Responsable")

    notes = models.TextField(blank=True, null=True, verbose_name="Informations")

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClientAddress(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='addresses')

    label = models.CharField(max_length=100, blank=True, null=True)

    street = models.CharField(max_length=255)
    number = models.CharField(max_length=50, blank=True, null=True)
    complement = models.CharField(max_length=255, blank=True, null=True)

    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Belgium")

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.name} - {self.city}"


class ClientContact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('general', 'Général'),
        ('financial', 'Finance'),
        ('commercial', 'Commercial'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')

    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, default='general')

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client.name} - {self.name}"

