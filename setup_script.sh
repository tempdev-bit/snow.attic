#!/bin/bash

echo "🔧 Starting Snow Attic setup..."

# Step 1: Ensure Python and venv module are installed
echo "📦 Installing Python and venv if needed..."
sudo apt update
sudo apt install -y python3 python3-venv

# Step 2: Create virtual environment
if [ ! -d "venv" ]; then
    echo "🧪 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Step 3: Activate virtual environment
source venv/bin/activate
echo "🟢 Virtual environment activated."

# Step 4: Install Python dependencies
if [ -f "req.txt" ]; then
    echo "📄 Installing dependencies from req.txt..."
    pip install --upgrade pip
    pip install -r req.txt
else
    echo "❌ req.txt not found!"
    deactivate
    exit 1
fi

# Step 5: Prompt for environment variables
read -p "👤 Enter username (SNOW_USERNAME): " snow_user
read -p "🔒 Enter password (SNOW_PASSWORD): " snow_pass
read -p "🔑 Enter NGROK_AUTHTOKEN (leave blank to skip): " ngrok_token

# Step 6: Write to .env file
echo "📄 Creating .env file..."
cat <<EOF > .env
SNOW_USERNAME=$snow_user
SNOW_PASSWORD=$snow_pass
NGROK_AUTHTOKEN=$ngrok_token
EOF

echo "✅ .env file created."

# Step 7: Ask user if they want to run the server now
read -p "🚀 Do you want to start the server now? (y/n): " start_now
if [[ "$start_now" =~ ^[Yy]$ ]]; then
    echo "🔄 Starting server..."
    python3 server.py
else
    echo "📦 Setup complete."
    echo "👉 To start later, run:"
    echo "   source venv/bin/activate"
    echo "   python3 server.py"
fi

# Cleanup
deactivate
