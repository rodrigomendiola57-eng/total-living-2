from django import forms
from .models import Property, PropertyImage, PropertyFeature
from .image_security import validate_image_upload


class PropertyForm(forms.ModelForm):
    """Formulario para crear/editar propiedades"""
    financing_options = forms.MultipleChoiceField(
        required=False,
        choices=Property.FINANCING_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'operation_type', 'status',
            'price', 'currency', 'address', 'city', 'state', 'zip_code', 'country',
            'latitude', 'longitude', 'bedrooms', 'bathrooms', 'parking_spaces',
            'construction_area', 'lot_area', 'floors', 'year_built',
            'is_featured', 'is_new', 'is_advisor_exclusive', 'exclusive_advisor', 'financing_options', 'published_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Casa moderna en zona residencial'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descripción detallada de la propiedad...'
            }),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'operation_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '3',
                'placeholder': 'MXN'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle y número'
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'parking_spaces': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'construction_area': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'lot_area': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'floors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'year_built': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2100'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_advisor_exclusive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'exclusive_advisor': forms.Select(attrs={'class': 'form-select'}),
            'published_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
        help_texts = {
            'latitude': 'Coordenada GPS (opcional)',
            'longitude': 'Coordenada GPS (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['construction_area'].required = True
        if self.instance and self.instance.pk:
            self.fields['financing_options'].initial = self.instance.financing_options or []

    def clean_construction_area(self):
        value = self.cleaned_data.get('construction_area')
        if value is None:
            raise forms.ValidationError('El campo "Área Construcción (m²)" es obligatorio.')
        return value


class PropertyImageForm(forms.ModelForm):
    """Formulario para agregar imágenes a una propiedad"""
    
    class Meta:
        model = PropertyImage
        fields = ['image', 'is_main', 'alt_text', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la imagen'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_image_upload(image)
        return image
