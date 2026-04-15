from django.db import models


class Planning(models.Model):
    date = models.DateField()

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='plannings'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('date', 'project')
        ordering = ['-date']

    def __str__(self):
        return f"{self.project} - {self.date}"


class PlanningSubcontractor(models.Model):
    planning = models.ForeignKey(
        Planning,
        on_delete=models.CASCADE,
        related_name='planning_subcontractors'
    )

    subcontractor = models.ForeignKey(
        'subcontractors.Subcontractor',
        on_delete=models.CASCADE,
        related_name='planning_assignments'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('planning', 'subcontractor')
        ordering = ['planning']

    def __str__(self):
        return f"{self.subcontractor} - {self.planning}"


class PlanningWorker(models.Model):

    PERIOD_CHOICES = [
        ('full_day', 'Full Day'),
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('custom', 'Custom'),
    ]

    planning = models.ForeignKey(
        Planning,
        on_delete=models.CASCADE,
        related_name='planning_workers'
    )

    worker = models.ForeignKey(
        'workforce.collaborator',
        on_delete=models.CASCADE,
        related_name='planning_assignments'
    )

    subcontractor = models.ForeignKey(
        'subcontractors.Subcontractor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_plannings'
    )

    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        default='full_day'
    )

    start_time = models.TimeField(
        null=True,
        blank=True
    )

    end_time = models.TimeField(
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=100,
        blank=True
    )

    is_present = models.BooleanField(
        default=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['planning__date', 'worker']

    def __str__(self):
        return f"{self.worker} - {self.planning} ({self.period})"