Steps:

sudo cp maintenance.service /etc/systemd/system/maintenance.service

sudo chmod 644 /etc/systemd/system/maintenance.service

chmod +x /home/pi/maintenance/maintenance.py

sudo systemctl daemon-reload

sudo systemctl enable maintenance.service

sudo systemctl start maintenance.service