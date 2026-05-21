from decimal import Decimal, InvalidOperation

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from properties.models import Amenity


def plain_decimal_str(value) -> str:
    """Representación sin ,00 innecesarios (formularios y m²); conserva decimales significativos."""
    if value is None:
        return ''
    try:
        d = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return str(value)
    if d == d.to_integral_value():
        return str(int(d))
    s = format(d.normalize(), 'f').rstrip('0').rstrip('.')
    return s or '0'


class Development(models.Model):
    OPERATION_CHOICES = [
        ('venta', 'Venta'),
        ('renta', 'Renta'),
        ('venta_renta', 'Venta y Renta'),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('casa', 'Casa / residencial'),
        ('depto', 'Departamento'),
        ('mixto', 'Mixto'),
        ('terreno', 'Terreno / lote'),
    ]
    CONSTRUCTION_STATUS_CHOICES = [
        ('preventa', 'Preventa ✨'),
        ('construccion', 'En Construcción 🏗️'),
        ('entrega_inmediata', 'Entrega Inmediata 🔑'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del Desarrollo")
    slug = models.SlugField(
        max_length=220,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name='Slug (URL pública)',
        help_text='URL: /desarrollos/&lt;slug&gt;/. Se genera solo si lo dejas vacío al guardar.',
    )
    subtitle = models.CharField(
        max_length=280,
        blank=True,
        verbose_name="Subtítulo / tagline",
        help_text="Ej. Residencial vertical · Zona norte de Querétaro",
    )
    description = models.TextField(verbose_name="Descripción")
    developer_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Desarrollador o promotora",
        help_text="Nombre comercial del desarrollador (opcional).",
    )
    amenities_text = models.TextField(
        blank=True,
        verbose_name="Amenidades (lista)",
        help_text="Una amenidad por línea (alberca, gimnasio, cowork, etc.).",
    )
    website_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Sitio web del desarrollo",
    )
    amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name='developments',
        verbose_name='Amenidades (catálogo)',
    )
    location = models.CharField(max_length=200, verbose_name="Ubicación")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud',
        help_text='Coordenada GPS para centrar el mapa.',
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud',
        help_text='Coordenada GPS para centrar el mapa.',
    )
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Estado")
    google_maps_url = models.URLField(max_length=500, blank=True, verbose_name="URL de Google Maps")
    operation_type = models.CharField(max_length=20, choices=OPERATION_CHOICES, default='venta', verbose_name="Tipo de Operación")
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='mixto',
        verbose_name="Tipo de producto",
        help_text="Para filtrar en el listado público (casa, depto, etc.).",
    )
    construction_status = models.CharField(
        max_length=20,
        choices=CONSTRUCTION_STATUS_CHOICES,
        default='preventa',
        verbose_name='Estatus de obra',
    )
    levels = models.PositiveIntegerField(default=0, verbose_name='Niveles')
    total_units = models.IntegerField(verbose_name="Total de Unidades", default=0)
    available_units = models.IntegerField(verbose_name="Unidades Disponibles", default=0)
    parking_spaces = models.PositiveIntegerField(default=0, verbose_name='Cajones de estacionamiento')
    total_m2 = models.PositiveIntegerField(default=0, verbose_name='M2 totales')
    price_from = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Desde")
    delivery_date = models.DateField(verbose_name="Fecha de Entrega", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Desarrollo"
        verbose_name_plural = "Desarrollos"
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not (self.slug or '').strip() and (self.name or '').strip():
            base = slugify(self.name) or 'desarrollo'
            slug = base
            n = 1
            while Development.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('developments:detail', kwargs={'development_slug': self.slug})

    def get_operation_type_display_custom(self):
        return dict(self.OPERATION_CHOICES).get(self.operation_type, '')

    @property
    def price_from_plain(self):
        """Precio para inputs del panel (sin .00 si es entero)."""
        return plain_decimal_str(self.price_from)

    def get_main_image(self):
        """Portada: categoría cover, o legado is_main, o primera imagen."""
        cover = (
            self.images.filter(category=DevelopmentImage.Category.COVER)
            .order_by('order', 'id')
            .first()
        )
        if cover:
            return cover
        legacy = self.images.filter(is_main=True).order_by('order', 'id').first()
        if legacy:
            return legacy
        return self.images.order_by('order', 'id').first()

    def get_amenity_lines(self):
        """Lista de amenidades no vacías (una por línea en amenities_text)."""
        if not self.amenities_text:
            return []
        return [line.strip() for line in self.amenities_text.splitlines() if line.strip()]

    @property
    def amenity_lines(self):
        """Alias para plantillas Django (sin llamada con paréntesis)."""
        return self.get_amenity_lines()

    @property
    def selected_amenities(self):
        """Amenidades del catálogo maestro ordenadas para render visual."""
        return self.amenities.filter(is_active=True).order_by(
            '-priority_score', 'display_name'
        )


class DevelopmentUnitModel(models.Model):
    """
    Modelo de distribución (tipología) dentro de un desarrollo: recámaras, baños, m², precio desde.
    """

    development = models.ForeignKey(
        Development,
        on_delete=models.CASCADE,
        related_name='unit_models',
        verbose_name='Desarrollo',
    )
    name = models.CharField(max_length=120, verbose_name='Nombre del modelo')
    slug = models.SlugField(max_length=130, verbose_name='Slug (URL)')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    bedrooms = models.PositiveSmallIntegerField(default=0, verbose_name='Recámaras')
    bathrooms = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
        verbose_name='Baños',
        help_text='Ej. 2 o 2.5',
    )
    construction_m2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='M² de construcción',
    )
    price_from = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio desde',
        help_text='Opcional; si está vacío se puede mostrar el precio del desarrollo.',
    )
    card_image = models.ImageField(
        upload_to='developments/unit_models/',
        blank=True,
        null=True,
        verbose_name='Imagen (tarjeta)',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Texto breve junto a la ficha (opcional).',
    )
    other_features_text = models.TextField(
        blank=True,
        verbose_name='Otras características',
        help_text='Una viñeta por línea (ej. Jardín, Área de lavado, 2 cajones).',
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Modelo de unidad'
        verbose_name_plural = 'Modelos de unidad'
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['development', 'slug'],
                name='developments_unitmodel_dev_slug_uniq',
            ),
        ]

    def __str__(self):
        return f'{self.development.name} · {self.name}'

    def save(self, *args, **kwargs):
        if not (self.slug or '').strip() and (self.name or '').strip():
            base = slugify(self.name) or 'modelo'
            slug = base
            dev_id = self.development_id
            if dev_id is not None:
                n = 1
                while True:
                    qs = DevelopmentUnitModel.objects.filter(development_id=dev_id, slug=slug)
                    if self.pk:
                        qs = qs.exclude(pk=self.pk)
                    if not qs.exists():
                        break
                    slug = f'{base}-{n}'
                    n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'developments:unit_model_detail',
            kwargs={
                'development_slug': self.development.slug,
                'model_slug': self.slug,
            },
        )

    def display_price_from(self):
        """Precio a mostrar en tarjeta: propio o el del desarrollo."""
        if self.price_from is not None:
            return self.price_from
        return self.development.price_from

    @property
    def bathrooms_display(self):
        """Texto de baños sin decimales innecesarios (2 vs 2.5)."""
        try:
            b = self.bathrooms
            if b is None:
                return '0'
            if not isinstance(b, Decimal):
                b = Decimal(str(b))
            if b == b.to_integral_value():
                return str(int(b))
            s = format(b.normalize(), 'f').rstrip('0').rstrip('.')
            return s or '0'
        except (InvalidOperation, AttributeError, ValueError):
            return '0'

    @property
    def construction_m2_display(self):
        """M² para panel y ficha pública (entero sin .00; 120.5 se mantiene)."""
        return plain_decimal_str(self.construction_m2)

    @property
    def price_from_plain(self):
        """Precio opcional del modelo para el panel (sin centavos si son .00)."""
        return plain_decimal_str(self.price_from)

    def get_other_feature_lines(self):
        if not self.other_features_text:
            return []
        return [line.strip() for line in self.other_features_text.splitlines() if line.strip()]

    @property
    def other_feature_lines(self):
        return self.get_other_feature_lines()


class DevelopmentUnitModelFloorPlan(models.Model):
    """Planta arquitectónica por modelo (pestañas en ficha pública)."""

    unit_model = models.ForeignKey(
        DevelopmentUnitModel,
        on_delete=models.CASCADE,
        related_name='floor_plans',
        verbose_name='Modelo',
    )
    image = models.ImageField(
        upload_to='developments/unit_models/floor_plans/',
        verbose_name='Imagen de planta',
    )
    label = models.CharField(
        max_length=120,
        default='Planta A',
        verbose_name='Etiqueta (pestaña)',
        help_text='Ej. Planta A, Planta B, Planta alta.',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        verbose_name = 'Planta arquitectónica'
        verbose_name_plural = 'Plantas arquitectónicas'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.unit_model.name} · {self.label}'


class DevelopmentUnitModelImage(models.Model):
    """Galería de imágenes por modelo de unidad (tipología)."""

    unit_model = models.ForeignKey(
        DevelopmentUnitModel,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Modelo',
    )
    image = models.ImageField(upload_to='developments/unit_models/gallery/', verbose_name='Imagen')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Leyenda')

    class Meta:
        verbose_name = 'Imagen de modelo'
        verbose_name_plural = 'Imágenes de modelos'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.unit_model.name} · imagen {self.pk}'


class DevelopmentImage(models.Model):
    class Category(models.TextChoices):
        COVER = 'cover', 'Imagen principal (portada)'
        GALLERY = 'gallery', 'Galería general'
        PLANS = 'plans', 'Planos / amenidades'

    development = models.ForeignKey(Development, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='developments/', verbose_name="Imagen")
    is_main = models.BooleanField(default=False, verbose_name="Imagen Principal")
    order = models.IntegerField(default=0, verbose_name="Orden")
    category = models.CharField(
        max_length=16,
        choices=Category.choices,
        default=Category.GALLERY,
        verbose_name='Categoría',
        help_text='Portada: hero del desarrollo. Galería: mosaico principal. Planos: sección aparte.',
    )

    class Meta:
        verbose_name = "Imagen de Desarrollo"
        verbose_name_plural = "Imágenes de Desarrollo"
        ordering = ['-is_main', 'order']  # Principal primero, luego por orden

    def __str__(self):
        return f"Imagen de {self.development.name}"

    @property
    def resolved_image_url(self):
        """URL segura para plantillas (archivo ausente o storage no disponible → cadena vacía)."""
        if not self.image or not getattr(self.image, 'name', None):
            return ''
        try:
            return self.image.url
        except Exception:
            return ''

    def save(self, *args, **kwargs):
        if self.category == self.Category.COVER:
            qs = DevelopmentImage.objects.filter(
                development_id=self.development_id,
                category=self.Category.COVER,
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(is_main=False, category=self.Category.GALLERY)
            self.is_main = True
        else:
            self.is_main = False
        super().save(*args, **kwargs)


class DevelopmentAmenity(models.Model):
    """Catálogo maestro de amenidades con icono fijo."""

    code = models.SlugField(max_length=50, unique=True, verbose_name='Clave')
    name = models.CharField(max_length=120, verbose_name='Amenidad')
    icon = models.CharField(max_length=16, verbose_name='Icono/emoji')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Amenidad de desarrollo'
        verbose_name_plural = 'Amenidades de desarrollo'
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.icon} {self.name}'

    @property
    def icon_class(self):
        """Ícono UI consistente para frontend (sin depender del emoji crudo)."""
        mapping = {
            'alberca': 'bi-water',
            'gym': 'bi-activity',
            'asadores': 'bi-fire',
            'seguridad': 'bi-shield-check',
            'rooftop': 'bi-sunrise',
            'pet': 'bi-heart',
            'cowork': 'bi-laptop',
            'juegos': 'bi-controller',
            'eventos': 'bi-calendar-event',
            'carga-electrica': 'bi-ev-station',
        }
        return mapping.get(self.code, 'bi-grid-1x2')


class DevelopmentsPageConfig(models.Model):
    """Configuración singleton para la página pública de desarrollos."""

    hero_background = models.ImageField(
        upload_to='developments/hero/',
        blank=True,
        null=True,
        verbose_name='Imagen de fondo (hero “Desarrollos únicos”)',
        help_text='Se muestra detrás del título en /desarrollos/. Recomendado: horizontal, alta resolución.',
    )

    # —— CMS: Smart Match (listado) ——
    smart_match_badge = models.CharField(
        max_length=80,
        default='Smart match',
        verbose_name='Etiqueta del quiz',
    )
    smart_match_title = models.CharField(
        max_length=300,
        default='Encuentra tu próximo desarrollo ideal en Querétaro',
        verbose_name='Título del Smart Match',
    )
    smart_match_subtitle = models.CharField(
        max_length=400,
        default='Responde 5 pasos y te enviamos una selección curada según tu perfil.',
        verbose_name='Subtítulo del Smart Match',
    )
    catalog_section_title = models.CharField(
        max_length=200,
        default='Catálogo de desarrollos',
        verbose_name='Título sección catálogo',
    )
    cta_section_title = models.CharField(
        max_length=300,
        default='¿Buscas un desarrollo específico en Querétaro?',
        verbose_name='Título bloque CTA inferior',
    )
    # —— CMS: ficha de desarrollo ——
    detail_amenities_title = models.CharField(
        max_length=200,
        default='Amenidades',
        verbose_name='Título sección amenidades (detalle)',
    )
    detail_amenities_subtitle = models.TextField(
        blank=True,
        default='Espacios y servicios seleccionados para elevar tu estilo de vida.',
        verbose_name='Subtítulo amenidades (detalle)',
    )
    detail_gallery_title = models.CharField(
        max_length=200,
        default='Galería del desarrollo',
        verbose_name='Título galería (detalle)',
    )
    detail_gallery_subtitle = models.TextField(
        blank=True,
        default='Haz clic en cualquier imagen para verla en pantalla completa.',
        verbose_name='Subtítulo galería (detalle)',
    )
    detail_models_title = models.CharField(
        max_length=120,
        default='Modelos',
        verbose_name='Título sección modelos (detalle)',
    )

    class Meta:
        verbose_name = 'Configuración página desarrollos'
        verbose_name_plural = 'Configuración página desarrollos'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Página desarrollos'
