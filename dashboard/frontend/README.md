# SMART FLOW v2 Dashboard Frontend

React-based web dashboard for real-time traffic monitoring and control.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm start
```

The dashboard will open at http://localhost:3000

## Configuration

Edit `.env` to configure backend connection:
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8080)
- `REACT_APP_WS_URL`: WebSocket URL (default: localhost:8080)

## Build

Create production build:
```bash
npm run build
```

## Features

- Real-time video feed with annotations
- Live metrics dashboard
- Traffic heatmap visualization
- Signal state indicators
- Manual signal override controls
- Alert notifications
- Historical data analysis
