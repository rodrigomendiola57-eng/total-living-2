"""
Script para probar la resolución de URLs en tiempo de ejecución
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'total_living.settings.development')
django.setup()

import json
log_path = r"c:\TOTAL LIVING\.cursor\debug.log"

print("=" * 70)
print("PROBANDO RESOLUCION DE URLs")
print("=" * 70)
print()

# Probar obtener el resolver
try:
    from django.conf import settings
    from django.urls import get_resolver, resolve
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"K","location":"test_url_resolution.py:18","message":"Testing URL resolution","data":{"ROOT_URLCONF":settings.ROOT_URLCONF},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    resolver = get_resolver()
    print(f"Resolver obtenido: {resolver}")
    print(f"URL patterns: {len(resolver.url_patterns)}")
    
    # #region agent log
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"K","location":"test_url_resolution.py:28","message":"Resolver patterns count","data":{"count":len(resolver.url_patterns)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    except: pass
    # #endregion
    
    # Intentar resolver "/"
    try:
        match = resolve('/')
        print(f"URL '/' resuelve a: {match.view_name}")
        print(f"Vista: {match.func}")
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"K","location":"test_url_resolution.py:38","message":"URL / resolved","data":{"view_name":match.view_name},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
    except Exception as e:
        print(f"ERROR al resolver '/': {e}")
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"K","location":"test_url_resolution.py:46","message":"ERROR resolving /","data":{"error":str(e),"type":type(e).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
    
    # Listar todos los patrones
    print("\nPatrones URL encontrados:")
    for i, pattern in enumerate(resolver.url_patterns):
        print(f"  {i+1}. {pattern.pattern}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
