# blank=True solo afecta validación en Django; no cambia el esquema en PostgreSQL.
# Un AlterField normal hacía que Django intentara recrear el índice
# developments_development_slug_*_like y fallaba con DuplicateTable.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0010_slug_cms_unit_gallery'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='development',
                    name='slug',
                    field=models.SlugField(
                        blank=True,
                        db_index=True,
                        help_text='URL: /desarrollos/&lt;slug&gt;/. Se genera solo si lo dejas vacío al guardar.',
                        max_length=220,
                        unique=True,
                        verbose_name='Slug (URL pública)',
                    ),
                ),
            ],
            database_operations=[],
        ),
    ]
