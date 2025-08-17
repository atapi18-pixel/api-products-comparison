FROM node:current-alpine3.22 AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund && npm audit fix --force
COPY frontend/ .
RUN npm run build

FROM python:3.12.11-slim

# set working directory
WORKDIR /app

# install python build dependencies required to compile some packages
# (keeps image reasonable while avoiding musl/rust toolchain failures)
COPY requirements.txt .
RUN apt-get update \
	 && apt-get install -y --no-install-recommends \
		 build-essential \
		 gcc \
		 libffi-dev \
		 libpq-dev \
		 libssl-dev \
	 && rm -rf /var/lib/apt/lists/* \
	 && pip install --no-cache-dir -r requirements.txt \
	 && apt-get purge -y --auto-remove build-essential gcc \
	 && rm -rf /var/lib/apt/lists/*

# copy backend application
COPY . .

# copy built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
