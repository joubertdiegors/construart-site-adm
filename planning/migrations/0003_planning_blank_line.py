from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0002_planning_day_off'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanningBlankLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('slot_index', models.PositiveSmallIntegerField()),
                ('line_index', models.PositiveSmallIntegerField()),
                ('text', models.CharField(blank=True, max_length=240)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('date', 'slot_index', 'line_index'),
            },
        ),
        migrations.AddConstraint(
            model_name='planningblankline',
            constraint=models.UniqueConstraint(
                fields=('date', 'slot_index', 'line_index'),
                name='planning_blankline_unique_date_slot_line',
            ),
        ),
    ]
