FROM python:3.10-slim

# Force HTTPS pour les dépôts Debian : sur certains réseaux (wifi d'école,
# box avec inspection de trafic), le HTTP simple est fortement ralenti ou
# bloqué, ce qui faisait traîner apt-get update sur plusieurs minutes.
RUN sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    || sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list

RUN apt-get update -o Acquire::Retries=5 && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 100 -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]