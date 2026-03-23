#!/bin/bash

# Trap to stop Tailscale when script exits
cleanup() {
    echo ""
    echo "🛑 Stopping Tailscale..."
    sudo tailscale down
    echo "✅ Tailscale stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "🔌 Starting Tailscale..."
sudo tailscale up

# Wait for Tailscale to connect
echo "⏳ Waiting for Tailscale to connect..."
sleep 3

# Get Tailscale IP
TAILSCALE_IP=$(tailscale ip -4)
echo "✅ Tailscale connected! IP: $TAILSCALE_IP"
echo "🚀 Starting FileShare server..."
echo "Access at: http://device:8000"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the Django server
python manage.py runserver $TAILSCALE_IP:8000