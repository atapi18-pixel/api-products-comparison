## 🌐 Frontend - Products UI

Interface web simples para consumir a Products API. Construída com **Vite + React** e servida em produção via **Nginx** (Dockerfile na pasta). Focada em demonstração rápida do catálogo e comportamento sob carga/falhas artificiais.

## 🚀 Principais Recursos
- Listagem de produtos paginada
- Integração direta com a API (`/v1/products`)
- Configurável via variável `VITE_API_BASE`
- Build leve e rápido (Vite)

## 📁 Estrutura Simplificada
```
frontend/
├── src/
│   ├── main.jsx        # Bootstrap React
│   ├── App.jsx         # Componente principal
│   └── App.css         # Estilos básicos
├── index.html          # Template HTML
├── vite.config.js      # Configuração Vite
├── Dockerfile          # Build + Nginx
└── nginx.conf          # Servindo assets estáticos
```

## ⚙️ Variáveis de Ambiente
Crie um arquivo `.env` na pasta `frontend/` (opcional):
```
VITE_API_BASE=http://localhost:8000
```
Caso não seja definido, pode ajustar diretamente no código ou usar padrão local.

## 🛠️ Scripts NPM
| Script | Descrição |
|--------|-----------|
| `npm install` | Instala dependências |
| `npm run dev` | Ambiente de desenvolvimento (hot reload) |
| `npm run build` | Gera build de produção em `dist/` |
| `npm run preview` | Serve o build localmente para inspeção |

## ▶️ Rodando em Desenvolvimento
```bash
cd frontend
npm install
npm run dev
# Acesse: http://localhost:5173 (porta padrão Vite)
```

## 🏗️ Build de Produção (Local)
```bash
cd frontend
npm install
npm run build
npm run preview
```

## 🐳 Build via Docker (usa Nginx)
```bash
docker build -t products-frontend ./frontend
docker run -p 8080:80 products-frontend
# Acesse: http://localhost:8080
```

## 🔄 Erros e Troubleshooting
| Sintoma | Possível causa | Ação |
|---------|----------------|------|
| 404 na API | Backend não iniciado ou porta errada | Verifique `docker compose ps` e `VITE_API_BASE` |
| CORS blocked | Variáveis de origem não liberadas | Checar configuração de CORS na API |
| Assets antigos | Cache ou diretório `dist` residual | Remova `dist/` e refaça `npm run build` |

## 📌 Boas Práticas Futuras
- Adicionar TypeScript
- Adotar testes (Vitest / Testing Library)
- Implementar roteamento (React Router)
- Criar componentes reutilizáveis (Design System leve)

---
_Última atualização: 18/08/2025_
