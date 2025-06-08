# 🌿 PlantCare AI - Plant Disease Detection & Care Assistant

A comprehensive full-stack web application that combines advanced AI-powered plant disease detection using YOLOv11 with an intelligent plant care chatbot powered by DialogPT. Built for agricultural professionals, gardeners, and plant enthusiasts.

## ✨ Features

### 🔬 AI Disease Detection
- **YOLOv11 Model**: State-of-the-art object detection for plant diseases
- **Real-time Analysis**: Upload plant images and get instant disease identification
- **Confidence Scoring**: Adjustable confidence thresholds for detection accuracy
- **Visual Results**: Annotated images with bounding boxes and disease labels
- **Disease Information**: Detailed information about detected diseases

### 🤖 Smart Plant Care Assistant
- **DialogPT Chatbot**: AI-powered conversational assistant for plant care
- **Contextual Conversations**: Maintains context about specific diseases
- **Treatment Recommendations**: Provides specific treatment advice
- **Prevention Tips**: Offers preventive measures for plant diseases
- **Chat History**: Saves and retrieves conversation history

### 👤 User Management
- **Authentication System**: Secure user registration and login
- **JWT Tokens**: Secure session management
- **User Profiles**: Personal user accounts with history tracking
- **Admin Features**: Administrative capabilities for user management

### 📊 Analytics & History
- **Prediction History**: Track all disease detection results
- **Chat History**: Review past conversations with the AI assistant
- **Usage Analytics**: Statistics on disease detections and user activity
- **Disease Trends**: Most common diseases and detection patterns

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-friendly interface
- **Bootstrap 5**: Modern, clean design
- **Interactive Elements**: Drag-and-drop file uploads
- **Real-time Updates**: Live chat interface with animations
- **Dashboard**: Comprehensive overview of user activity

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI Framework**: High-performance Python web framework
- **PostgreSQL Database**: Robust relational database
- **SQLAlchemy ORM**: Database abstraction layer
- **JWT Authentication**: Secure token-based authentication
- **RESTful API**: Well-structured API endpoints

### Frontend (Vanilla JavaScript)
- **Modern JavaScript**: ES6+ features with modular architecture
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Beautiful icons
- **SPA Architecture**: Single-page application experience

### AI Models
- **YOLOv11**: Advanced object detection for disease identification
- **DialogPT**: Conversational AI for plant care assistance
- **Custom Training**: Models trained on plant disease datasets

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd plantcare-ai
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # Start PostgreSQL service
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # Create database user
   sudo -u postgres createuser --interactive plantcare_user
   sudo -u postgres createdb plantcare_db -O plantcare_user
   ```

4. **Configure environment**
   ```bash
   # Copy and edit configuration
   cp config.py.example config.py
   # Edit config.py with your database credentials
   ```

5. **Initialize database**
   ```bash
   python setup_database.py
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

7. **Access the application**
   Open your browser to `http://localhost:8000`

## 📁 Project Structure

```
plantcare-ai/
├── main.py                 # FastAPI application entry point
├── database.py            # Database models and configuration
├── auth.py                # Authentication utilities
├── schemas.py             # Pydantic models for API
├── prediction_service.py  # YOLOv11 disease detection service
├── chatbot_service.py     # DialogPT chatbot service
├── config.py              # Application configuration
├── setup_database.py      # Database setup script
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── frontend/              # Frontend application
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS styles
│   └── app.js             # JavaScript application
├── Chatbot/               # Chatbot model and data
│   ├── modelv4/           # DialogPT model files
│   └── disease_info.json  # Disease information database
├── runs/                  # YOLOv11 model files
│   └── medium_model/      # Trained YOLO model
├── uploads/               # User uploaded images
└── outputs/               # Processed prediction images
```

## 🔧 Configuration

### Database Configuration
Edit `config.py` to configure your database connection:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/plantcare_db"
```

### Security Configuration
Set your secret key for JWT tokens:

```python
SECRET_KEY = "your-super-secret-key-here"
```

### Model Paths
Ensure your AI models are in the correct locations:

```python
MODEL_PATH = "./Chatbot/modelv4"
YOLO_MODEL_PATH = "./runs/medium_model/train/medium_plant_disease_exp2/weights/best.pt"
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Disease Detection Endpoints
- `POST /api/predict` - Upload image for disease detection
- `GET /api/predictions` - Get user's prediction history
- `GET /api/images/predicted/{filename}` - Get processed image

### Chat Endpoints
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history` - Get chat history

### Analytics Endpoints
- `GET /api/analytics` - Get usage analytics
- `GET /api/history` - Get complete user history

## 🧪 Testing

### Sample Users
If you created sample data during setup:

- **Admin User**: username=`admin`, password=`admin123`
- **Test User**: username=`testuser`, password=`test123`

### Testing Disease Detection
1. Register/login to the application
2. Navigate to "Disease Detection"
3. Upload a plant image (JPG, PNG, JPEG)
4. Adjust confidence threshold if needed
5. Click "Analyze Plant"
6. View results with annotated image

### Testing Chatbot
1. Navigate to "Plant Care Chat"
2. Ask questions about plant diseases
3. Try specific disease names for contextual responses
4. Ask follow-up questions for continued context

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure session management
- **Input Validation**: Pydantic models for API validation
- **File Upload Security**: File type validation and secure storage
- **CORS Protection**: Configurable CORS settings

## 🚀 Deployment

### Production Deployment

1. **Environment Variables**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/db"
   export SECRET_KEY="your-production-secret-key"
   export ENVIRONMENT="production"
   ```

2. **Database Migration**
   ```bash
   python setup_database.py
   ```

3. **Start with Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

4. **Nginx Configuration** (optional)
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **YOLOv11**: Ultralytics for the object detection framework
- **DialogPT**: Microsoft for the conversational AI model
- **FastAPI**: For the excellent web framework
- **Bootstrap**: For the responsive UI components

## 📞 Support

For support, email support@plantcare.ai or create an issue in the repository.

## 🔮 Future Enhancements

- [ ] Mobile app development (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Plant health monitoring over time
- [ ] Integration with IoT sensors
- [ ] Machine learning model improvements
- [ ] Social features (sharing, community)
- [ ] Expert consultation booking
- [ ] Plant care reminders and notifications

---

**Built with ❤️ for plant lovers and agricultural professionals worldwide** 🌱 