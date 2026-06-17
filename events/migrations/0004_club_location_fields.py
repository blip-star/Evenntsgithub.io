from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_add_club_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='country',
            field=models.CharField(blank=True, default='Kenya', max_length=100),
        ),
        migrations.AddField(
            model_name='club',
            name='location_area',
            field=models.CharField(blank=True, help_text='Neighbourhood or street-level location', max_length=200),
        ),
        migrations.AddField(
            model_name='club',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='lon',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
