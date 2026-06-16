# =============================================================================
#  Dockerfile multi-stage — Sistema de Automatización IA Hotel (Nivel 2)
#  Stage 1 (builder): instala dependencias en un venv aislado.
#  Stage 2 (runtime):  imagen final ligera, usuario no-root.
# =============================================================================

# ---------- Stage 1: builder -------------------------------------------------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# build-essential: necesario para compilar algunas ruedas (wheels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---------- Stage 2: runtime -------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/home/appuser/.hf_cache

# libgomp1: runtime de OpenMP requerido por torch/onnx. curl: para el healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

# Crear el caché de embeddings y dar propiedad a appuser. Clave: al montar un
# volumen nombrado nuevo sobre esta ruta, Docker hereda este dueño (uid 1000),
# evitando el "Permission denied" al escribir el modelo de HuggingFace.
RUN mkdir -p /home/appuser/.hf_cache \
    && chown -R appuser:appuser /app /home/appuser

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
