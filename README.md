# 🛡️ Text2SPL - AI-Powered Splunk Query Assistant

[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> An intelligent conversational AI assistant that transforms natural language security questions into precise Splunk SPL (Search Processing Language) queries. Built for cybersecurity professionals and SOC analysts to streamline threat hunting and log analysis.

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (Recommended)
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/farlos3/Text2SPL-Splunk-.git
   cd Text2SPL-Splunk-
   ```

2. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file with your API keys
   nano .env
   ```

3. **Start Development Environment**
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

4. **Access the Application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

### 💻 Local Development

#### Backend Setup
```bash
cd apps/backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd apps/frontend
npm install
npm run dev
```

## Project Architecture

```
Text2SPL-Splunk-/
├── 📁 apps/
│   ├── 📁 backend/              # FastAPI Backend
│   │   ├── 📁 app/
│   │   │   ├── 📁 core/         # Configuration & Settings
│   │   │   ├── 📁 models/       # Pydantic Data Models
│   │   │   ├── 📁 routers/      # API Route Handlers
│   │   │   ├── 📁 services/     # Business Logic Layer
│   │   │   └── 📄 main.py       # FastAPI Application Entry
│   │   ├── 📁 data/             # Training Data & Examples
│   │   │   ├── 📄 qa_pairs-normal.json
│   │   │   ├── 📄 field-mappings.json
│   │   │   └── 📄 index-sourcetype.json
│   │   └── 📄 requirements.txt  # Python Dependencies
│   └── 📁 frontend/             # Next.js Frontend
│       ├── 📁 src/
│       │   ├── 📁 app/          # App Router Pages
│       │   ├── 📁 components/   # React Components
│       │   ├── 📁 services/     # API Integration
│       │   └── 📁 types/        # TypeScript Definitions
│       └── 📄 package.json      # Node.js Dependencies
├── 📁 docker/                   # Docker Configuration
│   ├── 📄 backend.Dockerfile
│   └── 📄 frontend.Dockerfile
├── 📄 docker-compose.dev.yml    # Development Environment
├── 📄 docker-compose.yml        # Production Environment
└── 📄 README.md                 # This File
```

## 📊 Example Queries

### Authentication Analysis
**Input**: "For TechCorp, show all failed logins in the last 24 hours"

**Generated SPL**:
```spl
index=TechCorp_win sourcetype=WinEventLog earliest=-24h
| eval user=coalesce(User_Name, user, account, dest_user)
| eval src=coalesce(src_ip, src, Source_Network_Address, host)
| eval action=case(
    EventCode=4625, "failure",
    match(_raw,"Failed password|authentication failure|logon failure"), "failure",
    true(), "other"
  )
| search action=failure AND isnotnull(user) AND isnotnull(src)
| bin _time span=1h
| stats count by _time user src
| sort - _time
```

### Network Security
**Input**: "Find suspicious PowerShell commands with encoded parameters"

**Generated SPL**:
```spl
index=* sourcetype=WinEventLog (EventCode=4104 OR EventCode=4103) earliest=-24h
| regex _raw="(?i)(encodedcommand|-enc|-e|invoke-expression|iex)"
| eval command=coalesce(CommandLine, command, process_command)
| eval user=coalesce(User_Name, user, account)
| stats count by command user host
| sort - count
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Groq AI Configuration
GROQ_API_KEY=your_groq_api_key_here

# Application Settings
ENVIRONMENT=development
DEBUG=true
FRONTEND_ORIGIN=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

#### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Text2SPL Assistant
```

## 🧪 Testing

### Backend Testing
```bash
cd apps/backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd apps/frontend
npm test
npm run test:e2e
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👥 Team

- **Development Team**: KBTG Cyber Security Internship Program
- **Maintainer**: [@farlos3](https://github.com/farlos3)

## 🙏 Acknowledgments

- **Groq AI** for fast LLM inference
- **Splunk** for the SPL query language
- **KBTG** for the internship opportunity

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/farlos3/Text2SPL-Splunk-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/farlos3/Text2SPL-Splunk-/discussions)

---

<div align="center">
  <p>Made with ❤️ for the Cybersecurity Community</p>
  <p>
    <a href="#top">⬆️ Back to Top</a>
  </p>
</div>
