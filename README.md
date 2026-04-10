# Tracking SDK

SDK para captura automática de erros em aplicações Django.

## Instalação

```bash
pip install tracking-sdk
```

Ou direto do repositório:

```bash
pip install git+https://github.com/loezsilva/tracking-sdk.git#subdirectory=sdk
```

## Configuração rápida

No `settings.py` do seu projeto Django:

```python
import tracking_sdk

# DSN do projeto (visível na página de Projetos do Error Tracker)
tracking_sdk.init(
    "https://a1b2c3d4-e5f6-7890-abcd-ef1234567890@localhost:8000/f0e1d2c3-b4a5-6789-0abc-def123456789"
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # ... outros middlewares ...
    "tracking_sdk.DjangoMiddleware",  # adicionar no final
]
```

Pronto. Qualquer exceção não tratada será capturada e enviada automaticamente.

## Configuração com .env

```python
import tracking_sdk
from decouple import config

tracking_sdk.init(
    dsn=config("ERROR_TRACKER_DSN"),
    ambiente="producao",
)
```

```env
ERROR_TRACKER_DSN=http://chave@host:porta/projeto_id
```

## Captura manual de exceções

```python
import tracking_sdk

try:
    resultado = operacao_arriscada()
except Exception:
    tracking_sdk.capturar_excecao()
```

Com contexto extra:

```python
try:
    processar_pedido(pedido_id)
except Exception as e:
    tracking_sdk.capturar_excecao(
        excecao=e,
        contexto_extra={
            "url": "/api/pedidos/42/",
            "metodo": "POST",
            "usuario": "admin@empresa.com",
        },
    )
```

## Opções do init()

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `dsn` | str | — | DSN do projeto (obrigatório) |
| `ambiente` | str | `""` | Nome do ambiente (producao, staging, dev) |
| `debug` | bool | `False` | Se True, imprime erros de envio no console |

## Formato do DSN

```
http://<chave_api_do_projeto>@<host>:<porta>/<projeto_id>
```

O DSN é gerado automaticamente ao criar um projeto no Error Tracker e fica visível na página de Projetos.

## Como funciona

1. `init()` cria um cliente global que parseia o DSN
2. O `DjangoMiddleware` intercepta exceções via `process_exception`
3. Extrai: mensagem, traceback completo, URL, método HTTP e usuário
4. Envia via POST em thread separada (daemon) — nunca bloqueia a resposta
5. Falhas de envio são silenciosas (exceto com `debug=True`)
6. O middleware retorna `None` — o Django continua seu fluxo normal

## Zero dependências

A SDK usa apenas a biblioteca padrão do Python (`urllib`, `threading`, `json`). Nenhuma dependência externa é necessária.
