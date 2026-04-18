# Generated manually for PlanningDayOff

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0001_initial'),
        ('workforce', '0002_insurancefund_alter_collaborator_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanningDayOff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planning_day_offs', to='workforce.collaborator')),
            ],
            options={
                'ordering': ['date', 'worker__name'],
            },
        ),
        migrations.AddConstraint(
            model_name='planningdayoff',
            constraint=models.UniqueConstraint(fields=('date', 'worker'), name='planning_dayoff_unique_date_worker'),
        ),
    ]
