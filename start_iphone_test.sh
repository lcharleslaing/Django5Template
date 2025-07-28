#!/bin/bash

echo "📱 Starting Django server for iPhone testing..."

# Activate virtual environment
source venv/bin/activate

# Get IP address
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo "✅ Your Mac's IP: $IP_ADDRESS"
echo "📱 iPhone URL: http://$IP_ADDRESS:8000"
echo "💻 Local URL: http://127.0.0.1:8000"
echo ""
echo "🔍 Make sure your iPhone and Mac are on the same WiFi network!"
echo "📋 QR code will be available on the homepage"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server on all interfaces
python manage.py runserver 0.0.0.0:8000 