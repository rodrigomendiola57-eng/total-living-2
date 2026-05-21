# Generated manually: Development.slug, DevelopmentsPageConfig CMS, DevelopmentUnitModelImage

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def populate_development_slugs(apps, schema_editor):
    Development = apps.get_model('developments', 'Development')
    for d in Development.objects.all().order_by('id'):
        if getattr(d, 'slug', None):
            continue
        base = slugify(d.name) or 'desarrollo'
        slug = base
        n = 1
        while Development.objects.filter(slug=slug).exclude(pk=d.pk).exists():
            slug = f'{base}-{n}'
            n += 1
        d.slug = slug
        d.save(update_fields=['slug'])


def apply_development_slug_unique_database(apps, schema_editor):
    """
    Aplica unique en slug vía schema editor (CI/staging/upgrade).
    En PostgreSQL limpia restricciones/índices slug previos para evitar DuplicateTable.
    """
    from django.db import models as dj_models

    Development = apps.get_model('developments', 'Development')
    table = Development._meta.db_table

    if schema_editor.connection.vendor == 'postgresql':
        qn = schema_editor.quote_name
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                f'ALTER TABLE {qn(table)} DROP CONSTRAINT IF EXISTS {qn(table + "_slug_key")}'
            )
            cursor.execute(
                """
                SELECT indexname FROM pg_indexes
                WHERE schemaname = current_schema()
                  AND tablename = %s
                  AND indexname ILIKE %s
                """,
                [table, '%slug%'],
            )
            for (idx_name,) in cursor.fetchall():
                cursor.execute(f'DROP INDEX IF EXISTS {qn(idx_name)}')

    old_field = Development._meta.get_field('slug')
    new_field = dj_models.SlugField(
        max_length=220,
        unique=True,
        db_index=True,
        blank=True,
        help_text='URL: /desarrollos/<slug>/. Se genera solo si lo dejas vacío al guardar.',
        verbose_name='Slug (URL pública)',
    )
    new_field.set_attributes_from_name('slug')
    schema_editor.alter_field(Development, old_field, new_field, strict=False)

    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.deferred_sql = [
            stmt
            for stmt in schema_editor.deferred_sql
            if 'slug' not in str(stmt).lower()
        ]


def scrub_deferred_development_slug_like_index(apps, schema_editor):
    """Quita CREATE INDEX …slug… duplicado antes del flush en __exit__ del schema editor."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.deferred_sql = [
        stmt
        for stmt in schema_editor.deferred_sql
        if 'slug' not in str(stmt).lower()
    ]


class Migration(migrations.Migration):

    dependencies = [
        ('developments', '0009_developmentunitmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='development',
            name='slug',
            field=models.SlugField(
                blank=True,
                default='',
                max_length=220,
                verbose_name='Slug (URL pública)',
            ),
        ),
        migrations.RunPython(populate_development_slugs, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='development',
                    name='slug',
                    field=models.SlugField(
                        max_length=220,
                        unique=True,
                        db_index=True,
                        blank=True,
                        help_text='URL: /desarrollos/<slug>/. Se genera solo si lo dejas vacío al guardar.',
                        verbose_name='Slug (URL pública)',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(
                    apply_development_slug_unique_database,
                    migrations.RunPython.noop,
                ),
            ],
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='smart_match_badge',
            field=models.CharField(default='Smart match', max_length=80, verbose_name='Etiqueta del quiz'),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='smart_match_title',
            field=models.CharField(
                default='Encuentra tu próximo desarrollo ideal en Querétaro',
                max_length=300,
                verbose_name='Título del Smart Match',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='smart_match_subtitle',
            field=models.CharField(
                default='Responde 5 pasos y te enviamos una selección curada según tu perfil.',
                max_length=400,
                verbose_name='Subtítulo del Smart Match',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='catalog_section_title',
            field=models.CharField(
                default='Catálogo de desarrollos',
                max_length=200,
                verbose_name='Título sección catálogo',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='cta_section_title',
            field=models.CharField(
                default='¿Buscas un desarrollo específico en Querétaro?',
                max_length=300,
                verbose_name='Título bloque CTA inferior',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='detail_amenities_title',
            field=models.CharField(default='Amenidades', max_length=200, verbose_name='Título sección amenidades (detalle)'),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='detail_amenities_subtitle',
            field=models.TextField(
                blank=True,
                default='Espacios y servicios seleccionados para elevar tu estilo de vida.',
                verbose_name='Subtítulo amenidades (detalle)',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='detail_gallery_title',
            field=models.CharField(
                default='Galería del desarrollo',
                max_length=200,
                verbose_name='Título galería (detalle)',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='detail_gallery_subtitle',
            field=models.TextField(
                blank=True,
                default='Haz clic en cualquier imagen para verla en pantalla completa.',
                verbose_name='Subtítulo galería (detalle)',
            ),
        ),
        migrations.AddField(
            model_name='developmentspageconfig',
            name='detail_models_title',
            field=models.CharField(default='Modelos', max_length=120, verbose_name='Título sección modelos (detalle)'),
        ),
        migrations.CreateModel(
            name='DevelopmentUnitModelImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='developments/unit_models/gallery/', verbose_name='Imagen')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Leyenda')),
                (
                    'unit_model',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='gallery_images',
                        to='developments.developmentunitmodel',
                        verbose_name='Modelo',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Imagen de modelo',
                'verbose_name_plural': 'Imágenes de modelos',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(
            scrub_deferred_development_slug_like_index,
            migrations.RunPython.noop,
        ),
    ]
