import re

from django import forms
from django.utils.text import slugify

from .models import NosotrosContent, OrganigramMember

_BS_ICON_RE = re.compile(r'^bi-[a-z0-9-]{1,48}$')


def sanitize_bootstrap_icon(raw, fallback):
    s = (raw or '').strip()
    if _BS_ICON_RE.fullmatch(s):
        return s
    return fallback


class NosotrosContentForm(forms.ModelForm):
    class Meta:
        model = NosotrosContent
        exclude = ('singleton_key', 'updated_at')

    def clean_value_1_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('value_1_icon'), 'bi-heart')

    def clean_value_2_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('value_2_icon'), 'bi-shield-check')

    def clean_value_3_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('value_3_icon'), 'bi-people')

    def clean_value_4_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('value_4_icon'), 'bi-globe2')

    def clean_value_5_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('value_5_icon'), 'bi-gem')


class OrganigramMemberForm(forms.ModelForm):
    _STRIP_TEXT_FIELDS = (
        'slug', 'full_name', 'role_label', 'tag_label', 'tag_icon', 'bio',
        'expertise_1', 'expertise_2', 'expertise_3',
        'email', 'url_whatsapp', 'url_instagram', 'url_facebook',
        'url_linkedin', 'url_tiktok', 'url_x',
    )

    class Meta:
        model = OrganigramMember
        fields = [
            'tier',
            'sort_order',
            'slug',
            'full_name',
            'role_label',
            'tag_label',
            'tag_icon',
            'bio',
            'expertise_1',
            'expertise_2',
            'expertise_3',
            'photo',
            'email',
            'url_whatsapp',
            'url_instagram',
            'url_facebook',
            'url_linkedin',
            'url_tiktok',
            'url_x',
            'is_visible',
        ]
        labels = {
            'tier': 'Nivel en la página',
            'sort_order': 'Orden en el nivel',
            'slug': 'Slug (URL del perfil)',
            'full_name': 'Nombre completo',
            'role_label': 'Puesto o rol',
            'tag_label': 'Etiqueta (badge)',
            'tag_icon': 'Icono del badge',
            'bio': 'Biografía',
            'expertise_1': 'Especialidad 1',
            'expertise_2': 'Especialidad 2',
            'expertise_3': 'Especialidad 3',
            'photo': 'Foto',
            'email': 'Correo electrónico',
            'url_whatsapp': 'WhatsApp',
            'url_instagram': 'Instagram',
            'url_facebook': 'Facebook',
            'url_linkedin': 'LinkedIn',
            'url_tiktok': 'TikTok',
            'url_x': 'X (Twitter)',
            'is_visible': 'Visible en la web',
        }
        help_texts = {
            'tier': 'Agrupa la tarjeta en Dirección, Gerencia o Asesores en Nosotros.',
            'sort_order': 'Número menor = aparece antes dentro del mismo nivel.',
            'slug': (
                'Opcional: si lo dejas vacío se genera desde el nombre '
                '(minúsculas, números y guiones). Aparece en /nosotros/equipo/&lt;slug&gt;/.'
            ),
            'full_name': 'Nombre que verán los visitantes en la tarjeta y el perfil.',
            'role_label': 'Título profesional bajo el nombre.',
            'tag_label': 'Texto corto opcional (ej. foco o vertical).',
            'tag_icon': 'Clase Bootstrap Icons, por ejemplo bi-briefcase o bi-house-heart.',
            'bio': 'Resumen que puede mostrarse en la tarjeta del organigrama.',
            'expertise_1': 'Primera viñeta en la página de perfil detallado.',
            'expertise_2': 'Segunda viñeta (opcional).',
            'expertise_3': 'Tercera viñeta (opcional).',
            'photo': 'Cuadrada o vertical. Si editas sin subir archivo, se conserva la actual.',
            'email': 'Opcional. Puede mostrarse en la ficha pública si lo rellenas.',
            'url_whatsapp': 'URL completa (wa.me o api.whatsapp.com/send?phone=…).',
            'url_instagram': 'URL del perfil o página.',
            'url_facebook': 'URL del perfil o página.',
            'url_linkedin': 'URL del perfil (linkedin.com/in/…).',
            'url_tiktok': 'URL del perfil en TikTok.',
            'url_x': 'URL del perfil en X.',
            'is_visible': 'Desmarca para ocultar la ficha sin eliminarla.',
        }
        widgets = {
            'tier': forms.Select(attrs={'class': 'form-control'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vacío = automático desde el nombre',
                'spellcheck': 'false',
            }),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellidos'}),
            'role_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Directora comercial'}),
            'tag_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Inversión'}),
            'tag_icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-briefcase'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Trayectoria y enfoque…'}),
            'expertise_1': forms.TextInput(attrs={'class': 'form-control'}),
            'expertise_2': forms.TextInput(attrs={'class': 'form-control'}),
            'expertise_3': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'url_whatsapp': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://wa.me/52…'}),
            'url_instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.instagram.com/…'}),
            'url_facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.facebook.com/…'}),
            'url_linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.linkedin.com/in/…'}),
            'url_tiktok': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.tiktok.com/@…'}),
            'url_x': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://x.com/…'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_tag_icon(self):
        return sanitize_bootstrap_icon(self.cleaned_data.get('tag_icon'), 'bi-briefcase')

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        for key in self._STRIP_TEXT_FIELDS:
            val = data.get(key)
            if isinstance(val, str):
                data[key] = val.strip()
        if not data.get('full_name'):
            self.add_error('full_name', 'Indica el nombre completo.')
            return data
        if not data.get('role_label'):
            self.add_error('role_label', 'Indica el puesto o rol.')
            return data
        raw_slug = (data.get('slug') or '').strip()
        if raw_slug:
            s = slugify(raw_slug)
            if not s:
                self.add_error('slug', 'El slug no es válido.')
                return data
        elif self.instance.pk and getattr(self.instance, 'slug', None):
            s = self.instance.slug
        else:
            base = slugify((data.get('full_name') or '').strip()) or 'miembro'
            qs = OrganigramMember.objects.exclude(pk=self.instance.pk)
            candidate = base
            n = 2
            while qs.filter(slug=candidate).exists():
                candidate = f'{base}-{n}'
                n += 1
            s = candidate
        if OrganigramMember.objects.exclude(pk=self.instance.pk).filter(slug=s).exists():
            self.add_error('slug', 'Ya existe otra ficha con este slug.')
            return data
        data['slug'] = s
        return data
