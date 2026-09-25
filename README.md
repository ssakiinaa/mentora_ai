Mentora AI: An AI-Powered Personal Growth & Study Assistant

Balancing coursework, long-term goals, and daily health can quickly become overwhelming. **Mentora AI** is a holistic mentorship platform designed to bring structure to student life. Instead of treating productivity and personal well-being as separate things, Mentora AI connects your academic progress with daily wellness habits—helping you stay on top of your work without burning out.


**Key Features**

* **Academic Goal & Task Tracking:** Set long-term objectives, break them down into actionable steps, and keep your momentum going with visual progress bars and daily streak counters.

* **Daily Wellness Logging:** Quickly log essential health metrics including mood, sleep hours, physical activity, and overall day satisfaction.

* **AI Coaching & Chat:** Have natural, context-aware conversations with an AI assistant that understands your recent habit patterns and goals. Built-in sentiment analysis helps keep feedback constructive and relevant.

* **Productivity & Wellness Analytics:** Automatically analyze how your lifestyle affects your study habits. The platform runs background correlation checks to show you direct links between sleep, mood, and task completion.

* **Smart Study Schedules & Habits:** Generate customized weekly study plans and track routine habits over time.

* **Journaling & AI Reflection:** Write daily reflections and receive instant AI feedback to help you process your thoughts and set intentions for the next day.


**Tech Stack**

* **Backend Framework:** Python 3.12, Django 5.2, Django REST Framework

* **Frontend:** Django Templates, HTMX (for dynamic UI updates without full page reloads), TailwindCSS

* **Database:** SQLite (Development) / PostgreSQL (Production)

* **AI & NLP:** OpenAI GPT Models, NLTK / Custom Sentiment Analysis Pipeline


**Getting Started**

Follow these steps to run the application locally on your machine.

### Prerequisites

Make sure you have **Python 3.12+** and `git` installed on your system.

### Local Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/mentora-ai.git
cd mentora-ai

```


2. **Set up a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Configure environment variables:**
Create a `.env` file in the root directory (you can copy `.env.example`) and add your credentials:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
OPENAI_API_KEY=your_openai_api_key

```


> **Note:** If an OpenAI API key is not provided or rate limits are reached, the system will automatically fall back to an internal offline stub mode so all features remain functional.
> 
> 


5. **Apply database migrations:**
```bash
python manage.py migrate

```


6. **Start the local server:**
```bash
python manage.py runserver

```


Open your browser and visit `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)` to explore the app.

---

## Under the Hood: Key Algorithms

### 1. Sentiment Analysis Pipeline

Conversations and journal inputs pass through a light text-processing flow to gauge user sentiment:


$$\text{Text Input} \rightarrow \text{Tokenization} \rightarrow \text{Stop-Word Filtering (keeping negations)} \rightarrow \text{Lemmatization} \rightarrow \text{Score } [-1.0, +1.0]$$

### 2. Productivity Score (PS) Formula

Productivity isn't just about finishing tasks; it's about consistency over time. Mentora combines completion rates, goal strides, and daily streaks into a single balanced score:

$$\text{PS} = (0.40 \times \text{TCR} + 0.35 \times \text{GPR} + 0.25 \times \text{SCR}) \times 100$$

* **TCR:** Task Completion Rate


* **GPR:** Goal Progress Rate


* **SCR:** Streak Consistency Rate



### 3. Wellness Correlation Engine

To answer questions like *"Does better sleep actually improve my study output?"*, the system computes Pearson's correlation coefficient ($r$) across rolling 7-day windows comparing wellness metrics against daily productivity scores. Results with $p < 0.05$ trigger clear, plain-language insights directly on the user dashboard.

---

## Authors & Acknowledgments

* **Sakina Salim Sayed**

* **Nadeem Naseem Ansari**

* **Mujammil Abdulsattar Shaikh**

* **Abdullah Rehbar Alam Khan**


**Project Guide:** Prof. A. N. Adapanawar

*Department of Computer Engineering, Sinhgad Academy of Engineering, Pune*

---

## Research Publication

This project is backed by published academic research:

* **Title:** *MENTORA AI: AN AI-POWERED PERSONAL GROWTH AND STUDY ASSISTANT WITH INTEGRATED ANALYTICS AND CONVERSATIONAL INTELLIGENCE*

* **Journal:** *International Research Journal of Modernization in Engineering Technology and Science (IRJMETS)*, Volume 08, Issue 03, March 2026


* **DOI:** [10.56726/IRJMETS92563](https://www.google.com/search?q=https://www.doi.org/10.56726/IRJMETS92563&utm_source=gemini)
