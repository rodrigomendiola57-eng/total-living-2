from django.db import migrations, models


def seed_organigram(apps, schema_editor):
    OrganigramMember = apps.get_model('panel', 'OrganigramMember')
    if OrganigramMember.objects.exists():
        return
    OrganigramMember.objects.create(
        tier='director',
        sort_order=0,
        slug='alfredo-mendiola',
        full_name='Alfredo Mendiola',
        role_label='Director General',
        tag_label='Dirección estratégica',
        tag_icon='bi-briefcase',
        bio='Lidera la visión de Total Living, define estándares de servicio y asegura que cada unidad comercial opere con procesos medibles.',
        expertise_1='Estrategia comercial y posicionamiento',
        expertise_2='Estandarización de procesos',
        expertise_3='Dirección de equipos de alto desempeño',
        email='contacto@totalliving.com',
        url_instagram='https://www.instagram.com/total.living.mx/',
        url_facebook='https://www.facebook.com/total.living.mx?locale=es_LA',
        is_visible=True,
    )
    OrganigramMember.objects.create(
        tier='manager',
        sort_order=0,
        slug='patricia-chavarria',
        full_name='Patricia Chavarría',
        role_label='Gerente Comercial',
        tag_label='Ventas y captación',
        tag_icon='bi-graph-up-arrow',
        bio='Coordina el frente comercial, estructura estrategias de captación y supervisa la correcta ejecución de cada operación activa.',
        expertise_1='Gestión de cartera activa',
        expertise_2='Seguimiento comercial y cierres',
        expertise_3='Estrategias de captación',
        email='contacto@totalliving.com',
        url_whatsapp='https://api.whatsapp.com/send?phone=4428669965',
        is_visible=True,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0007_nosotroscontent_values_cms'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganigramMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.CharField(
                    choices=[
                        ('director', 'Dirección (nivel superior)'),
                        ('manager', 'Gerencia'),
                        ('advisor', 'Asesor / equipo'),
                    ],
                    db_index=True,
                    default='advisor',
                    help_text='Define en qué fila aparece en la página Nosotros.',
                    max_length=20,
                )),
                ('sort_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Orden dentro de la misma fila (menor = más a la izquierda).',
                )),
                ('slug', models.SlugField(
                    help_text='URL pública: /nosotros/equipo/<slug>/ — solo letras minúsculas, números y guiones.',
                    max_length=120,
                    unique=True,
                )),
                ('full_name', models.CharField(max_length=120)),
                ('role_label', models.CharField(max_length=120, verbose_name='Puesto / rol')),
                ('tag_label', models.CharField(blank=True, help_text='Texto de la etiqueta bajo el rol', max_length=120)),
                ('tag_icon', models.CharField(
                    default='bi-briefcase',
                    help_text='Clase Bootstrap Icons, ej. bi-house-heart',
                    max_length=48,
                )),
                ('bio', models.TextField(blank=True)),
                ('expertise_1', models.CharField(blank=True, max_length=220)),
                ('expertise_2', models.CharField(blank=True, max_length=220)),
                ('expertise_3', models.CharField(blank=True, max_length=220)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='organigram/', verbose_name='Foto')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('url_whatsapp', models.CharField(blank=True, help_text='URL completa wa.me o api.whatsapp.com', max_length=500)),
                ('url_instagram', models.CharField(blank=True, max_length=500)),
                ('url_facebook', models.CharField(blank=True, max_length=500)),
                ('url_linkedin', models.CharField(blank=True, max_length=500)),
                ('url_tiktok', models.CharField(blank=True, max_length=500)),
                ('url_x', models.CharField(blank=True, max_length=500, verbose_name='URL X (Twitter)')),
                ('is_visible', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Miembro del organigrama',
                'verbose_name_plural': 'Organigrama',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.RunPython(seed_organigram, noop_reverse),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_1'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_2'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_3'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_4'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_5'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_6'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_7'),
        migrations.RemoveField(model_name='nosotroscontent', name='pillar_8'),
    ]
