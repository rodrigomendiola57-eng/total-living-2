from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre de la Región")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descripción")
    image = models.ImageField(upload_to='regions/', verbose_name="Imagen Principal")
    highlights = models.TextField(verbose_name="Puntos Destacados", help_text="Separar con comas")
    growth_level = models.CharField(max_length=50, choices=[
        ('alto', 'Alto Crecimiento'),
        ('medio', 'Crecimiento Medio'),
        ('emergente', 'Zona Emergente')
    ], default='medio')
    order = models.IntegerField(default=0, verbose_name="Orden de Visualización")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Región"
        verbose_name_plural = "Regiones"

    def __str__(self):
        return self.name

    def get_highlights_list(self):
        return [h.strip() for h in self.highlights.split(',') if h.strip()]
