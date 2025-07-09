#!/data/data/com.termux/files/usr/bin/bash

PORT=5001
APP_NAME="app.py"

echo "📦 Starting Flask app..."
nohup python $APP_NAME > flask.log 2>&1 &

sleep 2

echo "🌐 Starting secure Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:$PORT
