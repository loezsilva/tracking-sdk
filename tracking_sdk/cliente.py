"""Cliente principal da SDK — gerencia conexão e envio de erros."""

import json
import sys
import threading
import traceback as tb_module
from urllib import request as urllib_request
from urllib.parse import urlparse


class ClienteErrorTracker:
    """Cliente que gerencia a conexão com o servidor Error Tracker."""

    def __init__(self, dsn, ambiente='', debug=False):
        self.ambiente = ambiente
        self.debug = debug
        self._url_base, self._chave_api, self._projeto_id = self._parsear_dsn(dsn)

    @property
    def ativo(self):
        """Retorna True se o DSN foi parseado com sucesso."""
        return bool(self._url_base and self._chave_api and self._projeto_id)

    @staticmethod
    def _parsear_dsn(dsn):
        """Parseia o DSN no formato http://<chave>@<host>:<porta>/<projeto_id>."""
        try:
            parsed = urlparse(dsn or '')
            chave = parsed.username
            host = parsed.hostname
            porta = parsed.port
            projeto_id = parsed.path.strip('/')

            if not chave or not host or not projeto_id:
                return None, None, None

            url_base = f'{parsed.scheme}://{host}:{porta}' if porta else f'{parsed.scheme}://{host}'
            return url_base, chave, projeto_id
        except Exception:
            return None, None, None

    def capturar_excecao(self, excecao=None, contexto_extra=None):
        """Captura uma exceção e envia ao servidor."""
        if not self.ativo:
            return

        if excecao is None:
            tipo, valor, tb = sys.exc_info()
            if valor is None:
                return
            excecao = valor
            traceback_formatado = ''.join(tb_module.format_exception(tipo, valor, tb))
        else:
            traceback_formatado = tb_module.format_exc()
            if traceback_formatado == 'NoneType: None\n':
                traceback_formatado = ''.join(
                    tb_module.format_exception(type(excecao), excecao, excecao.__traceback__)
                )

        payload = {
            'mensagem': str(excecao),
            'traceback': traceback_formatado,
            'url_endpoint': '',
            'metodo_http': '',
            'usuario': '',
            'ambiente': self.ambiente,
        }

        if contexto_extra:
            payload['url_endpoint'] = contexto_extra.get('url', payload['url_endpoint'])
            payload['metodo_http'] = contexto_extra.get('metodo', payload['metodo_http'])
            payload['usuario'] = contexto_extra.get('usuario', payload['usuario'])

        self._enviar_async(payload)

    def _enviar_async(self, payload):
        """Despacha o envio em thread separada."""
        thread = threading.Thread(
            target=self._enviar,
            args=(payload,),
            daemon=True,
        )
        thread.start()

    def _enviar(self, payload):
        """Envia o payload ao servidor. Falhas são silenciosas (exceto em modo debug)."""
        try:
            dados = json.dumps(payload).encode('utf-8')
            url = f'{self._url_base.rstrip("/")}/api/{self._projeto_id}/erros/'
            req = urllib_request.Request(
                url,
                data=dados,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self._chave_api}',
                },
                method='POST',
            )
            urllib_request.urlopen(req, timeout=5)
        except Exception as e:
            if self.debug:
                print(f'[ErrorTracker] Falha ao enviar: {e}')
