#!/bin/bash
set -eu
mkdir -p /srv/northwind
printf 'Northwind application is reachable\n' > /srv/northwind/index.html
cat > /etc/systemd/system/northwind.service <<'UNIT'
[Unit]
Description=Northwind demo HTTP listener on TCP 8443 (not TLS)
After=network.target
[Service]
ExecStart=/usr/bin/python3 -m http.server 8443 --bind 0.0.0.0 --directory /srv/northwind
Restart=always
User=nobody
[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now northwind
