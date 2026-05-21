import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.utils import OperationalError, ProgrammingError
from .models import Contact
from .spam_protection import ratelimit_contact, is_honeypot_triggered
from .quick_presets import get_contact_quick_presets
from properties.models import Property

logger = logging.getLogger(__name__)

# Captación de leads (se guarda en el mismo modelo Contact → buzón del panel)
LEAD_INTEREST_LABELS = {
    'comprar': 'Comprar vivienda o inversión',
    'vender': 'Vender o publicar una propiedad',
    'rentar': 'Rentar (inquilino)',
    'inversion': 'Inversión inmobiliaria',
    'valuacion': 'Valuación o avalúo',
    'desarrollo': 'Desarrollo / preventa',
    'otro': 'Otro',
}
CONTACT_CHANNEL_LABELS = {
    'email': 'Correo electrónico',
    'whatsapp': 'WhatsApp',
    'llamada': 'Llamada telefónica',
    'cualquiera': 'Cualquier medio',
}
TIMELINE_LABELS = {
    'inmediato': 'Lo antes posible',
    '1_3_meses': 'En 1 a 3 meses',
    'explorando': 'Solo estoy explorando',
}
# ?servicio= desde enlaces del sitio (p. ej. navbar)
SERVICIO_QUERY_TO_LEAD = {
    'inversion': 'inversion',
    'compra': 'comprar',
    'venta': 'vender',
    'renta': 'rentar',
}


def _contact_prefill_from_request(request):
    subject = (request.GET.get('subject') or request.GET.get('asunto') or '').strip()
    message = (request.GET.get('message') or request.GET.get('mensaje') or '').strip()
    return subject, message


def _prefill_lead_interest_from_request(request):
    raw = (request.GET.get('servicio') or '').strip().lower()
    code = SERVICIO_QUERY_TO_LEAD.get(raw, '')
    return code if code in LEAD_INTEREST_LABELS else ''


def _sanitize_lead_choice(post, key, allowed):
    v = (post.get(key) or '').strip()
    return v if v in allowed else ''


def _compose_lead_preamble(lead_interest, contact_channel, timeline, marketing_ok):
    lines = []
    if lead_interest:
        label = LEAD_INTEREST_LABELS.get(lead_interest)
        if label:
            lines.append(f'Interés: {label}')
    if contact_channel:
        label = CONTACT_CHANNEL_LABELS.get(contact_channel)
        if label:
            lines.append(f'Medio de contacto preferido: {label}')
    if timeline:
        label = TIMELINE_LABELS.get(timeline)
        if label:
            lines.append(f'Plazo aproximado: {label}')
    if marketing_ok:
        lines.append('Acepta recibir información comercial y seguimiento: Sí')
    if not lines:
        return ''
    return '[Captación de lead]\n' + '\n'.join(lines) + '\n\n---\n\n'


def _contact_template_context(request, property_obj=None, form_data=None):
    prefill_subject, prefill_message = _contact_prefill_from_request(request)
    ctx = {
        'property': property_obj,
        'prefill_subject': prefill_subject,
        'prefill_message': prefill_message,
        'prefill_lead_interest': _prefill_lead_interest_from_request(request),
        'lead_interest_items': list(LEAD_INTEREST_LABELS.items()),
        'contact_channel_items': list(CONTACT_CHANNEL_LABELS.items()),
        'timeline_items': list(TIMELINE_LABELS.items()),
        'contact_quick_presets': get_contact_quick_presets(property_obj),
    }
    if form_data is not None:
        ctx['form_data'] = form_data
    return ctx


@require_http_methods(["GET", "POST"])
@ratelimit_contact
def contact_view(request):
    """Vista para formulario de contacto"""
    property_id = request.GET.get('property', None)
    property_obj = None
    
    if property_id:
        try:
            property_obj = Property.objects.get(pk=property_id, status='disponible')
        except Property.DoesNotExist:
            pass
    
    if request.method == 'POST':
        if getattr(request, 'contact_rate_limited', False):
            messages.error(
                request,
                'Has enviado demasiados mensajes en poco tiempo. Intenta nuevamente en unos minutos.',
            )
            return render(
                request,
                'contact/contact.html',
                _contact_template_context(request, property_obj=property_obj, form_data=request.POST),
            )

        if is_honeypot_triggered(request):
            # Respuesta neutra: evita dar feedback util a bots.
            messages.success(
                request,
                '¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.',
            )
            return redirect('contact:contact')

        # Procesar formulario
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        property_id = request.POST.get('property_id', '').strip()

        lead_interest = _sanitize_lead_choice(request.POST, 'lead_interest', LEAD_INTEREST_LABELS)
        contact_channel = _sanitize_lead_choice(request.POST, 'contact_channel', CONTACT_CHANNEL_LABELS)
        timeline = _sanitize_lead_choice(request.POST, 'timeline', TIMELINE_LABELS)
        marketing_ok = request.POST.get('marketing_ok') == '1'

        if property_id:
            try:
                property_obj = Property.objects.get(pk=property_id, status='disponible')
            except Property.DoesNotExist:
                property_obj = None
        
        # Validación básica
        if not name or not email or not message:
            messages.error(request, 'Por favor completa todos los campos requeridos.')
            return render(
                request,
                'contact/contact.html',
                _contact_template_context(request, property_obj=property_obj, form_data=request.POST),
            )

        preamble = _compose_lead_preamble(lead_interest, contact_channel, timeline, marketing_ok)
        full_message = preamble + message if preamble else message

        if property_obj and not subject:
            subject = f'Consulta · {property_obj.title}'[:200]
        elif not subject:
            subject = 'Consulta desde sitio web'
        if lead_interest:
            short = {'comprar': '[Compra]', 'vender': '[Venta]', 'rentar': '[Renta]', 'inversion': '[Inv.]',
                     'valuacion': '[Valuación]', 'desarrollo': '[Desarrollo]', 'otro': '[Consulta]'}.get(lead_interest, '')
            if short and short not in subject:
                subject = f'{short} {subject}'[:200]

        # Crear contacto (mismo modelo que el buzón CRM del panel)
        try:
            contact = Contact.objects.create(
                name=name,
                email=email,
                phone=phone if phone else '',
                subject=subject[:200],
                message=full_message,
                property=property_obj if property_obj else None,
                status=Contact.STATUS_NEW,
                source='sitio_web_propiedad' if property_obj else 'sitio_web',
            )
            
            messages.success(
                request, 
                '¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.'
            )
            return redirect('contact:contact')
        except (OperationalError, ProgrammingError) as e:
            logger.exception('Fallo de base de datos al registrar contacto web')
            messages.error(request, 'Hubo un error al enviar tu mensaje. Por favor intenta de nuevo.')
            return render(
                request,
                'contact/contact.html',
                _contact_template_context(request, property_obj=property_obj, form_data=request.POST),
            )

    return render(
        request,
        'contact/contact.html',
        _contact_template_context(request, property_obj=property_obj),
    )


@require_http_methods(["GET", "POST"])
@ratelimit_contact
def advisory_purchase_view(request):
    """Modulo independiente para asesoria de compra inmobiliaria."""
    if request.method == 'POST':
        if getattr(request, 'contact_rate_limited', False):
            messages.error(
                request,
                'Has enviado demasiadas solicitudes en poco tiempo. Intenta nuevamente en unos minutos.',
            )
            return render(request, 'contact/advisory_purchase.html', {
                'form_data': request.POST,
            })

        if is_honeypot_triggered(request):
            messages.success(
                request,
                '¡Gracias por tu solicitud! Un asesor de compra te contactara pronto.',
            )
            return redirect('contact:advisory_purchase')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        property_type = request.POST.get('property_type', '').strip()
        budget = request.POST.get('budget', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not city:
            messages.error(request, 'Por favor completa los campos requeridos para la asesoria de compra.')
            return render(request, 'contact/advisory_purchase.html', {
                'form_data': request.POST,
            })

        composed_message = (
            f"Ciudad o zona de interes: {city}\n"
            f"Tipo de propiedad: {property_type or 'Sin especificar'}\n"
            f"Presupuesto estimado: {budget or 'Sin especificar'}\n\n"
            f"Detalle del cliente:\n{message or 'Sin comentarios adicionales.'}"
        )

        try:
            Contact.objects.create(
                name=name,
                email=email,
                phone=phone if phone else '',
                subject='Asesoria de compra inmobiliaria',
                message=composed_message,
                status=Contact.STATUS_NEW,
                source='asesoria_compra'
            )

            messages.success(
                request,
                '¡Solicitud enviada! Te contactaremos para iniciar tu asesoria de compra.',
            )
            return redirect('contact:advisory_purchase')
        except (OperationalError, ProgrammingError):
            logger.exception('Fallo de base de datos al registrar asesoria de compra')
            messages.error(request, 'Hubo un error al enviar tu solicitud. Intenta nuevamente.')

    return render(request, 'contact/advisory_purchase.html')


@require_http_methods(["GET", "POST"])
@ratelimit_contact
def advisory_sale_view(request):
    """Modulo independiente para captar propietarios que quieren vender/anunciar."""
    if request.method == 'POST':
        if getattr(request, 'contact_rate_limited', False):
            messages.error(
                request,
                'Has enviado demasiadas solicitudes en poco tiempo. Intenta nuevamente en unos minutos.',
            )
            return render(request, 'contact/advisory_sale.html', {
                'form_data': request.POST,
            })

        if is_honeypot_triggered(request):
            messages.success(
                request,
                '¡Gracias por tu solicitud! Un asesor de venta te contactara pronto.',
            )
            return redirect('contact:advisory_sale')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        property_type = request.POST.get('property_type', '').strip()
        estimated_price = request.POST.get('estimated_price', '').strip()
        sale_urgency = request.POST.get('sale_urgency', '').strip()
        exclusive_interest = request.POST.get('exclusive_interest', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not city:
            messages.error(request, 'Por favor completa los campos requeridos para la asesoria de venta.')
            return render(request, 'contact/advisory_sale.html', {
                'form_data': request.POST,
            })

        composed_message = (
            f"Ciudad o zona del inmueble: {city}\n"
            f"Tipo de propiedad: {property_type or 'Sin especificar'}\n"
            f"Valor estimado: {estimated_price or 'Sin especificar'}\n"
            f"Urgencia de venta: {sale_urgency or 'Sin especificar'}\n"
            f"Interes en exclusiva: {exclusive_interest or 'Sin especificar'}\n\n"
            f"Detalle del propietario:\n{message or 'Sin comentarios adicionales.'}"
        )

        try:
            Contact.objects.create(
                name=name,
                email=email,
                phone=phone if phone else '',
                subject='Asesoria de venta inmobiliaria',
                message=composed_message,
                status=Contact.STATUS_NEW,
                source='asesoria_venta'
            )

            messages.success(
                request,
                '¡Solicitud enviada! Te contactaremos para ayudarte a vender tu propiedad.',
            )
            return redirect('contact:advisory_sale')
        except (OperationalError, ProgrammingError):
            logger.exception('Fallo de base de datos al registrar asesoria de venta')
            messages.error(request, 'Hubo un error al enviar tu solicitud. Intenta nuevamente.')

    return render(request, 'contact/advisory_sale.html')
