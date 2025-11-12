# Mentora AI - Personal Growth & Study Assistant

An AI-powered personal growth and study assistant designed for students and professionals. Combines journaling, habit tracking, AI mentorship, study planning, mood analytics, and goal alignment into a single intuitive dashboard.

## 🚀 Features

### Core Modules

1. **📝 Journal with AI Reflections**
   - Daily journal entries
   - AI-generated reflection summaries
   - Mood tone analysis
   - Historical entry tracking

2. **✅ Daily To-Do & Habit Tracker**
   - Create and manage habits
   - Streak tracking
   - Progress percentage
   - Daily completion tracking
   - Motivational AI nudges

3. **🎯 Goal Setting (Short-term & Long-term)**
   - Create goals with descriptions
   - Progress tracking
   - Target date setting
   - Linked to daily habits

4. **💭 Mood Tracking & Analytics**
   - Daily mood logging (emoji + scale)
   - Week-over-week trend visualization
   - AI insights based on emotional patterns
   - Mood history tracking

5. **📚 Personalized AI Study Plan**
   - Subject-based study plans
   - AI-generated weekly schedules
   - Progress tracking
   - Study session logging

6. **👤 User Profile**
   - AI engagement summary
   - Statistics dashboard
   - Activity overview
   - Quick actions

## 🏗️ Tech Stack

- **Backend**: Django 5 + Django REST Framework (DRF)
- **Frontend**: TailwindCSS + HTMX + Alpine.js
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Google OAuth (django-allauth / social-auth-app-django)
- **AI Layer**: OpenAI API (with stub fallback)
- **Deployment**: Docker-ready, Render or Railway compatible

## 🎨 Design Philosophy

- **Minimalist UI**: Focus on productivity and calm energy
- **Dark Theme**: `bg-slate-950` / `bg-gray-900` base
- **Accent Color**: Indigo (#6366F1) - consistent branding
- **Typography**: System fonts (Inter/Poppins via Tailwind)
- **Smooth Interactions**: HTMX for dynamic UI without heavy JavaScript

## 📦 Installation

1. **Clone the repository**
   ```bash
   cd MENTORA_AI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   OPENAI_API_KEY=your-openai-api-key-optional
   SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-oauth-key
   SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-oauth-secret
   ```

5. **Run migrations**
   ```bash
   cd mentora
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Home: http://localhost:8000/
   - Dashboard: http://localhost:8000/dashboard/
   - Admin: http://localhost:8000/admin/

## 🔌 API Endpoints

All API endpoints require authentication. Base URL: `/api/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/journals/` | GET, POST | Manage journal entries |
| `/api/journals/{id}/` | GET, PUT, DELETE | Individual journal operations |
| `/api/journals/generate_reflection/` | POST | Generate AI reflection for text |
| `/api/habits/` | GET, POST | Manage habits |
| `/api/habits/{id}/complete/` | POST | Mark habit as completed |
| `/api/habits/{id}/nudge/` | GET | Get AI motivational nudge |
| `/api/goals/` | GET, POST | Manage goals |
| `/api/goals/by_type/` | GET | Filter goals by type |
| `/api/moods/` | GET, POST | Log moods |
| `/api/moods/analytics/` | GET | Get mood analytics and insights |
| `/api/studyplans/` | GET, POST | Manage study plans |
| `/api/studyplans/{id}/add_session/` | POST | Add study session |

## 🧠 AI Integration

The AI service layer (`dashboard/ai_service.py`) supports:

- **OpenAI Integration**: When `OPENAI_API_KEY` is set, uses GPT-3.5-turbo
- **Stub Mode**: Falls back to keyword-based analysis when OpenAI is unavailable
- **Features**:
  - Journal entry summarization
  - Mood tone analysis
  - Mood trend insights
  - Study plan generation
  - Habit motivational nudges

## 📁 Project Structure

```
MENTORA_AI/
├── mentora/
│   ├── dashboard/          # Main app with all modules
│   │   ├── models.py      # Journal, Habit, Goal, Mood, StudyPlan
│   │   ├── views.py       # Dashboard views
│   │   ├── viewsets.py    # DRF API viewsets
│   │   ├── serializers.py # DRF serializers
│   │   ├── ai_service.py  # AI integration layer
│   │   └── admin.py       # Admin configuration
│   ├── users/             # User management
│   ├── user_form/         # Legacy forms (Academic, Wellbeing)
│   ├── mentora/           # Project settings
│   │   ├── settings.py
│   │   └── urls.py
│   └── templates/         # HTML templates
│       ├── base.html
│       ├── dashboard/
│       └── users/
├── requirements.txt
└── README.md
```

## 🔐 Authentication

The app uses Google OAuth for authentication via `social-auth-app-django`. Configure your Google OAuth credentials in settings or environment variables.

## 🗄️ Database Models

- **Journal**: User journal entries with AI summaries
- **Habit**: Habit tracking with streaks and progress
- **HabitCompletion**: Daily habit completion records
- **Goal**: Short-term and long-term goals
- **Mood**: Daily mood tracking with emoji and scale
- **StudyPlan**: AI-generated study plans
- **StudySession**: Individual study session records

## 🚢 Deployment

### Docker (Recommended)

1. Create `Dockerfile` and `docker-compose.yml`
2. Set environment variables
3. Build and run:
   ```bash
   docker-compose up -d
   ```

### Render / Railway

1. Connect your repository
2. Set environment variables
3. Configure PostgreSQL database
4. Deploy!

## 📝 Development Notes

- The app uses SQLite by default for development
- For production, update `settings.py` to use PostgreSQL
- AI features work with stub mode if OpenAI API key is not provided
- All templates use TailwindCSS via CDN (consider using django-tailwind for production)

## 🎯 Next Steps

- [ ] Add Celery for async AI processing
- [ ] Implement email notifications
- [ ] Add data export functionality
- [ ] Create mobile-responsive improvements
- [ ] Add more AI insights and recommendations
- [ ] Implement social sharing features
- [ ] Add dark/light theme toggle

## 📄 License

This project is part of a Final Year project.

## 👥 Credits

Built with Django, TailwindCSS, HTMX, and OpenAI.

---

**Mentora AI** - Reflect, Plan, and Grow Intelligently 🚀

