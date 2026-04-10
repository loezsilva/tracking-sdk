"""
Error Tracker SDK — Captura automática de erros para aplicações Django.

Uso:
    import tracking_sdk
    tracking_sdk.init("http://<chave>@<host>:<porta>/<projeto_id>")

Depois adicione o middleware no settings.py:
    MIDDLEWARE = [
        ...
        "tracking_sdk.DjangoMiddleware",
    ]
"""

from tracking_sdk.cliente import ClienteErrorTracker
from tracking_sdk.django_middleware import DjangoMiddleware

__version__ = '0.1.0'
__all__ = ['init', 'capturar_excecao', 'DjangoMiddleware']

# Instância global do cliente
_cliente = None


def init(dsn, ambiente='', debug=False):
    """Inicializa a SDK com o DSN do projeto.

    Args:
        dsn: URL no formato http://<chave>@<host>:<porta>/<projeto_id>
        ambiente: Nome do ambiente (ex: 'producao', 'staging')
        debug: Se True, imprime erros de envio no console
    """
    global _cliente
    _cliente = ClienteErrorTracker(dsn=dsn, ambiente=ambiente, debug=debug)
    return _cliente


def obter_cliente():
    """Retorna a instância global do cliente, ou None se não inicializado."""
    return _cliente


def capturar_excecao(excecao=None, contexto_extra=None):
    """Captura e envia uma exceção manualmente.

    Args:
        excecao: A exceção a capturar. Se None, usa sys.exc_info().
        contexto_extra: Dict com informações adicionais.
    """
    if _cliente:
        _cliente.capturar_excecao(excecao=excecao, contexto_extra=contexto_extra)
