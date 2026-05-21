from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Region

def regions_list(request):
    regions = Region.objects.filter(is_active=True).annotate(
        available_properties_count=Count(
            'properties',
            filter=Q(properties__status='disponible'),
            distinct=True
        )
    )
    return render(request, 'regions/list.html', {'regions': regions})

@login_required
def panel_regions(request):
    regions = Region.objects.all()
    return render(request, 'regions/panel/list.html', {'regions': regions})

@login_required
def panel_region_add(request):
    if request.method == 'POST':
        region = Region.objects.create(
            name=request.POST['name'],
            slug=request.POST['slug'],
            description=request.POST['description'],
            highlights=request.POST['highlights'],
            growth_level=request.POST['growth_level'],
            order=request.POST.get('order', 0),
            is_active=request.POST.get('is_active') == 'on'
        )
        if request.FILES.get('image'):
            region.image = request.FILES['image']
            region.save()
        messages.success(request, 'Región agregada exitosamente')
        return redirect('regions:panel_regions')
    return render(request, 'regions/panel/add.html')

@login_required
def panel_region_edit(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == 'POST':
        region.name = request.POST['name']
        region.slug = request.POST['slug']
        region.description = request.POST['description']
        region.highlights = request.POST['highlights']
        region.growth_level = request.POST['growth_level']
        region.order = request.POST.get('order', 0)
        region.is_active = request.POST.get('is_active') == 'on'
        if request.FILES.get('image'):
            region.image = request.FILES['image']
        region.save()
        messages.success(request, 'Región actualizada exitosamente')
        return redirect('regions:panel_regions')
    return render(request, 'regions/panel/edit.html', {'region': region})

@login_required
def panel_region_delete(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == 'POST':
        region.delete()
        messages.success(request, 'Región eliminada exitosamente')
        return redirect('regions:panel_regions')
    return render(request, 'regions/panel/delete.html', {'region': region})
