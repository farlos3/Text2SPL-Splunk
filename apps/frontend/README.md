# AI SPL Assistant Frontend

A modern, responsive chat interface for the AI SPL Assistant built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

### 🎨 Modern Design
- **Glass Morphism UI**: Beautiful backdrop blur effects and transparency
- **Dark/Light Mode**: Automatic theme switching based on system preferences
- **Gradient Backgrounds**: Subtle gradient overlays for visual depth
- **Smooth Animations**: Fade-in, slide-in, and micro-interactions throughout

### 💬 Chat Interface
- **Real-time Messaging**: Instant message display with typing indicators
- **SPL Code Highlighting**: Specialized formatting for Splunk queries
- **Copy Functionality**: One-click copying of SPL queries and responses
- **Message Timestamps**: Thai locale time formatting
- **Error Handling**: User-friendly error messages with retry options

### 📱 Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Sidebar Navigation**: Collapsible sidebar with chat history
- **Touch-Friendly**: Large touch targets for mobile devices
- **Accessible**: Keyboard navigation and screen reader support

## Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables
Create a `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
src/
├── app/
│   ├── globals.css          # Global styles and animations
│   ├── layout.tsx           # Root layout with fonts
│   └── page.tsx            # Main chat interface
├── components/
│   ├── MessageBubble.tsx    # Individual message display
│   ├── LoadingSpinner.tsx   # Loading spinner component
│   └── Skeleton.tsx         # Skeleton loading states
├── services/
│   └── api.ts              # API service layer
└── types/
    └── chat.ts             # TypeScript interfaces
```

## Key Features

### Enhanced UI/UX
- **Glass morphism effects** with backdrop blur
- **Smooth animations** and transitions
- **Responsive design** for all devices
- **Dark/Light mode** support
- **Improved typography** with Inter and JetBrains Mono fonts

### Chat Experience
- **Beautiful message bubbles** with gradient backgrounds
- **SPL code highlighting** with copy functionality
- **Typing indicators** with animated dots
- **Error handling** with user-friendly messages
- **Suggested prompts** for SPL queries

### Performance
- **Next.js 15** with App Router
- **Optimized fonts** with display swap
- **Lazy loading** components
- **Smooth scrolling** to new messages

## Design System

### Colors
- **Primary**: Blue gradient (#3b82f6 to #6366f1)
- **Success**: Green for SPL queries (#22c55e)
- **Background**: Gradient from slate to blue
- **Glass**: Semi-transparent overlays with backdrop blur

### Typography
- **Sans**: Inter font for UI text
- **Mono**: JetBrains Mono for code blocks

### Animations
- **Fade In**: 0.3s ease-out for new elements
- **Slide In**: 0.3s ease-out for side navigation
- **Pulse Soft**: 2s infinite for loading states

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
