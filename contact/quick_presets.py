"""
Mensajes rápidos del formulario de contacto.

Los textos se resuelven con gettext en tiempo de petición (idioma activo).
La plantilla escapa con el filtro |escape en atributos HTML (válido en Django 5;
no usar el tag {% filter escape %}, que está restringido).
"""
from typing import Any, Dict, List

from django.utils.translation import gettext as _


def get_contact_quick_presets(property_obj: Any = None) -> List[Dict[str, str]]:
    """
    Devuelve filas {label, message, lead} para pintar chips en contact.html.
    `lead` vacío: no se modifica el select de motivo al pulsar el chip.
    """
    presets: List[Dict[str, str]] = [
        {
            'label': _('Contactarme'),
            'message': _(
                'Hola, quiero que un asesor me contacte para orientarme sobre sus servicios.'
            ),
            'lead': '',
        },
        {
            'label': _('Quiero comprar'),
            'message': _(
                'Estoy buscando opciones para comprar vivienda o inversión; me gustaría recibir recomendaciones.'
            ),
            'lead': 'comprar',
        },
        {
            'label': _('Quiero vender'),
            'message': _('Quiero vender o dar de alta mi propiedad y necesito asesoría.'),
            'lead': 'vender',
        },
        {
            'label': _('Busco renta'),
            'message': _('Busco propiedad en renta; agradecería opciones disponibles.'),
            'lead': 'rentar',
        },
        {
            'label': _('Agendar llamada'),
            'message': _(
                'Me interesa agendar una llamada o videollamada cuando sea posible.'
            ),
            'lead': '',
        },
    ]
    if property_obj is not None:
        title = getattr(property_obj, 'title', '') or ''
        presets.append(
            {
                'label': _('Info de esta propiedad'),
                'message': _(
                    'Solicito información, condiciones y disponibilidad sobre la propiedad: %(title)s.'
                )
                % {'title': title},
                'lead': 'comprar',
            }
        )
    return presets
