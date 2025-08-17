#!/usr/bin/env bash
set -e

PYTHON_VERSION=3.12.6

echo "🚀 Instalando dependências do sistema..."
brew update
brew install pyenv zlib bzip2 readline sqlite xz

echo "⚙️ Configurando shell..."
# Cria ~/.zshrc e ~/.zprofile se não existirem
touch ~/.zshrc
touch ~/.zprofile

# Garante que pyenv esteja no PATH
if ! grep -q 'pyenv init' ~/.zshrc; then
  echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
  echo 'eval "$(pyenv init -)"' >> ~/.zshrc
fi

if ! grep -q 'pyenv init' ~/.zprofile; then
  echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zprofile
  echo 'eval "$(pyenv init -)"' >> ~/.zprofile
fi

# Recarrega as configs
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

echo "🐍 Instalando Python $PYTHON_VERSION com pyenv..."
pyenv install -s $PYTHON_VERSION
pyenv local $PYTHON_VERSION

echo "📦 Criando virtualenv .venv..."
python -m venv .venv
source .venv/bin/activate

echo "⬆️ Atualizando pip e instalando pydantic..."
pip install --upgrade pip
pip install pydantic

echo "✅ Ambiente pronto! Ative com: source .venv/bin/activate"
