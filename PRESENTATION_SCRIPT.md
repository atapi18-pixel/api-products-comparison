# Roteiro de Apresentação - API de Produtos com Arquitetura Hexagonal

## 📋 Informações Gerais
- **Duração:** 15-20 minutos
- **Público-alvo:** Desenvolvedores, arquitetos de software, stakeholders técnicos
- **Objetivo:** Demonstrar implementação prática da arquitetura hexagonal com FastAPI

---

## 🎯 Estrutura da Apresentação

### 1. Introdução (2-3 minutos)
**Slide 1: Título**
- "API de Produtos com Arquitetura Hexagonal"
- "Implementação prática usando FastAPI e Python"

**Slide 2: Agenda**
- O que é Arquitetura Hexagonal?
- Benefícios e vantagens
- Demonstração da API
- Estrutura do projeto
- Próximos passos

**Script:**
> "Hoje vou apresentar uma implementação prática da arquitetura hexagonal, também conhecida como Ports & Adapters, usando FastAPI. Vamos ver como essa abordagem nos ajuda a criar aplicações mais testáveis, flexíveis e fáceis de manter."

### 2. Conceitos Fundamentais (4-5 minutos)

**Slide 3: O que é Arquitetura Hexagonal?**
- Criada por Alistair Cockburn
- Separação entre lógica de negócio e infraestrutura
- Inversão de dependências
- Testabilidade e flexibilidade

**Script:**
> "A arquitetura hexagonal foi criada para resolver um problema comum: como manter a lógica de negócio isolada das preocupações de infraestrutura? O hexágono representa nosso core domain, e as bordas são os adapters que conectam com o mundo externo."

**Slide 4: Componentes Principais**
- **Core/Domain:** Entidades e regras de negócio
- **Ports:** Interfaces que definem contratos
- **Adapters:** Implementações concretas
- **Services:** Orquestração da lógica de negócio

**Script:**
> "Temos quatro componentes principais: o Core contém nossas entidades e regras de negócio, os Ports definem contratos através de interfaces, os Adapters implementam esses contratos, e os Services orquestram a lógica de negócio."

### 3. Benefícios Técnicos e de Negócio (3-4 minutos)

**Slide 5: Benefícios Técnicos**
- ✅ **Testabilidade:** Fácil criação de mocks e testes unitários
- ✅ **Flexibilidade:** Troca de implementações sem afetar o core
- ✅ **Manutenibilidade:** Código organizado e bem estruturado
- ✅ **Reutilização:** Core independente de frameworks

**Slide 6: Benefícios de Negócio**
- 💰 **Redução de custos:** Menos bugs em produção
- ⚡ **Time-to-market:** Desenvolvimento mais rápido
- 🔄 **Adaptabilidade:** Fácil integração com novos sistemas
- 📈 **Escalabilidade:** Arquitetura preparada para crescimento

**Script:**
> "Os benefícios são tanto técnicos quanto de negócio. Tecnicamente, ganhamos testabilidade, flexibilidade e facilidade de manutenção. Do ponto de vista de negócio, reduzimos custos com bugs, aceleramos o desenvolvimento e facilitamos integrações futuras."

### 4. Demonstração Prática da API (5-6 minutos)

**Slide 7: Estrutura do Projeto**
```
app/
├── core/
│   ├── domain/          # Entidades e modelos
│   ├── ports/           # Interfaces (contratos)
│   └── services/        # Lógica de negócio
├── adapters/
│   ├── httphandlers/    # Controllers REST
│   └── repositories/    # Acesso a dados
└── main.py              # Configuração da aplicação
```

**Script:**
> "Vamos ver nossa estrutura. O core contém o domain com nossas entidades, os ports com as interfaces, e os services com a lógica de negócio. Os adapters implementam essas interfaces - temos HTTP handlers para REST e repositories para dados."

**Slide 8: Demonstração ao Vivo**
- Iniciar a aplicação
- Mostrar documentação Swagger
- Fazer requisições à API
- Demonstrar paginação e filtros

**Script para Demo:**
> "Vou iniciar nossa API e mostrar a documentação automática gerada pelo FastAPI. Vejam como temos endpoints bem documentados, com exemplos de request e response. Agora vou fazer algumas requisições para mostrar a paginação em funcionamento."

**Comandos para Demo:**
```bash
# Terminal 1 - Iniciar API
cd /Users/phtavares/Documents/workspace/example-products
source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Testar endpoints
curl "http://localhost:8000/v1/products?page=1&page_size=5"
curl "http://localhost:8000/v1/products?page=1&page_size=3&category=Laptops"
```

**Slide 9: Recursos da API**
- 📚 **Documentação automática** com Swagger/OpenAPI
- 🔍 **Paginação** com controle de página e tamanho
- 🎯 **Filtros** por categoria e outros critérios
- ⚡ **Performance testing** com header X-Delay
- 🌐 **CORS** configurado para desenvolvimento
- 📊 **Observabilidade** com OpenTelemetry

### 5. Arquitetura Detalhada (3-4 minutos)

**Slide 10: Fluxo de Dados**
```
HTTP Request → Handler → Service → Repository → Data Source
     ↓           ↓         ↓          ↓
  Adapter    Port/Core   Port     Adapter
```

**Script:**
> "O fluxo é simples: uma requisição HTTP chega no handler (adapter), que chama o service (core), que usa o repository (port) implementado por um adapter. Notem como o core nunca depende diretamente de infraestrutura."

**Slide 11: Injeção de Dependências**
- Uso do `dependency-injector`
- Container centralizado
- Wiring automático
- Facilita testes e manutenção

**Script:**
> "Usamos injeção de dependências para conectar tudo. O container gerencia as dependências automaticamente, facilitando testes e permitindo trocar implementações com facilidade."

### 6. Próximos Passos (2-3 minutos)

**Slide 12: Roadmap Técnico**
- 🗄️ **Banco de dados:** Implementar adapter para PostgreSQL
- 🔐 **Autenticação:** Adicionar JWT e controle de acesso
- ✅ **Testes:** Expandir cobertura de testes automatizados
- 🚀 **CI/CD:** Pipeline de deploy automatizado
- 📊 **Monitoramento:** Métricas e alertas em produção


**Script:**
> "Temos um roadmap ambicioso. Tecnicamente, queremos adicionar banco de dados, autenticação e mais testes. Funcionalmente, vamos expandir para CRUD completo, busca avançada e outras features empresariais."

### 7. Conclusão (1-2 minutos)

**Slide 14: Recapitulando os Benefícios**
- ✨ **Código limpo** e bem organizado
- 🧪 **Altamente testável** com mocks fáceis
- 🔄 **Flexível** para mudanças futuras
- 📈 **Escalável** para crescimento do negócio
- 🚀 **Produtivo** para o time de desenvolvimento

**Slide 15: Agradecimentos e Q&A**
- Obrigado pela atenção!
- Código disponível no repositório
- Perguntas e discussões

**Script Final:**
> "Em resumo, a arquitetura hexagonal nos proporcionou um código mais limpo, testável e flexível. Estamos preparados para escalar e evoluir conforme as necessidades do negócio. Agora estou aberto para perguntas!"

---

## 🎤 Dicas para Apresentação

### Preparação
- [ ] Testar a API antes da apresentação
- [ ] Preparar dados de exemplo interessantes
- [ ] Verificar se todos os endpoints funcionam
- [ ] Ter backup dos comandos curl

### Durante a Apresentação
- **Fale devagar** e com clareza
- **Mostre código** quando relevante
- **Interaja** com a audiência
- **Seja prático** - foque nos benefícios reais
- **Prepare-se** para perguntas técnicas

### Possíveis Perguntas
**Q: "Por que não usar uma arquitetura mais simples?"**
A: "Para projetos pequenos, pode ser overkill. Mas quando o projeto cresce, essa estrutura paga dividendos em manutenibilidade e testabilidade."

**Q: "Como isso se compara com Clean Architecture?"**
A: "São muito similares. Hexagonal é mais focada em ports/adapters, Clean Architecture tem mais camadas. Ambas buscam o mesmo objetivo: isolar o core."

**Q: "E a performance?"**
A: "A abstração adiciona overhead mínimo. Os benefícios em manutenibilidade superam qualquer impacto de performance, que é negligível."

---

## 📊 Métricas de Sucesso
- Audiência engajada com perguntas
- Feedback positivo sobre clareza
- Interesse em implementar em outros projetos
- Discussões técnicas produtivas

---

**Boa apresentação! 🚀**
