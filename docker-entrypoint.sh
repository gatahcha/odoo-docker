#!/bin/bash
set -euo pipefail
mkdir -p /var/lib/odoo
chown -R odoo:odoo /var/lib/odoo
exec gosu odoo "$@"
