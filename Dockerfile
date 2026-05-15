FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential git curl libpq-dev libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libssl-dev libjpeg-dev libffi-dev \
    node-less npm ca-certificates wkhtmltopdf gosu && \
    rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Copy source
COPY --chown=odoo:odoo ./odoo /opt/odoo/odoo

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/odoo/odoo/requirements.txt

# Addons directory
RUN mkdir -p /mnt/extra-addons && chown odoo:odoo /mnt/extra-addons

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

WORKDIR /opt/odoo/odoo

EXPOSE 8069 8072

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "odoo-bin", "-c", "/etc/odoo/odoo.conf"]