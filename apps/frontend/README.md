# 🎨 Text2SPL Frontend - AI-Powered Splunk Query Interface

A modern, responsive, and intelligent chat interface for the Text2SPL AI assistant. Built with Next.js 15, React 19, TypeScript, and Tailwind CSS to provide an exceptional user experience for cybersecurity professionals.

![Next.js](https://img.shields.io/badge/Next.js-15.5.2-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/React-19.1.0-61DAFB?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?style=flat-square&logo=typescript)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4?style=flat-square&logo=tailwind-css)

## 🌟 Features

### 🎨 Modern Design System
- **Glass Morphism UI**: Beautiful backdrop blur effects with transparency layers
- **Dynamic Theming**: Automatic dark/light mode based on system preferences
- **Gradient Backgrounds**: Sophisticated gradient overlays for visual depth
- **Micro-animations**: Smooth fade-in, slide-in, and hover interactions
- **Premium Typography**: Inter font for UI text, JetBrains Mono for code
- **Color Psychology**: Blue/purple gradients for trust, green accents for success

### 💬 Intelligent Chat Interface
- **Real-time Communication**: Instant message exchange with WebSocket-like experience
- **SPL Syntax Highlighting**: Specialized formatting for Splunk query language
- **Smart Copy Functionality**: One-click copying of SPL queries and responses
- **Contextual Timestamps**: Localized time formatting with relative timestamps
- **Advanced Error Handling**: User-friendly error messages with retry mechanisms
- **Query Suggestions**: Intelligent prompts for common security use cases

### 🛡️ Security-Focused UX
- **Threat Hunter Interface**: Designed specifically for SOC analysts and security teams
- **Query Preview**: Live preview of SPL queries before execution
- **Company Context Display**: Clear indication of target organization/environment
- **Confidence Indicators**: Visual confidence scores for AI-generated queries
- **Query Validation**: Real-time syntax validation and error highlighting

### 📱 Responsive & Accessible Design
- **Mobile-First Architecture**: Optimized for tablets and mobile devices
- **Touch-Optimized Controls**: Large touch targets and gesture support
- **Keyboard Navigation**: Full keyboard accessibility with proper focus management
- **Screen Reader Support**: ARIA labels and semantic HTML structure
- **Cross-Browser Compatibility**: Tested on Chrome, Firefox, Safari, and Edge

### ⚡ Performance & Optimization
- **Next.js 15 App Router**: Latest routing capabilities with server components
- **React 19 Features**: Concurrent rendering and automatic batching
- **Optimized Loading**: Lazy loading components and code splitting
- **Font Optimization**: Display swap for improved loading performance
- **Smooth Animations**: Hardware-accelerated CSS animations

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** (recommended: 20 LTS)
- **npm 9+** or **yarn 1.22+** or **pnpm 8+**
- **Modern browser** with ES2022 support

### 🐳 Docker Setup (Recommended)
```bash
# From project root directory
cd "f:/University/AISecOps/KBTG Cyber Security/INTERN/Web-Dev"

# Start frontend service
docker compose -f docker-compose.dev.yml up frontend

# Or start all services
docker compose -f docker-compose.dev.yml up --build
```

### 💻 Local Development
```bash
# Navigate to frontend directory
cd apps/frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
# or
yarn dev
# or
pnpm dev
```

### 🔧 Available Scripts
```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Lint code with ESLint
npm run lint

# Type checking
npm run type-check

# Format code with Prettier
npm run format
```

### 🌐 Access Points
- **Development**: http://localhost:3000
- **Production**: Configured in deployment environment
- **API Backend**: http://localhost:8000 (ensure backend is running)

## 🏗️ Project Architecture

```
frontend/
├── src/
│   ├── app/                     # Next.js 15 App Router
│   │   ├── globals.css          # Global styles and CSS variables
│   │   ├── layout.tsx           # Root layout with providers
│   │   ├── page.tsx            # Main chat interface page
│   │   └── favicon.ico         # Application icon
│   ├── components/              # Reusable React Components
│   │   ├── ChatHeader.tsx       # Chat interface header
│   │   ├── ChatInput.tsx        # Message input component
│   │   ├── MessageBubble.tsx    # Individual message display
│   │   ├── LoadingSpinner.tsx   # Loading spinner component
│   │   ├── Skeleton.tsx         # Skeleton loading states
│   │   └── TypingIndicator.tsx  # Typing animation component
│   ├── services/                # API Integration Layer
│   │   └── api.ts              # API service with error handling
│   └── types/                   # TypeScript Definitions
│       └── chat.ts             # Chat-related type definitions
├── public/                      # Static Assets
│   ├── next.svg                # Next.js logo
│   ├── vercel.svg              # Vercel logo
│   └── [other-assets]          # Icons and images
├── package.json                 # Dependencies and scripts
├── next.config.ts              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── tsconfig.json               # TypeScript configuration
├── eslint.config.mjs           # ESLint configuration
└── README.md                   # This file
```

## ⚙️ Environment Configuration

### Required Variables
Create a `.env.local` file in the frontend directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Text2SPL Assistant
NEXT_PUBLIC_APP_VERSION=1.0.0

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true

# UI Configuration
NEXT_PUBLIC_DEFAULT_THEME=system
NEXT_PUBLIC_ANIMATION_DURATION=300
```

### Optional Configuration
```bash
# Advanced Settings
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_MAX_MESSAGE_LENGTH=2000
NEXT_PUBLIC_ENABLE_VOICE_INPUT=false

# Development Settings
NEXT_PUBLIC_MOCK_API=false
NEXT_PUBLIC_SHOW_RESPONSE_TIME=true
```

### Environment Template
```bash
# Copy the example file
cp .env.local.example .env.local

# Edit with your specific values
nano .env.local
```

## 🎯 Key Components & Features

### 🧩 Core Components

#### `ChatHeader.tsx` - Interface Header
- **Company Context Display**: Shows current organization context
- **Status Indicators**: Real-time connection and processing status
- **Theme Toggle**: Manual dark/light mode switching
- **Settings Access**: Quick access to configuration options

#### `ChatInput.tsx` - Message Input System
- **Smart Input Validation**: Real-time validation of user queries
- **Auto-complete Suggestions**: Context-aware query suggestions
- **Multi-line Support**: Handles complex, multi-line queries
- **Voice Input Integration**: (Optional) Speech-to-text functionality
- **Character Counter**: Visual indication of message length limits

#### `MessageBubble.tsx` - Message Display
- **Dynamic Styling**: Different styles for user vs. AI messages
- **SPL Code Blocks**: Syntax-highlighted Splunk queries with copy functionality
- **Metadata Display**: Shows confidence scores, processing time, and query enhancement info
- **Interactive Elements**: Clickable company names, expandable details
- **Message Actions**: Copy, share, and feedback options

#### `TypingIndicator.tsx` - AI Processing Feedback
- **Animated Dots**: Smooth, professional typing animation
- **Processing Stages**: Different indicators for different pipeline stages
- **Estimated Time**: Shows expected response time based on query complexity

#### `LoadingSpinner.tsx` & `Skeleton.tsx` - Loading States
- **Progressive Loading**: Different loading states for different content types
- **Skeleton Screens**: Maintain layout during content loading
- **Smooth Transitions**: Seamless transitions from loading to content

### 🎨 Design System Implementation

#### Color Palette
```css
:root {
  /* Primary Colors */
  --primary-blue: #3b82f6;
  --primary-indigo: #6366f1;
  --primary-purple: #8b5cf6;
  
  /* Success/SPL Colors */
  --success-green: #22c55e;
  --success-emerald: #10b981;
  
  /* Background Gradients */
  --bg-gradient-start: #0f172a;
  --bg-gradient-end: #1e3a8a;
  
  /* Glass Morphism */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-shadow: rgba(0, 0, 0, 0.1);
}
```

#### Typography System
- **Primary Font**: Inter (sans-serif) - Clean, modern UI text
- **Monospace Font**: JetBrains Mono - Code blocks and technical content
- **Font Weights**: 300 (light), 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Font Sizes**: Responsive scale from 12px to 48px

#### Animation Framework
```css
/* Standard Transitions */
.transition-default { transition: all 0.3s ease-out; }
.transition-fast { transition: all 0.15s ease-out; }
.transition-slow { transition: all 0.5s ease-out; }

/* Custom Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.5); }
  50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8); }
}
```

### 🔧 Technical Features

#### State Management
- **React 19 Features**: Uses latest React capabilities including concurrent features
- **Local State**: Component-level state for UI interactions
- **Context API**: Global state for theme, user preferences, and chat history
- **URL State**: Query parameters for shareable chat states

#### API Integration (`services/api.ts`)
```typescript
interface ChatAPI {
  sendMessage(content: string): Promise<ChatResponse>;
  getHistory(): Promise<ChatMessage[]>;
  validateSPL(query: string): Promise<ValidationResult>;
  getPipelineStatus(): Promise<PipelineStatus>;
}
```

#### Error Handling
- **Network Errors**: Automatic retry with exponential backoff
- **API Errors**: User-friendly error messages with specific guidance
- **Validation Errors**: Real-time input validation with helpful suggestions
- **Graceful Degradation**: Fallback functionality when features are unavailable

#### Performance Optimizations
- **Code Splitting**: Dynamic imports for non-critical components
- **Image Optimization**: Next.js automatic image optimization
- **Font Loading**: Optimized web font loading with display swap
- **Lazy Loading**: Components loaded only when needed
- **Memoization**: React.memo and useMemo for expensive operations

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

## 📱 Browser Support & Compatibility

### Supported Browsers
- **Chrome** 90+ (Recommended)
- **Firefox** 88+
- **Safari** 14.1+
- **Edge** 90+

### Mobile Compatibility
- **iOS Safari** 14.1+
- **Chrome Mobile** 90+
- **Samsung Internet** 14+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features require modern browser APIs
- Graceful degradation for older browsers

## 📄 Scripts & Commands

### Development Scripts
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Type checking
npm run type-check

# Format code
npm run format

# Analyze bundle
npm run analyze
```

### Quality Assurance
```bash
# Run all quality checks
npm run qa

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y
```

## 🤝 Contributing Guidelines

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Install** dependencies: `npm ci`
4. **Start** development server: `npm run dev`
5. **Make** your changes following our coding standards
6. **Test** your changes: `npm run qa`
7. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
8. **Push** to branch: `git push origin feature/amazing-feature`
9. **Create** a Pull Request

### Code Standards
- **TypeScript**: Strict mode enabled, full type coverage required
- **ESLint**: Follows Next.js recommended rules + custom security rules
- **Prettier**: Consistent code formatting across the project
- **Naming Conventions**: PascalCase for components, camelCase for functions/variables
- **File Structure**: Logical organization with clear separation of concerns

### Component Development
```typescript
// Component Template
import React from 'react';
import { ComponentProps } from './ComponentName.types';

/**
 * ComponentName - Brief description
 * @param props - Component properties
 * @returns React component
 */
export const ComponentName: React.FC<ComponentProps> = ({ 
  prop1, 
  prop2,
  ...props 
}) => {
  return (
    <div className="component-name" {...props}>
      {/* Component content */}
    </div>
  );
};

export default ComponentName;
```

### Testing Guidelines
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows
- **Accessibility Tests**: Ensure WCAG 2.1 AA compliance
- **Visual Regression**: Prevent unintended UI changes

## 🔗 Related Documentation

### Project Documentation
- [Main Project README](../../README.md) - Complete project overview
- [Backend API Documentation](../backend/README.md) - API endpoints and usage
- [Pipeline Technical Details](../backend/PIPELINE_README.md) - AI processing pipeline
- [Docker Development Guide](../../README.docker.md) - Container setup and usage

### External Resources
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev/blog/2024/04/25/react-19)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

## 📞 Support & Community

### Getting Help
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Ask questions and share ideas on GitHub Discussions
- **Documentation**: Check our comprehensive docs for detailed guides
- **Examples**: Explore example implementations in the `/examples` directory

### Community Guidelines
- Be respectful and inclusive
- Provide detailed information when reporting issues
- Follow our code of conduct
- Contribute to documentation improvements
- Help others in discussions and issues

---

**🚀 Ready to build amazing SPL query interfaces? Start with `npm run dev` and explore the possibilities!**
