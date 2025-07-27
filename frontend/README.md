# ASU RAG Frontend

A modern Next.js frontend for the ASU RAG (Retrieval-Augmented Generation) system.

## Features

- 🎨 Modern, responsive UI with Tailwind CSS
- 🔍 Real-time query interface
- 📊 System statistics display
- 📚 Source attribution and links
- ⚡ Fast, client-side rendering
- 🔄 API proxy to Flask backend

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3001`

## Prerequisites

Make sure your Flask backend is running on `http://localhost:3000` before using the frontend.

## Development

- **Frontend**: Next.js 14 with TypeScript and Tailwind CSS
- **Backend**: Flask API (separate process)
- **Ports**: Frontend (3001), Backend (3000)

## API Routes

The frontend includes API routes that proxy requests to the Flask backend:

- `GET /api/stats` - Get system statistics
- `POST /api/query` - Submit a question to the RAG system

## Building for Production

```bash
npm run build
npm start
```
