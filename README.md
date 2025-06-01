# 🏠 AI-Enhanced Real Estate CRM

A comprehensive real estate customer relationship management system with integrated AI chatbot capabilities, built for modern real estate professionals.

## ✨ Features

### 🤖 AI-Powered Assistant
- **Smart Email Processing**: Automatically extract client information from emails
- **Natural Language Queries**: Ask questions about your database in plain English
- **Intelligent Data Entry**: AI suggests database operations with user confirmation
- **Context-Aware Responses**: Remembers conversation history for better assistance

### 🏢 Complete CRM Functionality
- **Client Management**: Track buyers, sellers, and their complete profiles
- **Property Database**: Comprehensive property listings with MLS integration
- **Transaction Tracking**: Monitor deals from offer to closing
- **Document Generation**: Auto-fill PDF forms and contracts

### 🔄 Real-Time Dashboard
- **Live Statistics**: Auto-updating client, property, and transaction counts
- **Recent Activity**: See latest transactions and status changes
- **Visual Indicators**: Animated updates when data changes
- **Quick Actions**: One-click access to common tasks

### 🔗 Integration Capabilities
- **Nevada County MLS**: Direct import of MLS listings
- **ZipForm Compatibility**: Full support for California real estate forms
- **PDF Processing**: Advanced form filling and generation
- **Database Security**: User confirmation required for all AI database operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask
- SQLite (included) or PostgreSQL (production)
- Google Gemini API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/endersclarity/ai-enhanced-real-estate-crm.git
   cd ai-enhanced-real-estate-crm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

4. **Initialize the database**
   ```bash
   python real_estate_crm.py
   ```

5. **Start the application**
   ```bash
   flask run
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - Default login: admin@narissarealty.com / password

## 📊 System Architecture

### Core Components
- **Flask Backend**: RESTful API with AI integration
- **SQLite Database**: Comprehensive 177-field schema
- **AI Engine**: Google Gemini 2.5 Flash with LangChain
- **Frontend**: Bootstrap-based responsive interface
- **Real-time Updates**: JavaScript-powered dashboard refresh

### AI Integration
```
User Input → AI Processing → Operation Proposal → User Confirmation → Database Update → Dashboard Refresh
```

### Database Schema
- **Clients**: Complete contact and financial information
- **Properties**: Detailed listings with MLS integration
- **Transactions**: Full deal tracking from offer to close
- **AI Logs**: Conversation history and operation tracking

## 🛠️ Configuration

### Environment Variables
```bash
# AI Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=models/gemini-2.5-flash-preview-04-17

# Database Configuration (optional)
DATABASE_URL=sqlite:///real_estate_crm.db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Setup
The system automatically creates the database schema on first run. For production deployments, see `deployment/` folder for PostgreSQL configuration.

## 📁 Project Structure

```
ai-enhanced-real-estate-crm/
├── core_app/                    # Core application modules
│   ├── database/               # Database schemas and functions
│   ├── mls_integration.py      # MLS data processing
│   └── zipform_ai_functions.py # AI-powered form functions
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── crm_dashboard.html     # Main dashboard
│   └── clients_list.html      # Client management
├── static/                     # CSS, JavaScript, images
├── deployment/                 # Production deployment configs
├── development/               # Development tools and tests
├── documents/                 # PDF templates and forms
├── real_estate_crm.py         # Main application file
└── requirements.txt           # Python dependencies
```

## 🔧 API Endpoints

### Core CRM Operations
- `GET /` - Main dashboard
- `GET /clients` - Client list and management
- `POST /api/clients` - Create new client
- `GET /api/properties` - Property listings
- `POST /api/transactions` - Transaction management

### AI Integration
- `POST /chat` - AI chatbot interaction
- `POST /process_email` - Email content extraction
- `POST /propose_operation` - AI operation proposals
- `POST /confirm_operation` - Execute confirmed operations
- `GET /api/dashboard_stats` - Real-time statistics

## 🤖 AI Capabilities

### Natural Language Processing
The AI assistant can understand and respond to queries like:
- "Add John Smith as a new buyer, email john@email.com"
- "Show me all properties under $500,000 in Sacramento"
- "What transactions are closing this month?"
- "Create a new listing for 123 Main Street"

### Email Processing
Paste email content to automatically extract:
- Client contact information
- Property details
- Transaction data
- Important dates and deadlines

### Smart Confirmations
- All database operations require user approval
- Preview changes before execution
- Edit extracted data before saving
- Full audit trail of AI operations

## 🔒 Security Features

- **User Authentication**: Secure login system
- **Operation Confirmation**: AI cannot modify database without approval
- **Input Validation**: Comprehensive data validation
- **Audit Logging**: Complete operation history
- **Safe Defaults**: Conservative AI behavior with user override

## 🚀 Production Deployment

See the `deployment/` folder for:
- Docker configuration
- PostgreSQL setup
- Production environment variables
- Security hardening guidelines
- Performance optimization

## 🧪 Testing

Run the test suite:
```bash
python -m pytest development/tests/
```

Test categories:
- AI function integration
- Database operations
- PDF processing
- MLS integration
- Form validation

## 📚 Documentation

- **User Guide**: `README_USER_GUIDE.md`
- **Development Setup**: `INSTRUCTIONS.md`
- **Architecture Details**: `ARCHITECTURE.md`
- **Deployment Guide**: `deployment/README.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **AI Technology**: Google Gemini 2.5 Flash
- **Framework**: Flask and LangChain
- **Real Estate Standards**: California Association of Realtors forms
- **MLS Integration**: Nevada County MLS compatibility

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the troubleshooting guide in `INSTRUCTIONS.md`

---

**Built with ❤️ for real estate professionals who want to leverage AI to grow their business.**

*Version 1.0 - Production Ready*