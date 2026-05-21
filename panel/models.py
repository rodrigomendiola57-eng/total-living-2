from django.db import models


class NosotrosContent(models.Model):
    """CMS singleton: una sola fila activa por `singleton_key`."""

    SINGLETON_DEFAULT = 'default'
    singleton_key = models.CharField(
        max_length=40,
        default=SINGLETON_DEFAULT,
        unique=True,
        editable=False,
        db_index=True,
        help_text='Clave fija para garantizar un único registro de configuración.',
    )

    hero_title = models.CharField(max_length=120, default='Filosofía Total')
    hero_line_1 = models.CharField(
        max_length=220,
        default='En el sector inmobiliario sobran promesas y faltan procesos.',
    )
    hero_line_2 = models.CharField(max_length=220, default='Nosotros elegimos método TOTAL.')

    manifest_title = models.CharField(max_length=140, default='Manifiesto T.O.T.A.L')
    manifest_t_meaning = models.CharField(max_length=140, default='Transparencia')
    manifest_t_desc = models.CharField(
        max_length=220, default='Verdad completa, sin letras chiquitas.'
    )
    manifest_o_meaning = models.CharField(max_length=140, default='Orden')
    manifest_o_desc = models.CharField(
        max_length=220, default='Procesos claros que aceleran cierres.'
    )
    manifest_t2_meaning = models.CharField(
        max_length=140, default='Trabajo con estrategia'
    )
    manifest_t2_desc = models.CharField(
        max_length=220, default='No mostramos propiedades, construimos decisiones.'
    )
    manifest_a_meaning = models.CharField(max_length=140, default='Acompañamiento')
    manifest_a_desc = models.CharField(
        max_length=320,
        default='De principio a fin (y más allá).',
    )
    manifest_l_meaning = models.CharField(max_length=140, default='Lealtad')
    manifest_l_desc = models.CharField(
        max_length=320,
        default='Tu patrimonio es nuestra prioridad absoluta.',
    )

    mission_vision_title = models.CharField(max_length=140, default='Misión y visión')
    mission_title = models.CharField(max_length=80, default='Misión')
    mission_text = models.TextField(
        default='Convertir cada operación inmobiliaria en una decisión clara, segura y rentable, '
                'mediante asesoría profesional y multidisciplinaria, con transparencia, orden y '
                'estrategia en cada etapa del proceso.'
    )
    vision_title = models.CharField(max_length=80, default='Visión')
    vision_text = models.TextField(
        default='Ser la alternativa que pone orden y certeza donde otros improvisan, integrando '
                'decisiones con datos, seguimiento real y negociación estratégica en todo el mercado inmobiliario.'
    )

    team_banner_title = models.CharField(max_length=140, default='Equipo Total Living')

    values_title = models.CharField(max_length=140, default='Valores Total Living')
    values_subtitle = models.CharField(
        max_length=260,
        default='Los principios que guían cada decisión.',
    )
    value_1_icon = models.CharField(max_length=48, default='bi-heart')
    value_1_title = models.CharField(max_length=140, default='Pasión por el Servicio')
    value_1_text = models.CharField(
        max_length=400,
        default='Cada interacción importa: escuchamos, respondemos y acompañamos con energía y cercanía.',
    )
    value_2_icon = models.CharField(max_length=48, default='bi-shield-check')
    value_2_title = models.CharField(max_length=140, default='Integridad')
    value_2_text = models.CharField(
        max_length=400,
        default='Transparencia y criterio profesional en cada paso, sin atajos ni promesas vacías.',
    )
    value_3_icon = models.CharField(max_length=48, default='bi-people')
    value_3_title = models.CharField(max_length=140, default='Trabajo en Equipo')
    value_3_text = models.CharField(
        max_length=400,
        default='Coordinación real entre especialistas para que tu operación avance con orden.',
    )
    value_4_icon = models.CharField(max_length=48, default='bi-globe2')
    value_4_title = models.CharField(max_length=140, default='Responsabilidad Social')
    value_4_text = models.CharField(
        max_length=400,
        default='Contribuimos con prácticas conscientes y relaciones de respeto con clientes y comunidad.',
    )
    value_5_icon = models.CharField(max_length=48, default='bi-gem')
    value_5_title = models.CharField(max_length=140, default='Imagen Impecable')
    value_5_text = models.CharField(
        max_length=400,
        default='Presentación, comunicación y estándares que reflejan la calidad de Total Living.',
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Configuración Nosotros'


class OrganigramMember(models.Model):
    """Ficha de organigrama (Nosotros): dirección, gerencia y asesores — editable desde el panel."""

    TIER_DIRECTOR = 'director'
    TIER_MANAGER = 'manager'
    TIER_ADVISOR = 'advisor'
    TIER_CHOICES = [
        (TIER_DIRECTOR, 'Dirección (nivel superior)'),
        (TIER_MANAGER, 'Gerencia'),
        (TIER_ADVISOR, 'Asesor / equipo'),
    ]

    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default=TIER_ADVISOR,
        db_index=True,
        help_text='Define en qué fila aparece en la página Nosotros.',
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='Orden dentro de la misma fila (menor = más a la izquierda).',
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text='URL pública: /nosotros/equipo/&lt;slug&gt;/ — solo letras minúsculas, números y guiones.',
    )
    full_name = models.CharField(max_length=120)
    role_label = models.CharField(max_length=120, verbose_name='Puesto / rol')
    tag_label = models.CharField(max_length=120, blank=True, help_text='Texto de la etiqueta bajo el rol')
    tag_icon = models.CharField(
        max_length=48,
        default='bi-briefcase',
        help_text='Clase Bootstrap Icons, ej. bi-house-heart',
    )
    bio = models.TextField(blank=True)
    expertise_1 = models.CharField(max_length=220, blank=True)
    expertise_2 = models.CharField(max_length=220, blank=True)
    expertise_3 = models.CharField(max_length=220, blank=True)
    photo = models.ImageField(upload_to='organigram/', blank=True, null=True, verbose_name='Foto')
    email = models.EmailField(blank=True)
    url_whatsapp = models.CharField(max_length=500, blank=True, help_text='URL completa wa.me o api.whatsapp.com')
    url_instagram = models.CharField(max_length=500, blank=True)
    url_facebook = models.CharField(max_length=500, blank=True)
    url_linkedin = models.CharField(max_length=500, blank=True)
    url_tiktok = models.CharField(max_length=500, blank=True)
    url_x = models.CharField(max_length=500, blank=True, verbose_name='URL X (Twitter)')
    is_visible = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Miembro del organigrama'
        verbose_name_plural = 'Organigrama'

    def __str__(self):
        return f'{self.full_name} ({self.get_tier_display()})'

    @property
    def initials(self):
        parts = [p for p in (self.full_name or '').split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        if parts:
            return parts[0][:2].upper()
        return 'TL'


class HomeContent(models.Model):
    """CMS singleton para secciones clave de Inicio."""

    SINGLETON_DEFAULT = 'default'
    singleton_key = models.CharField(
        max_length=40,
        default=SINGLETON_DEFAULT,
        unique=True,
        editable=False,
        db_index=True,
        help_text='Clave fija para garantizar un único registro de configuración.',
    )

    about_eyebrow = models.CharField(max_length=80, default='Quiénes somos')
    about_title = models.CharField(
        max_length=220,
        default='Total Living: Estrategia Real detrás de cada Propiedad',
    )
    about_paragraph_1 = models.TextField(
        default='En Total Living no solo mostramos casas; diseñamos la ruta para que logres tu próxima gran inversión con absoluta certeza.',
    )
    about_paragraph_2 = models.TextField(default='Tu tranquilidad es nuestro mejor cierre.')
    about_cta_text = models.CharField(max_length=60, default='Conócenos')
    about_cta_url = models.CharField(max_length=240, default='/contact/')
    about_image = models.ImageField(
        upload_to='home/',
        blank=True,
        null=True,
        verbose_name='Imagen sección Quiénes somos',
    )

    why_title = models.CharField(max_length=140, default='¿Por qué elegir Total Living?')
    why_subtitle = models.CharField(
        max_length=260,
        default='Trabajamos cada operación con enfoque humano, estrategia inmobiliaria y resultados medibles.',
    )

    why_1_icon = models.CharField(max_length=40, default='bi-shield-lock')
    why_1_title = models.CharField(max_length=140, default='Seguridad Legal y Patrimonial')
    why_1_text = models.CharField(max_length=220, default='Tu tranquilidad es nuestra prioridad absoluta.')
    why_1_bullet_1 = models.CharField(max_length=160, default='Validación documental y notarial.')
    why_1_bullet_2 = models.CharField(max_length=160, default='Contratos blindados y personalizados.')
    why_1_bullet_3 = models.CharField(max_length=160, default='Filtro de prospectos y procesos claros.')
    why_1_bullet_4 = models.CharField(max_length=160, default='Gestión de pagos segura y transparente.')

    why_2_icon = models.CharField(max_length=40, default='bi-megaphone')
    why_2_title = models.CharField(max_length=140, default='Marketing Premium')
    why_2_text = models.CharField(max_length=220, default='Hacemos que tu propiedad destaque del resto.')
    why_2_bullet_1 = models.CharField(max_length=160, default='Fotografía y video de alta calidad.')
    why_2_bullet_2 = models.CharField(max_length=160, default='Publicidad segmentada en Meta.')
    why_2_bullet_3 = models.CharField(max_length=160, default='Posicionamiento en portales premium.')
    why_2_bullet_4 = models.CharField(max_length=160, default='Recorridos virtuales para filtrar visitas.')

    why_3_icon = models.CharField(max_length=40, default='bi-bar-chart-line')
    why_3_title = models.CharField(max_length=140, default='Inteligencia de Mercado')
    why_3_text = models.CharField(max_length=220, default='Vendemos al precio justo, sin perder tiempo.')
    why_3_bullet_1 = models.CharField(max_length=160, default='Análisis comparativo de mercado.')
    why_3_bullet_2 = models.CharField(max_length=160, default='Reportes de tracción comercial.')
    why_3_bullet_3 = models.CharField(max_length=160, default='Estrategia de precio basada en datos.')
    why_3_bullet_4 = models.CharField(max_length=160, default='Acompañamiento para inversión y preventa.')

    why_4_icon = models.CharField(max_length=40, default='bi-patch-check-fill')
    why_4_title = models.CharField(max_length=140, default='Negociación y Cierre')
    why_4_text = models.CharField(max_length=220, default='Expertos en obtener las mejores condiciones para ti.')
    why_4_bullet_1 = models.CharField(max_length=160, default='Cierre acelerado de operaciones.')
    why_4_bullet_2 = models.CharField(max_length=160, default='Mediación profesional entre partes.')
    why_4_bullet_3 = models.CharField(max_length=160, default='Gestión de créditos y viabilidad.')
    why_4_bullet_4 = models.CharField(max_length=160, default='Acompañamiento total hasta firma.')

    services_title = models.CharField(max_length=120, default='Nuestros servicios')
    services_subtitle = models.CharField(
        max_length=220,
        default='Soluciones inmobiliarias diseñadas para acompañarte con estrategia, claridad y resultados reales.',
    )
    service_1_icon = models.CharField(max_length=40, default='bi-chat-square-text')
    service_1_title = models.CharField(max_length=120, default='Asesoría personalizada')
    service_1_text = models.CharField(max_length=220, default='Te acompañamos para comprar, vender o rentar con estrategia clara y atención cercana.')
    service_1_b1 = models.CharField(max_length=150, default='Estrategia a la medida.')
    service_1_b2 = models.CharField(max_length=150, default='Acompañamiento comercial y documental.')
    service_1_b3 = models.CharField(max_length=150, default='Seguimiento puntual hasta el cierre.')
    service_2_icon = models.CharField(max_length=40, default='bi-bar-chart-line')
    service_2_title = models.CharField(max_length=120, default='Análisis de mercado')
    service_2_text = models.CharField(max_length=220, default='Analizamos tu propiedad y su zona para definir el mejor posicionamiento comercial.')
    service_2_b1 = models.CharField(max_length=150, default='Valoración estratégica.')
    service_2_b2 = models.CharField(max_length=150, default='Lectura de oferta y demanda.')
    service_2_b3 = models.CharField(max_length=150, default='Recomendaciones para vender mejor.')
    service_3_icon = models.CharField(max_length=40, default='bi-house-heart')
    service_3_title = models.CharField(max_length=120, default='Compra, venta y renta')
    service_3_text = models.CharField(max_length=220, default='Gestionamos operaciones inmobiliarias con orden, visibilidad y enfoque en resultados.')
    service_3_b1 = models.CharField(max_length=150, default='Promoción profesional.')
    service_3_b2 = models.CharField(max_length=150, default='Filtrado de prospectos y visitas.')
    service_3_b3 = models.CharField(max_length=150, default='Cierre guiado en cada etapa.')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Configuración Inicio'
