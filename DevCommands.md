# Dev Commands

debug
```
sudo systemctl kill labook.service 
source venv/bin/activate
python app.py
```

activate
```
sudo systemctl daemon-reload
sudo systemctl restart labook
sudo systemctl status labook
```

nginx reload
```
sudo nginx -t
sudo systemctl reload nginx
```