from django.db import models
from django.core.validators import EmailValidator
from django.conf import settings


class Contact(models.Model):
    """Modelo para formularios de contacto"""
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESPONDED = 'responded'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Nueva'),
        (STATUS_IN_PROGRESS, 'En seguimiento'),
        (STATUS_RESPONDED, 'Respondida'),
        (STATUS_CLOSED, 'Cerrada'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Baja'),
        (PRIORITY_MEDIUM, 'Media'),
        (PRIORITY_HIGH, 'Alta'),
    ]
    
    # Información del contacto
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        help_text='Nombre completo del contacto'
    )
    email = models.EmailField(
        max_length=255,
        validators=[EmailValidator()],
        verbose_name='Correo Electrónico'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono de contacto'
    )
    
    # Mensaje
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto',
        help_text='Asunto del mensaje'
    )
    message = models.TextField(
        verbose_name='Mensaje',
        help_text='Contenido del mensaje'
    )
    
    # Relación con propiedad (opcional)
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts',
        verbose_name='Propiedad',
        help_text='Propiedad relacionada (si aplica)'
    )
    
    # Estado
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leído',
        help_text='Marcar como leído'
    )
    is_responded = models.BooleanField(
        default=False,
        verbose_name='Respondido',
        help_text='Marcar como respondido'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
        verbose_name='Estado'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        db_index=True,
        verbose_name='Prioridad'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_contacts',
        verbose_name='Asignado a'
    )
    follow_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de seguimiento'
    )
    source = models.CharField(
        max_length=50,
        default='sitio_web',
        verbose_name='Origen'
    )
    internal_summary = models.TextField(
        blank=True,
        verbose_name='Resumen interno'
    )
    
    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Respuesta'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['property']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"


class ContactNote(models.Model):
    """Notas internas de seguimiento por solicitud."""
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='Solicitud'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_notes',
        verbose_name='Autor'
    )
    note = models.TextField(verbose_name='Nota')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        verbose_name = 'Nota de contacto'
        verbose_name_plural = 'Notas de contacto'
        ordering = ['-created_at']

    def __str__(self):
        author = self.author.username if self.author else 'Sistema'
        return f'{author}: {self.note[:40]}'
