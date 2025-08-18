# Products API - Catálogo de Produtos

Uma API REST moderna e robusta para gerenciamento de catálogo de produtos, construída com **FastAPI** e seguindo os princípios da **Arquitetura Hexagonal** (Ports & Adapters).

## 📋 Pré-requisitos

**Único requisito: Docker instalado**

## 🚀 Como Rodar

Execute um único comando para iniciar toda a aplicação:

```bash
docker compose up --build
```

Pronto! A aplicação completa estará rodando com:
- **API**: http://localhost:8000
- **Dashboard de Monitoramento**: http://localhost:3000/dashboards (admin/admin)
- **Testes de Carga Automatizados**: A cada 10 minutos
- **Sistema de Alertas**: WhatsApp para timeouts >5s

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
- **📊 Observabilidade**: OpenTelemetry integrado
- **🌐 CORS**: Suporte completo para aplicações web
- **📝 Documentação**: Swagger/OpenAPI automático
- **🔒 Middleware**: Timeout, logging e tratamento de erros
- **📱 Sistema de Alertas**: WhatsApp para timeouts >5s
- **📊 Dashboard de Monitoramento**: Métricas em tempo real via Grafana
- **🧪 Testes Automatizados**: K6 rodando a cada 10 minutos

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

O sistema inclui testes automatizados de carga que rodam **a cada 10 minutos**:

- ✅ Requisições normais
- ❌ Testes de erro (404)
- ⏱️ Testes de timeout (5 segundos)

### Teste Manual com Delay

Use o header `X-Delay` para simular latência:

```bash
# Simula 5 segundos de delay (aciona alertas)
curl -H "X-Delay: 5" "http://localhost:8000/v1/products"
```

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
- **Testes Automatizados**: K6 a cada 10 minutos

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