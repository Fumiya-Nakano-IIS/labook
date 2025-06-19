#!/usr/bin/env bash
set -e

# 仮想環境を有効化
source /home/pdlab/labook/venv/bin/activate

# 作業ディレクトリ移動
cd /home/pdlab/labook

# Gunicorn 起動
exec gunicorn \
  --workers 3 \
  --bind 127.0.0.1:5000 \
  app:app
