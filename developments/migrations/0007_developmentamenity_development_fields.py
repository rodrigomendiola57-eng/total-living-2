from django.db import migrations, models


def seed_amenities(apps, schema_editor):
    Amenity = apps.get_model('developments', 'DevelopmentAmenity')
    defaults = [
        ('alberca', 'Alberca', '🏊', 10),
        ('gym', 'Gym', '🏋️', 20),
        ('asadores', 'Asadores', '🍖', 30),
        ('seguridad', 'Seguridad 24/7', '🛡️', 40),
        ('rooftop', 'Rooftop', '🌅', 50),
        ('pet', 'Pet Friendly', '🐾', 60),
        ('cowork', 'Cowork', '💼', 70),
        ('juegos', 'Juegos infantiles', '🧒', 80),
        ('eventos', 'Salón de eventos', '🎉', 90),
        ('carga-electrica', 'Carga eléctrica', '🔌', 100),
    ]
    for code, name, icon, order in defaults:
        Amenity.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'icon': icon,
                'order': order,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0006_development_product_type_developmentspageconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentAmenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(max_length=50, unique=True, verbose_name='Clave')),
                ('name', models.CharField(max_length=120, verbose_name='Amenidad')),
                ('icon', models.CharField(max_length=16, verbose_name='Icono/emoji')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Amenidad de desarrollo',
                'verbose_name_plural': 'Amenidades de desarrollo',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='development',
            name='amenities',
            field=models.ManyToManyField(blank=True, related_name='developments', to='developments.developmentamenity', verbose_name='Amenidades (catálogo)'),
        ),
        migrations.AddField(
            model_name='development',
            name='construction_status',
            field=models.CharField(choices=[('preventa', 'Preventa ✨'), ('construccion', 'En Construcción 🏗️'), ('entrega_inmediata', 'Entrega Inmediata 🔑')], default='preventa', max_length=20, verbose_name='Estatus de obra'),
        ),
        migrations.AddField(
            model_name='development',
            name='levels',
            field=models.PositiveIntegerField(default=0, verbose_name='Niveles'),
        ),
        migrations.AddField(
            model_name='development',
            name='parking_spaces',
            field=models.PositiveIntegerField(default=0, verbose_name='Cajones de estacionamiento'),
        ),
        migrations.AddField(
            model_name='development',
            name='total_m2',
            field=models.PositiveIntegerField(default=0, verbose_name='M2 totales'),
        ),
        migrations.RunPython(seed_amenities, migrations.RunPython.noop),
    ]
