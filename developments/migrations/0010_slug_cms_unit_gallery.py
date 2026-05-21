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
    PostgreSQL: todo el cambio de esquema va por SQL aquí.

    No usar AlterField en database_operations: en PG Django puede ejecutar más de
    una vez CREATE INDEX …_slug_*_like (p. ej. con SQL diferido) y el contenedor
    entra en bucle de reinicios al fallar migrate.

    SQLite/otros: un solo alter_field.
    """
    Development = apps.get_model('developments', 'Development')
    table = Development._meta.db_table

    if schema_editor.connection.vendor == 'postgresql':
        qn = schema_editor.quote_name
        constraint = f'{table}_slug_key'
        like_idx = f'{table}_slug_64edfc09_like'
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                f'ALTER TABLE {qn(table)} DROP CONSTRAINT IF EXISTS {qn(constraint)}'
            )
            cursor.execute(
                """
                SELECT indexname FROM pg_indexes
                WHERE schemaname = 'public' AND tablename = %s
                  AND (indexname LIKE %s OR indexname = %s)
                """,
                [table, '%slug%like', like_idx],
            )
            for (idx_name,) in cursor.fetchall():
                cursor.execute(f'DROP INDEX IF EXISTS {qn(idx_name)}')
            cursor.execute(
                f'ALTER TABLE {qn(table)} ADD CONSTRAINT {qn(constraint)} '
                f'UNIQUE ({qn("slug")})'
            )
            cursor.execute(
                f'CREATE INDEX IF NOT EXISTS {qn(like_idx)} ON {qn(table)} '
                f'({qn("slug")} varchar_pattern_ops)'
            )
        # Django encola el mismo CREATE INDEX en deferred_sql (p. ej. tras add_field)
        # y lo ejecuta en schema_editor.__exit__ → "already exists" si ya lo creamos.
        schema_editor.deferred_sql = [
            stmt
            for stmt in schema_editor.deferred_sql
            if like_idx not in str(stmt).replace('"', '')
        ]
        return

    from django.db import models as dj_models

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


def scrub_deferred_development_slug_like_index(apps, schema_editor):
    """Quita CREATE INDEX …slug…_like duplicado antes del flush en __exit__ del schema editor."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    Development = apps.get_model('developments', 'Development')
    like_idx = f'{Development._meta.db_table}_slug_64edfc09_like'
    schema_editor.deferred_sql = [
        stmt
        for stmt in schema_editor.deferred_sql
        if like_idx not in str(stmt).replace('"', '')
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
