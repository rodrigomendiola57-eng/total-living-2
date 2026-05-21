"""
Middleware de debug para capturar requests
"""
import json
import os

log_path = r"c:\TOTAL LIVING\.cursor\debug.log"

class URLDebugMiddleware:
    """Middleware para debug de URLs"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"J","location":"total_living/middleware_debug.py:15","message":"Request received","data":{"path":request.path,"method":request.method},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        # Intentar resolver la URL
        try:
            from django.urls import resolve
            match = resolve(request.path)
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"J","location":"total_living/middleware_debug.py:24","message":"URL resolved successfully","data":{"view_name":match.view_name,"url_name":match.url_name if hasattr(match, 'url_name') else None},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
        except Exception as e:
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"J","location":"total_living/middleware_debug.py:30","message":"ERROR resolving URL","data":{"path":request.path,"error":str(e),"type":type(e).__name__},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
        
        response = self.get_response(request)
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"J","location":"total_living/middleware_debug.py:38","message":"Response generated","data":{"status_code":response.status_code},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        
        return response
