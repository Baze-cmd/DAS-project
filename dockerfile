FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=3

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --default-timeout=100 numpy==2.2.1
RUN pip3 install --default-timeout=100 scipy pandas scikit-learn

COPY requirements.txt .
RUN pip3 install --default-timeout=100 -r requirements.txt

COPY . .
WORKDIR "/app/Домашна 2/tech prototype/react-app"
RUN npm install
RUN npm install -g serve
RUN npm run build
WORKDIR /app

EXPOSE 3000 8000
CMD /opt/venv/bin/python3 "/app/Домашна 2/tech prototype/DjangoProject/manage.py" runserver 0.0.0.0:8000 & \
    serve -s "/app/Домашна 2/tech prototype/react-app/build" -l 3000