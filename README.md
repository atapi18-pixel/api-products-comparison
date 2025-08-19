# Products API - Catálogo de Produtos

Uma API REST moderna e robusta para gerenciamento de catálogo de produtos, construída com **FastAPI** e seguindo os princípios da **Arquitetura Hexagonal** (Ports & Adapters).

## 🔮 Auto-healing preditivo

O projeto inclui um mecanismo de **mitigação preditiva automática** que detecta tendência de violação de SLO (latência P95 ou taxa de erro) e executa uma ação de recuperação antes do impacto.  
➡ Documentação completa: [PREDICTIVE_SELF_HEALING.md](./PREDICTIVE_SELF_HEALING.md)

Principais recursos no dashboard `predictive-selfheal`:

Para uma demonstração rápida: injete latência com `/admin/fault` e aguarde o ciclo preditivo acionar `/admin/mitigate` automaticamente.

## � Pré-requisitos

**Único requisito: Docker instalado**

## 🚀 Como Rodar

Execute um único comando para iniciar toda a aplicação:

```bash
docker compose up -d --build
```

Pronto! A aplicação completa estará rodando com:
- **FRONTEND**: http://localhost:8000
 <br>

- **Dashboard de Monitoramento**:
  ***aguarde 3 minutos para popular os dados***
 http://localhost:3000/dashboards (admin/admin)
<br>
- **Quick Tips**:
  - Acesse os dashboards. Tenha em mente os tempos de refresh e evaluation do grafana. Aguarda 30 segundos entre as ações.
  - Observe a latencia inicial.
  - Mitigue manualmente e observe a latencia zerar.
  - Depois gere latencia através do  `curl -X POST -H 'x-admin-token: secret'   'http://localhost:8000/admin/fault?mode=latency&inc=110'`
  - Observe a nova latencia.
  - Vá subindo a cada 30/40 segundos através do curl. Se preferir aumente o tempo ingerido no comando.
  - Observe as linhas de latencia, forecast e SLO.
  - Latencias acima de 1seg devem ser suficientes para o modelo atuar e mitigar automaticamente.

<br>

- **Testes de Carga Automatizados**: A cada 30 minutos
- **Sistema de Alertas**: WhatsApp para timeouts >5s ***(para gerar o alerta, recomendo usar o postman e alterar o X-Delay na collection)***

## 📊 Relatório do Sonar
- **Link do projeto**: https://sonarcloud.io/summary/overall?id=atapi18-pixel_api-products-comparison&branch=main

## 🏗️ Arquitetura

### Arquitetura Hexagonal (Ports & Adapters)

Este projeto implementa a **Arquitetura Hexagonal**, também conhecida como **Ports & Adapters**, criada por Alistair Cockburn. Esta arquitetura promove:

```
┌─────────────────────────────────────────────────────────┐
│                    Adapters (External)                  │
├─────────────────────────────────────────────────────────┤
│  HTTP Handlers  │  Repositories  │  External Services   │
├─────────────────────────────────────────────────────────┤
│                     Ports (Interfaces)                  │
├─────────────────────────────────────────────────────────┤
│                   Core Domain (Business Logic)          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   Models    │  │  Services   │  │ Repositories│      │
│  │             │  │             │  │ Interfaces  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Estrutura do Projeto

```
app/
├── core/                          # Domínio Central
│   ├── domain/                    # Modelos de Domínio
│   │   └── product.py            # Entidade Product
│   ├── ports/                     # Interfaces (Contratos)
│   │   ├── services.py           # Interface do Serviço
│   │   └── repositories.py       # Interface do Repositório
│   └── services/                  # Implementação dos Serviços
│       └── product_service.py    # Lógica de Negócio
├── adapters/                      # Adaptadores Externos
│   ├── httphandlers/             # Controladores HTTP
│   │   ├── product_handler.py    # Endpoints da API
│   │   └── product_dto.py        # DTOs de Resposta
│   └── repositories/             # Implementações de Repositórios
│       └── inmem/                # Repositório em Memória
│           └── product_repository.py
├── config.py                     # Configuração de DI
├── main.py                       # Aplicação FastAPI
├── middlewares.py                # Middlewares Customizados
├── logger.py                     # Configuração de Logs
└── errors.py                     # Tratamento de Erros
```

## ✨ Benefícios da Arquitetura Hexagonal

### 1. **Separação de Responsabilidades**
- **Core Domain**: Contém apenas lógica de negócio pura
- **Ports**: Definem contratos claros entre camadas
- **Adapters**: Implementam detalhes técnicos específicos

### 2. **Testabilidade**
- Fácil criação de mocks e stubs para testes unitários
- Testes de domínio independentes de infraestrutura
- Cobertura de testes mais eficiente

### 3. **Flexibilidade e Manutenibilidade**
- Troca de implementações sem afetar o core
- Adição de novos adapters sem modificar o domínio
- Evolução independente das camadas

### 4. **Inversão de Dependências**
- Core não depende de detalhes de implementação
- Adapters dependem do core, não o contrário
- Facilita a injeção de dependências

### 5. **Escalabilidade**
- Fácil adição de novos endpoints
- Múltiplas implementações de repositórios
- Suporte a diferentes protocolos de comunicação

## 🚀 Funcionalidades

- **📦 Catálogo Completo**: 27 produtos em 4 categorias
- **🔍 Paginação Eficiente**: Suporte a paginação customizável
- **📱 Múltiplas Categorias**: Laptops, Smartphones, Headphones, TVs
- **⚡ Performance Testing**: Header X-Delay para testes de carga
 - **⚡ Performance Testing**: Header X-Delay para testes de carga
 - **� Fault Injection / Auto-Healing**: Endpoints `/admin/fault` (latency & leak) + `/admin/mitigate`
- **�📊 Observabilidade**: OpenTelemetry integrado
- **🌐 CORS**: Suporte completo para aplicações web
- **📝 Documentação**: Swagger/OpenAPI automático
- **🔒 Middleware**: Timeout, logging e tratamento de erros
- **📱 Sistema de Alertas**: WhatsApp para timeouts >5s
- **📊 Dashboard de Monitoramento**: Métricas em tempo real via Grafana
- **🧪 Testes Automatizados**: K6 rodando a cada 30 minutos

## 🛠️ Tecnologias Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web moderno e rápido
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Validação de dados e serialização
- **[Dependency Injector](https://python-dependency-injector.ets-labs.org/)**: Injeção de dependências
- **[OpenTelemetry](https://opentelemetry.io/)**: Observabilidade e rastreamento
- **[Uvicorn](https://www.uvicorn.org/)**: Servidor ASGI de alta performance
- **[Prometheus](https://prometheus.io/)**: Coleta de métricas
- **[Grafana](https://grafana.com/)**: Visualização e dashboards
- **[AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager/)**: Sistema de alertas
- **[K6](https://k6.io/)**: Testes de performance automatizados

## 📚 Documentação da API

### Swagger UI
Acesse a documentação interativa em: `http://localhost:8000/docs`

### ReDoc
Documentação alternativa em: `http://localhost:8000/redoc`

## 📮 Collection do Postman

Para avaliadores que desejam testar manualmente, incluímos uma **collection completa do Postman**:

📁 **Localização**: `tests/postman/Products API v1.postman_collection.json`

### Como Importar:
1. Abra o Postman
2. Clique em **Import**
3. Selecione o arquivo `tests/postman/Products API v1.postman_collection.json`
4. A collection será importada com todas as variáveis configuradas

### O que está incluído:
- ✅ **Todos os endpoints** da API
- ✅ **Variáveis configuradas** (localhost:8000)
- ✅ **Testes de paginação** (diferentes page_size)
- ✅ **Teste de timeout** (X-Delay: 5s para acionar alertas)
- ✅ **Testes de erro** (endpoints inválidos)

### Testes Especiais:
- **🚨 Timeout Test**: Usa header `X-Delay: 5` para simular timeout e acionar alertas WhatsApp
- **❌ Error Test**: Testa endpoint inexistente para validar tratamento de erros
- **📄 Pagination Tests**: Diferentes valores de `page_size` e `page`

## 📊 Dashboard de Monitoramento

Acesse o dashboard completo em: `http://localhost:3000/dashboards`
- **Usuário**: admin
- **Senha**: admin

O dashboard inclui:
- 📈 Métricas de performance da API
- 🔍 Top produtos e categorias mais acessados
- ⚡ Tempo de resposta médio
- 🚨 Alertas em tempo real
- 📊 Volume de requisições

## 🧪 Sistema de Alertas

O sistema monitora automaticamente timeouts >5 segundos e envia alertas via **WhatsApp**.

## 🔌 Endpoints

### GET /v1/products
Retorna uma lista paginada de produtos.

**Parâmetros:**
- `page` (query, opcional): Número da página (padrão: 1)
- `page_size` (query, opcional): Itens por página (padrão: 10, máximo: 100)
- `X-Delay` (header, opcional): Delay em segundos para testes de performance

**Exemplo de Requisição:**
```bash
curl "http://localhost:8000/v1/products?page=1&page_size=5"
```

**Exemplo de Resposta:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "MacBook Pro 14\" M3",
      "category": "Laptops",
      "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
      "description": "Apple MacBook Pro with M3 chip, 14-inch Liquid Retina XDR display",
      "price": 1999.99,
      "rating": 4.8,
      "specifications": {
        "processor": "Apple M3 8-core CPU",
        "memory": "8GB Unified Memory",
        "storage": "512GB SSD",
        "display": "14.2-inch Liquid Retina XDR",
        "graphics": "10-core GPU",
        "battery_life": "Up to 22 hours",
        "weight": "1.55 kg",
        "ports": "3x Thunderbolt 4, HDMI, SD card slot"
      },
      "availability": "In Stock",
      "brand": "Apple"
    }
  ],
  "total": 27,
  "page": 1,
  "page_size": 5
}
```

## 📦 Categorias de Produtos

### 💻 Laptops
- MacBook Pro, Dell XPS, ThinkPad, Alienware, Razer Blade, MSI Creator
- Especificações: Processador, Memória, Armazenamento, Display, Gráficos

### 📱 Smartphones
- iPhone 15 Series, Samsung Galaxy S24, Google Pixel 8, OnePlus, Xiaomi
- Especificações: Processador, Câmera, Bateria, Conectividade

### 🎧 Headphones
- Sony WH-1000XM5, Bose QuietComfort, Apple AirPods Max
- Especificações: Drivers, Cancelamento de Ruído, Bateria, Conectividade

### 📺 TVs
- LG OLED, Samsung QLED, Sony BRAVIA
- Especificações: Tamanho, Resolução, HDR, Plataforma Smart

## 🧪 Testes de Performance

O sistema inclui testes automatizados de carga que rodam **a cada 30 minutos**:

- ✅ Requisições normais
- ❌ Testes de erro (404)
- ⏱️ Testes de timeout (5 segundos)

### Teste Manual com Delay

Use o header `X-Delay` para simular latência:

```bash
# Simula 5 segundos de delay (aciona alertas)
curl -H "X-Delay: 5" "http://localhost:8000/v1/products"
```

### Injeção de Latência Artificial (Fault Injection)

Além do `X-Delay`, é possível injetar **latência artificial global** (em milissegundos) via endpoint administrativo. Essa latência é **somada** ao valor enviado no header `X-Delay` dentro da camada de repositório (não existe mais middleware separado para isso, evitando duplicação).

Endpoint:
```
POST /admin/fault?mode=latency&inc=<ms>
```
Parâmetros:
- `mode=latency` → indica que estamos ajustando latência artificial
- `inc` → incremento (ou decremento, se negativo) em milissegundos (acumulativo, limitado entre 0 e 5000ms)

Mitigação / Reset manual:
```
POST /admin/mitigate
```

Header de autenticação (default):
```
x-admin-token: secret
```

Exemplos:
```bash
# Injeta +150ms de latência global
curl -X POST "http://localhost:8000/admin/fault?mode=latency&inc=150" -H "x-admin-token: secret"

# Faz requisição com X-Delay de 1s (resultado ~1.15s incluindo sobrecarga/tolerância)
time curl -H "X-Delay: 1" "http://localhost:8000/v1/products?page=1&page_size=5"

# Aumenta mais 200ms (total agora 350ms)
curl -X POST "http://localhost:8000/admin/fault?mode=latency&inc=200" -H "x-admin-token: secret"

# Reseta (auto-healing manual)
curl -X POST "http://localhost:8000/admin/mitigate" -H "x-admin-token: secret"
```

Observações:
- A latência artificial é refletida na métrica `artificial_latency_injected_ms`.
- O endpoint `/health` expõe `artificial_latency_ms` para inspeção rápida.
- O reset automático pode ser disparado pelo mecanismo preditivo (ver documentação de self-healing).

### Memory Leak Sintético
Também é possível simular acúmulo de memória:
```
POST /admin/fault?mode=leak&kb=256
```
Isto aloca ~256KB e incrementa a métrica `memory_leak_chunks`. O reset (liberação) ocorre via `/admin/mitigate`.

## 🔧 Configuração

### Injeção de Dependências
O projeto usa `dependency-injector` para gerenciar dependências:

```python
# config.py
class Container(containers.DeclarativeContainer):
    product_repository = providers.Singleton(InMemoryProductRepository)
    product_service = providers.Factory(ProductServiceImpl, repo=product_repository)
```

### Middleware
- **CORS**: Configurado para desenvolvimento local e produção
- **Timeout**: Timeout padrão de 5 segundos
- **Logging**: Logs estruturados com contexto de requisição
- **OpenTelemetry**: Rastreamento distribuído
 - (REMOVIDO) Middleware de latência artificial global: agora a composição de latência (`X-Delay` + injetada) acontece diretamente no repositório para evitar duplicidade e facilitar teste.

### Alertas WhatsApp
Para configurar os alertas via WhatsApp, edite as variáveis no `docker-compose.yml`:
```yaml
TWILIO_ACCOUNT_SID: your_account_sid
TWILIO_AUTH_TOKEN: your_auth_token
TWILIO_WHATSAPP_FROM: whatsapp:+14155238886
WHATSAPP_TO: whatsapp:+5511999999999
```

## 🏃‍♂️ Desenvolvimento

### Adicionando Novos Endpoints
1. Crie o handler em `adapters/httphandlers/`
2. Defina DTOs necessários
3. Implemente a lógica no serviço
4. Configure as rotas no router

### Adicionando Novos Repositórios
1. Implemente a interface `ProductRepository`
2. Configure no container de DI
3. Injete no serviço correspondente

## 📊 Monitoramento

A aplicação inclui monitoramento completo:
- **OpenTelemetry**: Traces automáticos
- **Logs Estruturados**: JSON com contexto
- **Health Checks**: Endpoints de status
- **Métricas**: Performance e uso
- **Dashboard Grafana**: Visualização em tempo real
- **Alertas WhatsApp**: Notificações de timeout
- **Testes Automatizados**: K6 a cada 30 minutos

## 🤝 Contribuição

1. Fork o projeto https://github.com/atapi18-pixel/api-products-comparison
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para dúvidas ou suporte:
- Email: jorgegabrielpereira@hotmail.com
- Documentação: `http://localhost:8000/docs`
- Issues: GitHub Issues

---

**Desenvolvido com ❤️ usando Arquitetura Hexagonal e FastAPI**