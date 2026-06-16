# Cambio de M2M: DevelopmentAmenity (bigint) -> properties.Amenity (uuid).
# AlterField falla en PostgreSQL (cannot cast bigint to uuid); recrear la tabla intermedia.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0014_alter_floorplan_label_default'),
        ('properties', '0010_alter_property_property_type_amenitycategory_amenity_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='development',
            name='amenities',
        ),
        migrations.AddField(
            model_name='development',
            name='amenities',
            field=models.ManyToManyField(
                blank=True,
                related_name='developments',
                to='properties.amenity',
                verbose_name='Amenidades (catálogo)',
            ),
        ),
    ]
