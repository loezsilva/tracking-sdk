"""Testes para o cliente da SDK."""

from error_tracker_sdk.cliente import ClienteErrorTracker


class TestParsearDsn:
    def test_dsn_valido_com_porta(self):
        c = ClienteErrorTracker(dsn="http://abc123@127.0.0.1:8000/proj456")
        assert c.ativo
        assert c._url_base == "http://127.0.0.1:8000"
        assert c._chave_api == "abc123"
        assert c._projeto_id == "proj456"

    def test_dsn_valido_sem_porta(self):
        c = ClienteErrorTracker(dsn="https://chave@exemplo.com/proj")
        assert c.ativo
        assert c._url_base == "https://exemplo.com"

    def test_dsn_vazio(self):
        c = ClienteErrorTracker(dsn="")
        assert not c.ativo

    def test_dsn_none(self):
        c = ClienteErrorTracker(dsn=None)
        assert not c.ativo

    def test_dsn_invalido(self):
        c = ClienteErrorTracker(dsn="nao-e-um-dsn")
        assert not c.ativo


class TestCapturarExcecao:
    def test_cliente_inativo_nao_quebra(self):
        c = ClienteErrorTracker(dsn="")
        c.capturar_excecao(excecao=Exception("teste"))

    def test_captura_com_excecao_direta(self):
        c = ClienteErrorTracker(dsn="http://chave@127.0.0.1:9999/proj")
        # Não deve lançar exceção mesmo com servidor inacessível
        c.capturar_excecao(excecao=ValueError("erro teste"))
