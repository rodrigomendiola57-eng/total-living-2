from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage, PropertyFeature, PropertyFeatureRelation


class PropertyImageInline(admin.TabularInline):
    """Inline para gestionar imágenes desde el admin de propiedades"""
    model = PropertyImage
    extra = 1
    fields = ('image', 'is_main', 'alt_text', 'order')
    ordering = ('order', 'is_main')


class PropertyFeatureInline(admin.TabularInline):
    """Inline para gestionar características desde el admin de propiedades"""
    model = PropertyFeatureRelation
    extra = 1
    autocomplete_fields = ['feature']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Administración de propiedades"""
    
    list_display = [
        'id',
        'title',
        'property_type',
        'operation_type',
        'city',
        'price_display',
        'status',
        'is_advisor_exclusive',
        'exclusive_advisor',
        'is_featured',
        'created_at',
        'image_preview'
    ]
    
    list_filter = [
        'property_type',
        'operation_type',
        'status',
        'is_featured',
        'is_new',
        'is_advisor_exclusive',
        'exclusive_advisor',
        'city',
        'state',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'description',
        'address',
        'city',
        'state',
        'zip_code'
    ]
    
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Tipo y Operación', {
            'fields': ('property_type', 'operation_type', 'status')
        }),
        ('Precio', {
            'fields': ('price', 'currency')
        }),
        ('Ubicación', {
            'fields': (
                'address',
                'city',
                'state',
                'zip_code',
                'country',
                'latitude',
                'longitude'
            )
        }),
        ('Características Físicas', {
            'fields': (
                'bedrooms',
                'bathrooms',
                'parking_spaces',
                'construction_area',
                'lot_area',
                'floors',
                'year_built'
            )
        }),
        ('Opciones', {
            'fields': ('is_featured', 'is_new', 'is_advisor_exclusive', 'exclusive_advisor', 'financing_options', 'published_at')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    inlines = [PropertyImageInline, PropertyFeatureInline]
    
    date_hierarchy = 'created_at'
    
    list_per_page = 25
    
    def price_display(self, obj):
        """Mostrar precio formateado"""
        return obj.get_price_display()
    price_display.short_description = 'Precio'
    price_display.admin_order_field = 'price'
    
    def image_preview(self, obj):
        """Mostrar preview de la imagen principal"""
        main_image = obj.get_main_image()
        if main_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                main_image.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Imagen'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Administración de imágenes de propiedades"""
    
    list_display = [
        'id',
        'property',
        'image_preview',
        'is_main',
        'order',
        'created_at'
    ]
    
    list_filter = ['is_main', 'created_at']
    
    search_fields = ['property__title', 'alt_text']
    
    list_editable = ['is_main', 'order']
    
    def image_preview(self, obj):
        """Mostrar preview de la imagen"""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Sin imagen"
    image_preview.short_description = 'Preview'


@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    """Administración de características"""
    
    list_display = ['name', 'icon', 'usage_count']
    
    search_fields = ['name', 'icon']
    
    def usage_count(self, obj):
        """Contar cuántas propiedades usan esta característica"""
        return obj.propertyfeaturerelation_set.count()
    usage_count.short_description = 'Propiedades'


@admin.register(PropertyFeatureRelation)
class PropertyFeatureRelationAdmin(admin.ModelAdmin):
    """Administración de relaciones propiedad-característica"""
    
    list_display = ['property', 'feature']
    
    list_filter = ['feature']
    
    search_fields = ['property__title', 'feature__name']
    
    autocomplete_fields = ['property', 'feature']
