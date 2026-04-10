# Adicionar em ~/tracking-sdk/tracking_sdk/middleware.py (ou onde estiver o DjangoMiddleware)

import time
import threading
import urllib.request
import json

class DjangoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.monotonic()
        response = self.get_response(request)
        duracao_ms = int((time.monotonic() - inicio) * 1000)

        self._enviar_desempenho(request, response, duracao_ms)
        return response

    def _enviar_desempenho(self, request, response, duracao_ms):
        from django.conf import settings

        dsn = getattr(settings, 'TRACKING_DSN', None)
        if not dsn:
            return

        # Parseia o DSN: scheme://chave_api@host/projeto_id
        try:
            from urllib.parse import urlparse
            parsed = urlparse(dsn)
            chave_api = parsed.username
            projeto_id = parsed.path.lstrip('/')
            base_url = f'{parsed.scheme}://{parsed.hostname}'
            if parsed.port:
                base_url += f':{parsed.port}'
        except Exception:
            return

        payload = {
            'url_endpoint': request.path,
            'metodo_http': request.method,
            'status_code': response.status_code,
            'duracao_ms': duracao_ms,
            'usuario': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else '',
            'ambiente': getattr(settings, 'ENVIRONMENT', ''),
        }

        def _enviar():
            try:
                url = f'{base_url}/api/{projeto_id}/desempenho/'
                dados = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=dados,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {chave_api}',
                    },
                    method='POST',
                )
                urllib.request.urlopen(req, timeout=3)
            except Exception:
                pass

        threading.Thread(target=_enviar, daemon=True).start()
