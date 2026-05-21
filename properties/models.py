import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify
from .image_security import validate_image_upload, optimize_image_for_storage


class PropertyType(models.TextChoices):
    """Tipos de propiedades disponibles"""
    CASA = 'casa', 'Casa'
    DEPARTAMENTO = 'departamento', 'Departamento'
    TERRENO = 'terreno', 'Terreno'
    CONDOMINIO = 'condominio', 'Condominio'
    CASA_CONDOMINIO = 'casa_condo', 'Casa en condominio'
    PENTHOUSE = 'penthouse', 'Penthouse'
    LOCAL = 'local', 'Local Comercial'
    OFICINA = 'oficina', 'Oficina'
    CONSULTORIO = 'consultorio', 'Consultorio'
    BODEGA = 'bodega', 'Bodega'
    NAVE_INDUSTRIAL = 'nave_industrial', 'Nave industrial'
    RANCHO = 'rancho', 'Rancho'
    OTRO = 'otro', 'Otro'


class PropertyStatus(models.TextChoices):
    """Estados de la propiedad"""
    DISPONIBLE = 'disponible', 'Disponible'
    VENDIDA = 'vendida', 'Vendida'
    RENTADA = 'rentada', 'Rentada'
    RESERVADA = 'reservada', 'Reservada'
    NO_DISPONIBLE = 'no_disponible', 'No Disponible'


class PropertyProcess(models.TextChoices):
    """Proceso/Etapa de la propiedad en el sistema inmobiliario"""
    EN_BUSQUEDA = 'en_busqueda', 'En Búsqueda'
    EN_NEGOCIACION = 'en_negociacion', 'En Negociación'
    EN_PROCESO_LEGAL = 'en_proceso_legal', 'En Proceso Legal'
    EN_ESCRITURACION = 'en_escrituracion', 'En Escrituración'
    CERRADO = 'cerrado', 'Cerrado'
    CANCELADO = 'cancelado', 'Cancelado'
    NO_APLICA = 'no_aplica', 'No Aplica'


class PropertyOperation(models.TextChoices):
    """Tipo de operación"""
    VENTA = 'venta', 'Venta'
    RENTA = 'renta', 'Renta'
    VENTA_RENTA = 'venta_renta', 'Venta o Renta'


class AmenityCategory(models.Model):
    """Categorías normalizadas para amenidades inmobiliarias."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True, verbose_name='Nombre')
    slug = models.SlugField(max_length=140, unique=True, verbose_name='Slug')
    icon = models.CharField(
        max_length=40,
        default='bi-grid-1x2',
        verbose_name='Icono Bootstrap',
        help_text='Ejemplo: bi-shield-check',
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría de amenidades'
        verbose_name_plural = 'Categorías de amenidades'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['sort_order']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Amenity(models.Model):
    """Catálogo maestro de amenidades para propiedades y desarrollos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True, verbose_name='Nombre canónico')
    display_name = models.CharField(max_length=120, verbose_name='Nombre visible')
    slug = models.SlugField(max_length=140, unique=True, verbose_name='Slug')
    category = models.ForeignKey(
        AmenityCategory,
        on_delete=models.PROTECT,
        related_name='amenities',
        verbose_name='Categoría',
    )
    icon = models.CharField(
        max_length=40,
        default='bi-check2-circle',
        verbose_name='Icono Bootstrap',
        help_text='Icono minimalista (Bootstrap Icons). Se pinta en verde olivo en UI.',
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Activa')
    is_premium = models.BooleanField(default=False, db_index=True, verbose_name='Premium')
    priority_score = models.IntegerField(default=0, db_index=True, verbose_name='Score prioridad')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Amenidad'
        verbose_name_plural = 'Amenidades'
        ordering = ['-priority_score', 'display_name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['display_name']),
            models.Index(fields=['is_active', 'priority_score']),
        ]

    def __str__(self):
        return self.display_name

    @property
    def icon_class(self):
        return self.icon or 'bi-check2-circle'


class AmenityAlias(models.Model):
    """Sinónimos/alias para búsqueda robusta de amenidades."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name='Amenidad',
    )
    alias_name = models.CharField(max_length=120, verbose_name='Alias')
    alias_slug = models.SlugField(max_length=140, verbose_name='Alias slug')

    class Meta:
        verbose_name = 'Alias de amenidad'
        verbose_name_plural = 'Aliases de amenidades'
        constraints = [
            models.UniqueConstraint(fields=['amenity', 'alias_slug'], name='amenity_alias_unique_per_amenity'),
            models.UniqueConstraint(fields=['alias_slug'], name='amenity_alias_slug_unique_global'),
        ]
        indexes = [
            models.Index(fields=['alias_slug']),
        ]

    def __str__(self):
        return f'{self.alias_name} -> {self.amenity.display_name}'


class Property(models.Model):
    """Modelo principal para propiedades inmobiliarias"""
    FINANCING_BANK = 'credito_bancario'
    FINANCING_INFONAVIT = 'infonavit'
    FINANCING_FOVISSSTE = 'fovissste'
    FINANCING_COFINAVIT = 'cofinavit'
    FINANCING_APOYO_INFONAVIT = 'apoyo_infonavit'
    FINANCING_INFONAVIT_TOTAL = 'infonavit_total'
    FINANCING_FOVISSSTE_PARA_TODOS = 'fovissste_para_todos'
    FINANCING_ISSFAM = 'issfam'
    FINANCING_COOPERATIVE = 'cooperativa_caja_popular'
    FINANCING_SOFOM = 'sofom'
    FINANCING_LEASE_OPTION = 'arrendamiento_opcion_compra'
    FINANCING_OWNER_DIRECT = 'financiamiento_directo_propietario'
    FINANCING_CHOICES = [
        (FINANCING_BANK, 'Crédito hipotecario bancario'),
        (FINANCING_INFONAVIT, 'INFONAVIT'),
        (FINANCING_FOVISSSTE, 'FOVISSSTE'),
        (FINANCING_COFINAVIT, 'COFINAVIT'),
        (FINANCING_APOYO_INFONAVIT, 'Apoyo Infonavit'),
        (FINANCING_INFONAVIT_TOTAL, 'Infonavit Total'),
        (FINANCING_FOVISSSTE_PARA_TODOS, 'FOVISSSTE para Todos'),
        (FINANCING_ISSFAM, 'ISSFAM'),
        (FINANCING_COOPERATIVE, 'Cooperativa / Caja Popular'),
        (FINANCING_SOFOM, 'SOFOM / financiera no bancaria'),
        (FINANCING_LEASE_OPTION, 'Arrendamiento con opción a compra'),
        (FINANCING_OWNER_DIRECT, 'Financiamiento directo con propietario'),
    ]
    
    # Información básica
    title = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título descriptivo de la propiedad'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name='Slug',
        help_text='URL amigable (se genera automáticamente)'
    )
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la propiedad'
    )
    
    # Tipo y operación
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.CASA,
        verbose_name='Tipo de Propiedad'
    )
    operation_type = models.CharField(
        max_length=20,
        choices=PropertyOperation.choices,
        default=PropertyOperation.VENTA,
        verbose_name='Tipo de Operación'
    )
    status = models.CharField(
        max_length=20,
        choices=PropertyStatus.choices,
        default=PropertyStatus.DISPONIBLE,
        verbose_name='Estado'
    )
    process = models.CharField(
        max_length=30,
        choices=PropertyProcess.choices,
        default=PropertyProcess.EN_BUSQUEDA,
        verbose_name='Proceso/Etapa',
        help_text='Etapa actual en el proceso de venta/renta'
    )
    
    # Precio
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Precio',
        help_text='Precio en moneda local'
    )
    currency = models.CharField(
        max_length=3,
        default='MXN',
        verbose_name='Moneda',
        help_text='Código de moneda (MXN, USD, etc.)'
    )
    
    # Ubicación
    address = models.CharField(
        max_length=255,
        verbose_name='Dirección'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    region = models.ForeignKey(
        'regions.Region',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        verbose_name='Región'
    )
    state = models.CharField(
        max_length=100,
        verbose_name='Estado/Provincia'
    )
    zip_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Código Postal'
    )
    country = models.CharField(
        max_length=100,
        default='México',
        verbose_name='País'
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitud',
        help_text='Coordenada GPS'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitud',
        help_text='Coordenada GPS'
    )
    google_maps_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='URL Google Maps',
        help_text='Link de Google Maps de la ubicación'
    )
    
    # Características físicas
    bedrooms = models.PositiveIntegerField(
        default=0,
        verbose_name='Recámaras',
        help_text='Número de recámaras'
    )
    bathrooms = models.PositiveIntegerField(
        default=0,
        verbose_name='Baños',
        help_text='Número de baños'
    )
    half_bathrooms = models.PositiveIntegerField(
        default=0,
        verbose_name='Medios Baños',
        help_text='Número de medios baños'
    )
    parking_spaces = models.PositiveIntegerField(
        default=0,
        verbose_name='Estacionamientos',
        help_text='Número de espacios de estacionamiento'
    )
    construction_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Área de Construcción (m²)',
        help_text='Área construida en metros cuadrados (obligatorio)'
    )
    lot_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name='Área de Terreno (m²)',
        help_text='Área del terreno en metros cuadrados'
    )
    floors = models.PositiveIntegerField(
        default=1,
        verbose_name='Niveles',
        help_text='Número de pisos o niveles'
    )
    year_built = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de Construcción'
    )
    front_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Medida Frente (m)'
    )
    back_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Medida Fondo (m)'
    )
    rooms = models.PositiveIntegerField(
        default=0,
        verbose_name='Ambientes'
    )
    maintenance_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Cuota de Mantenimiento'
    )
    
    amenities = models.ManyToManyField(
        Amenity,
        through='PropertyAmenity',
        blank=True,
        related_name='properties',
        verbose_name='Amenidades (catálogo)',
    )
    interior_features = models.ManyToManyField(
        'InteriorFeature',
        through='PropertyInteriorFeature',
        blank=True,
        related_name='properties',
        verbose_name='Distribución interior (catálogo)',
    )
    service_features = models.ManyToManyField(
        'ServiceFeature',
        through='PropertyServiceFeature',
        blank=True,
        related_name='properties',
        verbose_name='Servicios disponibles (catálogo)',
    )

    # Gestión comercial interna (solo panel/admin)
    is_advisor_exclusive = models.BooleanField(
        default=False,
        verbose_name='Exclusiva de asesor',
        help_text='Solo visible para administración/panel interno'
    )
    exclusive_advisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exclusive_properties',
        verbose_name='Asesor responsable de la exclusiva'
    )
    financing_options = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Opciones de financiamiento',
        help_text='Solo visible para administración/panel interno'
    )
    
    # Información adicional
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacada',
        help_text='Mostrar en la página principal'
    )
    is_new = models.BooleanField(
        default=False,
        verbose_name='Nueva',
        help_text='Marcar como propiedad nueva'
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Publicación'
    )
    
    class Meta:
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['property_type']),
            models.Index(fields=['operation_type']),
            models.Index(fields=['city']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['construction_area'], name='prop_construction_area_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.city}"
    
    def save(self, *args, **kwargs):
        """Generar slug automáticamente si no existe"""
        if self.construction_area is None:
            raise ValidationError({'construction_area': 'El área de construcción es obligatoria.'})
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL absoluta para la propiedad"""
        return reverse('properties:detail', kwargs={'pk': self.pk})
    
    def get_main_image(self):
        """Obtener la imagen principal de la propiedad"""
        prefetched = getattr(self, '_prefetched_objects_cache', {}).get('images')
        if prefetched is not None:
            for image in prefetched:
                if image.is_main:
                    return image
            return prefetched[0] if prefetched else None
        return self.images.filter(is_main=True).first() or self.images.first()
    
    def get_price_display(self):
        """Formatear el precio para mostrar"""
        return f"${self.price:,.2f} {self.currency}"

    def get_location_line_display(self):
        """Una sola línea de ubicación: omite campos vacíos y usa región si falta ciudad/estado."""
        parts = []
        for val in (self.address, self.city, self.state):
            s = (val or '').strip()
            if s:
                parts.append(s)
        if not parts and self.region_id:
            try:
                rname = (self.region.name or '').strip() if self.region else ''
                if rname:
                    parts.append(rname)
            except Exception:
                pass
        if not parts and (self.country or '').strip():
            parts.append((self.country or '').strip())
        return ', '.join(parts)

    def get_financing_options_display(self):
        labels = dict(self.FINANCING_CHOICES)
        return [labels.get(code, code) for code in (self.financing_options or [])]


class PropertyImage(models.Model):
    """Modelo para imágenes de propiedades"""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Propiedad'
    )
    image = models.ImageField(
        upload_to='properties/',
        verbose_name='Imagen',
        help_text='Imagen de la propiedad'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Imagen Principal',
        help_text='Marcar como imagen principal'
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Texto Alternativo',
        help_text='Descripción de la imagen para accesibilidad'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Imagen de Propiedad'
        verbose_name_plural = 'Imágenes de Propiedades'
        ordering = ['is_main', 'order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['property'],
                condition=Q(is_main=True),
                name='uniq_property_one_main_image',
            ),
        ]
    
    def __str__(self):
        return f"Imagen de {self.property.title}"

    def save(self, *args, **kwargs):
        if self.image:
            validate_image_upload(self.image)
            self.image = optimize_image_for_storage(self.image, max_width=1920)

        if self.is_main and self.property_id:
            PropertyImage.objects.filter(
                property_id=self.property_id,
                is_main=True,
            ).exclude(pk=self.pk).update(is_main=False)

        super().save(*args, **kwargs)


class CarouselSlide(models.Model):
    """Modelo para gestionar slides del carrusel principal"""
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título del slide'
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Subtítulo',
        help_text='Subtítulo o descripción breve'
    )
    image = models.ImageField(
        upload_to='carousel/',
        verbose_name='Imagen',
        help_text='Imagen del slide (recomendado: 1920x1080px)'
    )
    link_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL de Enlace',
        help_text='URL a la que redirigir al hacer clic (opcional)'
    )
    link_text = models.CharField(
        max_length=100,
        blank=True,
        default='Ver Más',
        verbose_name='Texto del Botón',
        help_text='Texto del botón de acción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Mostrar este slide en el carrusel'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden de visualización (menor número = primero)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    class Meta:
        verbose_name = 'Slide del Carrusel'
        verbose_name_plural = 'Slides del Carrusel'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({'Activo' if self.is_active else 'Inactivo'})"
    
    def save(self, *args, **kwargs):
        """Optimizar imagen antes de guardar."""
        if self.image:
            validate_image_upload(self.image)
            self.image = optimize_image_for_storage(self.image, max_width=1920)

        super().save(*args, **kwargs)


class PropertyFeature(models.Model):
    """Modelo para características adicionales de propiedades"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre de la característica (ej: Piscina, Jardín, etc.)'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icono',
        help_text='Clase de icono (FontAwesome, Material Icons, etc.)'
    )
    
    class Meta:
        verbose_name = 'Característica'
        verbose_name_plural = 'Características'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PropertyFeatureRelation(models.Model):
    """Relación entre propiedades y características"""
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name='Propiedad'
    )
    feature = models.ForeignKey(
        PropertyFeature,
        on_delete=models.CASCADE,
        verbose_name='Característica'
    )
    
    class Meta:
        verbose_name = 'Característica de Propiedad'
        verbose_name_plural = 'Características de Propiedades'
        unique_together = ['property', 'feature']
    
    def __str__(self):
        return f"{self.property.title} - {self.feature.name}"


class PropertyAmenity(models.Model):
    """Relación normalizada propiedad ↔ amenidad."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='property_amenity_links',
        verbose_name='Propiedad',
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='property_amenity_links',
        verbose_name='Amenidad',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Amenidad de propiedad'
        verbose_name_plural = 'Amenidades de propiedades'
        constraints = [
            models.UniqueConstraint(fields=['property', 'amenity'], name='property_amenity_unique'),
        ]
        indexes = [
            models.Index(fields=['amenity']),
        ]

    def __str__(self):
        return f'{self.property_id} - {self.amenity.display_name}'


class InteriorFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    icon = models.CharField(max_length=40, default='bi-house')
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class ServiceFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    icon = models.CharField(max_length=40, default='bi-tools')
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class PropertyInteriorFeature(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    feature = models.ForeignKey(InteriorFeature, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'feature'], name='property_interior_feature_unique'),
        ]


class PropertyServiceFeature(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    feature = models.ForeignKey(ServiceFeature, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'feature'], name='property_service_feature_unique'),
        ]
