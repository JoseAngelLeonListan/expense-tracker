FROM python:3.14-slim

# Sin archivos .pyc y con los logs al momento (sin buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero solo requirements.txt: si no cambia, Docker reutiliza la capa de pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No ejecutar la app como root dentro del contenedor
RUN useradd --create-home app
USER app

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
