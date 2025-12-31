#!/bin/bash

# Startup script for SlokaCamp project
# This script starts both backend and frontend services

echo "🚀 Starting SlokaCamp Project..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

# Check if Yarn is installed
if ! command -v yarn &> /dev/null; then
    echo -e "${YELLOW}⚠️  Yarn is not installed. Installing Yarn...${NC}"
    npm install -g yarn
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}🐍 Starting Django Backend...${NC}"
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -d "venv/lib" ] || [ ! -f "venv/bin/pip" ]; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    # Run migrations
    echo -e "${BLUE}Running database migrations...${NC}"
    python manage.py migrate --noinput
    
    # Start server
    echo -e "${GREEN}✅ Backend starting on http://localhost:8000${NC}"
    python manage.py runserver
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting React Frontend...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing Node dependencies...${NC}"
        yarn install
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating .env file...${NC}"
        echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
    fi
    
    # Start server
    echo -e "${GREEN}✅ Frontend starting on http://localhost:3000${NC}"
    yarn start
}

# Check OS and open terminals accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo -e "${GREEN}Detected macOS${NC}"
    
    # Start backend in new terminal
    osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"'/backend && source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver"'
    
    # Wait a bit for backend to start
    sleep 3
    
    # Start frontend in new terminal
    osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"'/frontend && [ ! -f .env ] && echo \"REACT_APP_BACKEND_URL=http://localhost:8000\" > .env; [ ! -d node_modules ] && yarn install; yarn start"'
    
    echo -e "${GREEN}✅ Both services starting in separate terminal windows${NC}"
    echo -e "${BLUE}📝 Backend: http://localhost:8000${NC}"
    echo -e "${BLUE}📝 Frontend: http://localhost:3000${NC}"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo -e "${GREEN}Detected Linux${NC}"
    
    # Start backend in background
    cd backend
    start_backend &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit
    sleep 3
    
    # Start frontend in background
    cd frontend
    start_frontend &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Both services starting in background${NC}"
    echo -e "${BLUE}📝 Backend PID: $BACKEND_PID${NC}"
    echo -e "${BLUE}📝 Frontend PID: $FRONTEND_PID${NC}"
    echo -e "${BLUE}📝 Backend: http://localhost:8000${NC}"
    echo -e "${BLUE}📝 Frontend: http://localhost:3000${NC}"
    echo ""
    echo "To stop services, run: kill $BACKEND_PID $FRONTEND_PID"
    
else
    # Windows or other - manual instructions
    echo -e "${YELLOW}⚠️  Automatic startup not supported for this OS${NC}"
    echo -e "${BLUE}Please run manually:${NC}"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd backend"
    echo "  python manage.py runserver"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd frontend"
    echo "  yarn start"
fi

