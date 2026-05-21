# Generated manually for singleton CMS rows + DB integrity.

from django.db import migrations, models


def _dedupe_and_fill(apps, schema_editor, model_name):
    Model = apps.get_model('panel', model_name)
    rows = list(Model.objects.all().order_by('pk'))
    if len(rows) > 1:
        keep = rows[0]
        Model.objects.exclude(pk=keep.pk).delete()
    Model.objects.all().update(singleton_key='default')


def dedupe_home(apps, schema_editor):
    _dedupe_and_fill(apps, schema_editor, 'HomeContent')


def dedupe_nosotros(apps, schema_editor):
    _dedupe_and_fill(apps, schema_editor, 'NosotrosContent')


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0005_homecontent_service_1_b1_homecontent_service_1_b2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='homecontent',
            name='singleton_key',
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                help_text='Clave fija para garantizar un único registro de configuración.',
                max_length=40,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='nosotroscontent',
            name='singleton_key',
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                help_text='Clave fija para garantizar un único registro de configuración.',
                max_length=40,
                null=True,
            ),
        ),
        migrations.RunPython(dedupe_home, migrations.RunPython.noop),
        migrations.RunPython(dedupe_nosotros, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='homecontent',
            name='singleton_key',
            field=models.CharField(
                db_index=True,
                default='default',
                editable=False,
                help_text='Clave fija para garantizar un único registro de configuración.',
                max_length=40,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='nosotroscontent',
            name='singleton_key',
            field=models.CharField(
                db_index=True,
                default='default',
                editable=False,
                help_text='Clave fija para garantizar un único registro de configuración.',
                max_length=40,
                unique=True,
            ),
        ),
    ]
