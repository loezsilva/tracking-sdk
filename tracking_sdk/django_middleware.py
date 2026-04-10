"""Middleware Django para captura automática de exceções."""

import tracking_sdk


class DjangoMiddleware:
    """Middleware que intercepta exceções não tratadas e envia ao Error Tracker.

    Requer que tracking_sdk.init() tenha sido chamado antes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Captura a exceção e envia ao servidor."""
        cliente = tracking_sdk.obter_cliente()
        if not cliente or not cliente.ativo:
            return None

        contexto = {
            'url': request.path,
            'metodo': request.method,
            'usuario': self._extrair_usuario(request),
        }

        cliente.capturar_excecao(excecao=exception, contexto_extra=contexto)
        return None

    @staticmethod
    def _extrair_usuario(request):
        """Extrai informação do usuário da requisição."""
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                return str(request.user)
        except Exception:
            pass
        return ''
