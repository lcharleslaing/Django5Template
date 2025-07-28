#!/bin/bash

# Django5Template Development Startup Script

echo "🚀 Starting Django5Template Development Environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

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

# Start the development server
echo "🌐 Starting development server at http://127.0.0.1:8000/"
echo "Press Ctrl+C to stop the server"
echo ""
python manage.py runserver 127.0.0.1:8000 