FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    iputils-ping \
    nmap \
    net-tools \
    iproute2 \
    && pip install poetry

RUN setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)

WORKDIR /app

COPY pyproject.toml poetry.lock ./
 
RUN poetry install --no-root

COPY /src .
COPY .streamlit/ .streamlit/

EXPOSE 8501

ENTRYPOINT ["poetry", "run", "streamlit", "run", "networkscanner/site.py"]