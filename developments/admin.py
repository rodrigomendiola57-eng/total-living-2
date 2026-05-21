from django.contrib import admin
from .db_compat import floorplan_table_ready
from .models import (
    Development,
    DevelopmentAmenity,
    DevelopmentImage,
    DevelopmentUnitModel,
    DevelopmentUnitModelFloorPlan,
    DevelopmentUnitModelImage,
    DevelopmentsPageConfig,
)


class DevelopmentImageInline(admin.TabularInline):
    model = DevelopmentImage
    extra = 1
    fields = ('image', 'category', 'is_main', 'order')


class DevelopmentUnitModelImageInline(admin.TabularInline):
    model = DevelopmentUnitModelImage
    extra = 0


class DevelopmentUnitModelFloorPlanInline(admin.TabularInline):
    model = DevelopmentUnitModelFloorPlan
    extra = 0
    fields = ('label', 'order', 'image')


class DevelopmentUnitModelInline(admin.StackedInline):
    model = DevelopmentUnitModel
    extra = 0
    prepopulated_fields = {'slug': ('name',)}
    fields = (
        'name',
        'slug',
        'order',
        'bedrooms',
        'bathrooms',
        'construction_m2',
        'price_from',
        'description',
        'other_features_text',
        'card_image',
        'is_active',
    )


@admin.register(Development)
class DevelopmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'city', 'construction_status', 'total_units', 'available_units', 'price_from', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'construction_status', 'city', 'state']
    search_fields = ['name', 'slug', 'subtitle', 'developer_name', 'location', 'city']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DevelopmentImageInline, DevelopmentUnitModelInline]
    filter_horizontal = ['amenities']
    
@admin.register(DevelopmentImage)
class DevelopmentImageAdmin(admin.ModelAdmin):
    list_display = ['development', 'category', 'is_main', 'order']
    list_filter = ['category', 'is_main', 'development']


@admin.register(DevelopmentAmenity)
class DevelopmentAmenityAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'code', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


def _table_column_names(table_name: str) -> set:
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            desc = connection.introspection.get_table_description(cursor, table_name)
        return {row.name for row in desc}
    except Exception:
        return set()


def _developments_page_config_has_cms_columns() -> bool:
    """True si existen columnas CMS (migración 0010+)."""
    table = DevelopmentsPageConfig._meta.db_table
    cols = _table_column_names(table)
    return bool(cols) and 'smart_match_title' in cols


def _development_unit_gallery_table_ready():
    """Evita 500 en admin si la migración de galería aún no está aplicada."""
    try:
        from django.db import connection

        return 'developments_developmentunitmodelimage' in connection.introspection.table_names()
    except Exception:
        return False


@admin.register(DevelopmentUnitModel)
class DevelopmentUnitModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'development', 'bedrooms', 'bathrooms', 'construction_m2', 'order', 'is_active']
    list_filter = ['is_active', 'development']
    search_fields = ['name', 'slug', 'development__name']
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['development']

    def get_inlines(self, request, obj=None):
        inlines = []
        if _development_unit_gallery_table_ready():
            inlines.append(DevelopmentUnitModelImageInline)
        if floorplan_table_ready():
            inlines.append(DevelopmentUnitModelFloorPlanInline)
        return inlines


@admin.register(DevelopmentsPageConfig)
class DevelopmentsPageConfigAdmin(admin.ModelAdmin):
    _fieldsets_full = (
        ('Hero del listado', {'fields': ('hero_background',)}),
        (
            'Smart Match',
            {'fields': ('smart_match_badge', 'smart_match_title', 'smart_match_subtitle')},
        ),
        (
            'Listado público',
            {'fields': ('catalog_section_title', 'cta_section_title')},
        ),
        (
            'Ficha de desarrollo',
            {
                'fields': (
                    'detail_amenities_title',
                    'detail_amenities_subtitle',
                    'detail_gallery_title',
                    'detail_gallery_subtitle',
                    'detail_models_title',
                )
            },
        ),
    )

    def get_list_display(self, request):
        disp = ['id', 'hero_background']
        if _developments_page_config_has_cms_columns():
            disp.append('smart_match_title')
        return disp

    def get_fieldsets(self, request, obj=None):
        if _developments_page_config_has_cms_columns():
            return self._fieldsets_full
        return (('Hero del listado', {'fields': ('hero_background',)}),)

    def has_add_permission(self, request):
        return not DevelopmentsPageConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
