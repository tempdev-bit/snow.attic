#!/bin/bash

echo "🔧 Starting Snow Attic setup..."

# Step 1: Check Python 3
echo "📦 Checking for Python 3..."
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found. Attempting to install..."
    if [ -f /etc/debian_version ]; then
        sudo apt update && sudo apt install -y python3
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y python3
    elif [ -f /etc/arch-release ]; then
        sudo pacman -Sy --noconfirm python
    else
        echo "⚠️ Unsupported distro. Please install Python 3 manually."
        exit 1
    fi
fi

# Step 2: Check for venv module
echo "🧪 Checking for Python venv module..."
if ! python3 -m venv --help &>/dev/null; then
    echo "⚙️ 'venv' module not found. Attempting to install..."
    if [ -f /etc/debian_version ]; then
        sudo apt install -y python3-venv
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y python3-venv || sudo dnf install -y python3-virtualenv
    elif [ -f /etc/arch-release ]; then
        sudo pacman -Sy --noconfirm python-virtualenv
    else
        echo "⚠️ Unsupported distro. Please install 'python3-venv' manually."
        exit 1
    fi
fi

# Step 3: Create virtual environment
if [ ! -d "venv" ]; then
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists."
fi

# Step 4: Activate virtual environment
source venv/bin/activate
echo "🟢 Virtual environment activated."

# Step 5: Install dependencies
if [ -f "req.txt" ]; then
    echo "📄 Installing Python dependencies from req.txt..."
    pip install --upgrade pip
    pip install -r req.txt
else
    echo "❌ req.txt not found!"
    deactivate
    exit 1
fi

# Step 6: Collect env vars
read -p "👤 Enter username (SNOW_USERNAME): " snow_user
read -p "🔒 Enter password (SNOW_PASSWORD): " snow_pass
read -p "🔑 Enter NGROK_AUTHTOKEN (leave blank to skip): " ngrok_token

# Step 7: Generate secret key
echo "🔐 Generating secure SECRET_KEY..."
secret_key=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Step 8: Write .env file
echo "📄 Writing .env file..."
cat <<EOF > .env
SNOW_USERNAME=$snow_user
SNOW_PASSWORD=$snow_pass
NGROK_AUTHTOKEN=$ngrok_token
SECRET_KEY=$secret_key
EOF

echo "✅ .env file created."

# Step 9: Optionally start server
read -p "🚀 Do you want to start the server now? (y/n): " start_now
if [[ "$start_now" =~ ^[Yy]$ ]]; then
    echo "🔄 Starting server..."
    python3 server.py
else
    echo "📦 Setup complete."
    echo "👉 To start later, run:"
    echo " source venv/bin/activate"
    echo " python3 server.py"
fi

# Deactivate env after setup
deactivate
