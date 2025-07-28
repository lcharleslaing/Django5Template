#!/bin/bash

# Django5Template Mobile Development Startup Script

echo "📱 Starting Django5Template for Mobile Testing..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Get the Mac's IP address
echo "🌐 Getting your Mac's IP address..."
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

if [ -z "$IP_ADDRESS" ]; then
    echo "❌ Could not determine IP address. Using localhost."
    IP_ADDRESS="127.0.0.1"
fi

echo "✅ Your Mac's IP address: $IP_ADDRESS"
echo "📱 Your iPhone can access the app at: http://$IP_ADDRESS:8000"
echo ""

# Check if dependencies are installed
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if Tailwind is built
if [ ! -f "theme/static/css/dist/styles.css" ]; then
    echo "🎨 Building Tailwind CSS..."
    python manage.py tailwind install
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start the development server on all interfaces
echo "🌐 Starting development server..."
echo "📱 Mobile URL: http://$IP_ADDRESS:8000"
echo "💻 Local URL: http://127.0.0.1:8000"
echo "📋 QR Code will be available on the homepage"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000 