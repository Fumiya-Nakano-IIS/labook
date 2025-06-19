# labook
bookshelf management system

## dev commands

```
sudo systemctl kill labook.service 
source venv/bin/activate
python app.py
```
```
deactivate
sudo systemctl daemon-reload
sudo systemctl restart labook
sudo systemctl status labook
```
```
sudo nginx -t
sudo systemctl reload nginx
```