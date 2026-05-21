"""
Script para verificar qué está pasando cuando el servidor inicia
"""
import os
import sys
import json

log_path = r"c:\TOTAL LIVING\.cursor\debug.log"

# Cambiar al directorio correcto
os.chdir(r"C:\TOTAL LIVING")
sys.path.insert(0, r"C:\TOTAL LIVING")

print("=" * 70)
print("VERIFICANDO CONFIGURACION DEL SERVIDOR")
print("=" * 70)
print()

# #region agent log
try:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:15","message":"Script started","data":{"cwd":os.getcwd()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

print(f"Directorio actual: {os.getcwd()}")
print(f"Archivo manage.py existe: {os.path.exists('manage.py')}")
print()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')

# #region agent log
try:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:26","message":"DJANGO_SETTINGS_MODULE set","data":{"module":os.environ.get('DJANGO_SETTINGS_MODULE')},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

import django
django.setup()

# #region agent log
try:
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:34","message":"Django setup complete","data":{},"timestamp":int(__import__('time').time()*1000)}) + '\n')
except: pass
# #endregion

from django.conf import settings
from django.urls import get_resolver, resolve

print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
print()

# Intentar importar el módulo de URLs directamente
try:
    import importlib
    url_module = importlib.import_module(settings.ROOT_URLCONF)
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:47","message":"URL module imported directly","data":{"module":settings.ROOT_URLCONF,"has_urlpatterns":hasattr(url_module, 'urlpatterns'),"urlpatterns_count":len(getattr(url_module, 'urlpatterns', []))},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    print(f"URL module importado: {url_module}")
    print(f"Tiene urlpatterns: {hasattr(url_module, 'urlpatterns')}")
    if hasattr(url_module, 'urlpatterns'):
        print(f"urlpatterns count: {len(url_module.urlpatterns)}")
        for i, pattern in enumerate(url_module.urlpatterns[:5]):
            print(f"  {i+1}. {pattern.pattern}")
except Exception as e:
    print(f"ERROR al importar módulo de URLs: {e}")
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:60","message":"ERROR importing URL module","data":{"error":str(e),"type":type(e).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion

print()

# Obtener el resolver
try:
    resolver = get_resolver()
    print(f"Resolver: {resolver}")
    print(f"URL patterns en resolver: {len(resolver.url_patterns)}")
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:73","message":"Resolver obtained","data":{"patterns_count":len(resolver.url_patterns)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    # Intentar resolver "/"
    try:
        match = resolve('/')
        print(f"URL '/' resuelve a: {match.view_name}")
        print(f"Vista: {match.func.__name__}")
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:83","message":"URL / resolved successfully","data":{"view_name":match.view_name},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
    except Exception as e:
        print(f"ERROR al resolver '/': {e}")
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"M","location":"verificar_servidor.py:91","message":"ERROR resolving /","data":{"error":str(e)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
