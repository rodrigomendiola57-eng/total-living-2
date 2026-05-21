@login_required
@user_passes_test(is_staff_user, login_url='/admin/login/')
def download_property_pdf(request, pk):
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    import os
    from django.conf import settings
    
    property_obj = get_object_or_404(Property, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TotalLiving_{property_obj.slug}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    olive = colors.HexColor('#3B3E2A')
    gold = colors.HexColor('#D6B585')
    beige = colors.HexColor('#F2ECE0')
    
    # Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'SharedScreenshot.png')
    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=1.5*inch, height=1.5*inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 0.2*inch))
    
    # Header
    h = Table([[Paragraph('<b><font size=28 color="#3B3E2A">TOTAL LIVING</font></b><br/><font size=12 color="#D6B585">Tu Inmobiliaria de Confianza</font>', ParagraphStyle('H', parent=styles['Normal'], alignment=TA_CENTER))]], colWidths=[7*inch])
    h.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),beige),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),20),('BOTTOMPADDING',(0,0),(-1,-1),20),('BOX',(0,0),(-1,-1),2,olive)]))
    elements.append(h)
    elements.append(Spacer(1, 0.3*inch))
    
    # Título y Precio
    elements.append(Paragraph(property_obj.title.upper(), ParagraphStyle('T', parent=styles['Heading1'], fontSize=20, textColor=olive, alignment=TA_CENTER, fontName='Helvetica-Bold')))
    elements.append(Paragraph(property_obj.get_price_display(), ParagraphStyle('P', parent=styles['Normal'], fontSize=24, textColor=gold, alignment=TA_CENTER, fontName='Helvetica-Bold')))
    elements.append(Spacer(1, 0.2*inch))
    
    # Info General
    ih = Table([[Paragraph('<b><font size=14 color="white">INFORMACIÓN GENERAL</font></b>', styles['Normal'])]], colWidths=[7*inch])
    ih.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    elements.append(ih)
    
    md = [
        ['Tipo:', property_obj.get_property_type_display(), 'Operación:', property_obj.get_operation_type_display()],
        ['Recámaras:', str(property_obj.bedrooms), 'Baños:', str(property_obj.bathrooms)],
        ['Medios Baños:', str(getattr(property_obj,'half_bathrooms',0)), 'Estacionamientos:', str(property_obj.parking_spaces)],
        ['Terreno:', f"{property_obj.lot_area} m²" if property_obj.lot_area else 'N/A', 'Construcción:', f"{property_obj.construction_area} m²" if property_obj.construction_area else 'N/A'],
        ['Niveles:', str(property_obj.floors), 'Año:', str(property_obj.year_built) if property_obj.year_built else 'N/A'],
        ['Ambientes:', str(getattr(property_obj,'rooms',0)), 'Mantenimiento:', f"${getattr(property_obj,'maintenance_fee',0)}" if getattr(property_obj,'maintenance_fee',None) else 'N/A']
    ]
    mt = Table(md, colWidths=[1.5*inch,2*inch,1.5*inch,2*inch])
    mt.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),beige),('BACKGROUND',(2,0),(2,-1),beige),('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),1,colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    elements.append(mt)
    elements.append(Spacer(1, 0.2*inch))
    
    # Distribución
    di = []
    if getattr(property_obj,'has_sala',False): di.append('Sala')
    if getattr(property_obj,'has_comedor',False): di.append('Comedor')
    if getattr(property_obj,'has_cocina',False): di.append('Cocina Integral')
    if getattr(property_obj,'has_estudio',False): di.append('Estudio')
    if getattr(property_obj,'has_despensa',False): di.append('Despensa')
    if getattr(property_obj,'has_cuarto_tv',False): di.append('Cuarto TV')
    if getattr(property_obj,'has_gimnasio',False): di.append('Gimnasio')
    if getattr(property_obj,'has_balcon',False): di.append('Balcón')
    if getattr(property_obj,'has_jardin',False): di.append('Jardín')
    if getattr(property_obj,'has_patio',False): di.append('Patio')
    if getattr(property_obj,'has_roof_garden',False): di.append('Roof Garden')
    if getattr(property_obj,'has_area_lavado',False): di.append('Área de Lavado')
    if getattr(property_obj,'has_bodega',False): di.append('Bodega')
    
    if di:
        dh = Table([[Paragraph('<b><font size=14 color="white">DISTRIBUCIÓN</font></b>', styles['Normal'])]], colWidths=[7*inch])
        dh.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        elements.append(dh)
        dt = Table([[Paragraph('• '+'<br/>• '.join(di), ParagraphStyle('D',parent=styles['Normal'],fontSize=10))]], colWidths=[7*inch])
        dt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.grey),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15)]))
        elements.append(dt)
        elements.append(Spacer(1, 0.2*inch))
    
    # Amenidades
    am = []
    if getattr(property_obj,'amenity_salon',False): am.append('Salón de Usos Múltiples')
    if getattr(property_obj,'amenity_vigilancia',False): am.append('Vigilancia 24/7')
    if getattr(property_obj,'amenity_acceso',False): am.append('Acceso Controlado')
    if getattr(property_obj,'amenity_areas_verdes',False): am.append('Áreas Verdes')
    if getattr(property_obj,'amenity_juegos',False): am.append('Juegos Infantiles')
    if getattr(property_obj,'amenity_gimnasio',False): am.append('Gimnasio')
    if getattr(property_obj,'amenity_alberca',False): am.append('Alberca')
    if getattr(property_obj,'amenity_cancha_futbol',False): am.append('Cancha de Fútbol')
    if getattr(property_obj,'amenity_cancha_tenis',False): am.append('Cancha de Tenis')
    if getattr(property_obj,'amenity_cancha_basket',False): am.append('Cancha de Basketball')
    if getattr(property_obj,'amenity_asadores',False): am.append('Zona de Asadores')
    if getattr(property_obj,'amenity_pet_friendly',False): am.append('Pet Friendly')
    
    if am:
        ah = Table([[Paragraph('<b><font size=14 color="white">AMENIDADES</font></b>', styles['Normal'])]], colWidths=[7*inch])
        ah.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        elements.append(ah)
        at = Table([[Paragraph('• '+'<br/>• '.join(am), ParagraphStyle('A',parent=styles['Normal'],fontSize=10))]], colWidths=[7*inch])
        at.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.grey),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15)]))
        elements.append(at)
        elements.append(Spacer(1, 0.2*inch))
    
    # Servicios
    sv = []
    if getattr(property_obj,'service_agua',False): sv.append('Agua')
    if getattr(property_obj,'service_drenaje',False): sv.append('Drenaje')
    if getattr(property_obj,'service_luz',False): sv.append('Luz')
    if getattr(property_obj,'service_gas',False): sv.append('Gas Estacionario')
    if getattr(property_obj,'service_internet',False): sv.append('Internet')
    if getattr(property_obj,'service_fibra',False): sv.append('Fibra Óptica')
    if getattr(property_obj,'service_cable',False): sv.append('TV Cable')
    if getattr(property_obj,'service_telefono',False): sv.append('Línea Telefónica')
    if getattr(property_obj,'service_cisterna',False): sv.append('Cisterna')
    if getattr(property_obj,'service_hidroneumatico',False): sv.append('Hidroneumático')
    if getattr(property_obj,'service_aire',False): sv.append('Aire Acondicionado')
    if getattr(property_obj,'service_boiler',False): sv.append('Boiler')
    
    if sv:
        sh = Table([[Paragraph('<b><font size=14 color="white">SERVICIOS</font></b>', styles['Normal'])]], colWidths=[7*inch])
        sh.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
        elements.append(sh)
        st = Table([[Paragraph('• '+'<br/>• '.join(sv), ParagraphStyle('S',parent=styles['Normal'],fontSize=10))]], colWidths=[7*inch])
        st.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.grey),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15)]))
        elements.append(st)
        elements.append(Spacer(1, 0.2*inch))
    
    # Ubicación
    lh = Table([[Paragraph('<b><font size=14 color="white">UBICACIÓN</font></b>', styles['Normal'])]], colWidths=[7*inch])
    lh.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    elements.append(lh)
    lt = Table([[Paragraph(f"<b>{property_obj.address}</b><br/>{property_obj.city}, {property_obj.state}<br/>C.P. {property_obj.zip_code if property_obj.zip_code else 'N/A'}", ParagraphStyle('L',parent=styles['Normal'],fontSize=11,alignment=TA_CENTER))]], colWidths=[7*inch])
    lt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.grey),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15)]))
    elements.append(lt)
    elements.append(Spacer(1, 0.2*inch))
    
    # Descripción
    deh = Table([[Paragraph('<b><font size=14 color="white">DESCRIPCIÓN</font></b>', styles['Normal'])]], colWidths=[7*inch])
    deh.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),olive),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    elements.append(deh)
    det = Table([[Paragraph(property_obj.description, ParagraphStyle('DE',parent=styles['Normal'],fontSize=10,alignment=TA_JUSTIFY,leading=14))]], colWidths=[7*inch])
    det.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.grey),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15)]))
    elements.append(det)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    f = Table([[Paragraph('<b><font size=12 color="#3B3E2A">TOTAL LIVING</font></b><br/><font size=9 color="#D6B585">www.totalliving.com | contacto@totalliving.com | Tel: +52 55 1234 5678</font><br/><font size=8>Esta ficha técnica es informativa y no constituye una oferta vinculante</font>', ParagraphStyle('F',parent=styles['Normal'],alignment=TA_CENTER))]], colWidths=[7*inch])
    f.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),beige),('ALIGN',(0,0),(-1,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),15),('BOTTOMPADDING',(0,0),(-1,-1),15),('BOX',(0,0),(-1,-1),2,olive)]))
    elements.append(f)
    
    doc.build(elements)
    return response
