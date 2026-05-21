from django.db import migrations


def apply_manifest_copy(apps, schema_editor):
    NosotrosContent = apps.get_model('panel', 'NosotrosContent')
    NosotrosContent.objects.update(
        manifest_t_meaning='Transparencia',
        manifest_t_desc='Verdad completa, sin letras chiquitas.',
        manifest_o_meaning='Orden',
        manifest_o_desc='Procesos claros que aceleran cierres.',
        manifest_t2_meaning='Trabajo con estrategia',
        manifest_t2_desc='No mostramos propiedades, construimos decisiones.',
        manifest_a_meaning='Acompañamiento',
        manifest_a_desc='De principio a fin (y más allá).',
        manifest_l_meaning='Lealtad',
        manifest_l_desc='Tu patrimonio es nuestra prioridad absoluta.',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_manifest_copy, migrations.RunPython.noop),
    ]
