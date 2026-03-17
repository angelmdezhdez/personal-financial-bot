#!/bin/bash

cd /home/ubuntu/personal-financial-bot

git add .

git commit -m "auto backup $(date '+%Y-%m-%d %H:%M:%S')" || exit 0

git push origin main
