from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NosotrosContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(default='Filosofía Total', max_length=120)),
                ('hero_line_1', models.CharField(default='En el sector inmobiliario sobran promesas y faltan procesos.', max_length=220)),
                ('hero_line_2', models.CharField(default='Nosotros elegimos método TOTAL.', max_length=220)),
                ('pillar_1', models.CharField(default='No improvisamos', max_length=140)),
                ('pillar_2', models.CharField(default='No vendemos por presión', max_length=140)),
                ('pillar_3', models.CharField(default='Tomamos decisiones con datos', max_length=140)),
                ('pillar_4', models.CharField(default='Ejecutamos con orden', max_length=140)),
                ('pillar_5', models.CharField(default='Respuesta ágil y seguimiento real', max_length=140)),
                ('pillar_6', models.CharField(default='Documentación clara en cada etapa', max_length=140)),
                ('pillar_7', models.CharField(default='Trabajo coordinado entre especialistas', max_length=140)),
                ('pillar_8', models.CharField(default='Negociación enfocada en rentabilidad', max_length=140)),
                ('manifest_title', models.CharField(default='Manifiesto T.O.T.A.L', max_length=140)),
                ('manifest_t_meaning', models.CharField(default='Transparencia', max_length=140)),
                ('manifest_t_desc', models.CharField(default='Comunicación clara y honesta.', max_length=220)),
                ('manifest_o_meaning', models.CharField(default='Orden', max_length=140)),
                ('manifest_o_desc', models.CharField(default='Procesos definidos en cada etapa.', max_length=220)),
                ('manifest_t2_meaning', models.CharField(default='Trazabilidad', max_length=140)),
                ('manifest_t2_desc', models.CharField(default='Seguimiento visible y documentado.', max_length=220)),
                ('manifest_a_meaning', models.CharField(default='Acompañamiento real', max_length=140)),
                ('manifest_a_desc', models.CharField(default='Del primer mensaje a la firma y después: seguimiento cercano en cada paso del proceso.', max_length=320)),
                ('manifest_l_meaning', models.CharField(default='Lealtad al cliente', max_length=140)),
                ('manifest_l_desc', models.CharField(default='Tu interés primero, con negociación firme y criterio profesional en cada decisión.', max_length=320)),
                ('mission_vision_title', models.CharField(default='Misión y visión', max_length=140)),
                ('mission_title', models.CharField(default='Misión', max_length=80)),
                ('mission_text', models.TextField(default='Convertir cada operación inmobiliaria en una decisión clara, segura y rentable, mediante asesoría profesional y multidisciplinaria, con transparencia, orden y estrategia en cada etapa del proceso.')),
                ('vision_title', models.CharField(default='Visión', max_length=80)),
                ('vision_text', models.TextField(default='Ser la alternativa que pone orden y certeza donde otros improvisan, integrando decisiones con datos, seguimiento real y negociación estratégica en todo el mercado inmobiliario.')),
                ('team_banner_title', models.CharField(default='Equipo Total Living', max_length=140)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
