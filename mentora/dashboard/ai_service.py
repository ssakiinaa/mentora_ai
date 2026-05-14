"""
AI Core Service Layer for Mentora AI
Handles AI-powered reflections, mood analysis, and study plan generation
"""
import os
from decouple import config
from typing import List, Dict, Optional

# Try to import OpenAI, fallback to stub if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AICore:
    """Core AI service for generating insights and reflections"""
    
    def __init__(self):
        self.api_key = config('OPENAI_API_KEY', default=None)
        if OPENAI_AVAILABLE and self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def summarize_journal(self, entry_text: str) -> Dict[str, str]:
        """
        Generate AI reflection summary from journal entry
        
        Returns:
            dict with 'summary' and 'mood_tone' keys
        """
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a thoughtful AI mentor. Provide brief, encouraging reflections on journal entries. Keep responses under 100 words."},
                        {"role": "user", "content": f"Please provide a brief reflection on this journal entry:\n\n{entry_text}"}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                summary = response.choices[0].message.content
                
                # Determine mood tone
                mood_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Analyze the emotional tone. Respond with ONE word: positive, reflective, anxious, calm, or neutral."},
                        {"role": "user", "content": entry_text}
                    ],
                    max_tokens=10,
                    temperature=0.3
                )
                mood_tone = mood_response.choices[0].message.content.strip().lower()
                
                return {
                    'summary': summary,
                    'mood_tone': mood_tone
                }
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._stub_summarize_journal(entry_text)
        else:
            return self._stub_summarize_journal(entry_text)
    
    def _stub_summarize_journal(self, entry_text: str) -> Dict[str, str]:
        """Stub implementation when OpenAI is not available"""
        # Simple keyword-based analysis
        entry_lower = entry_text.lower()
        if any(word in entry_lower for word in ['happy', 'great', 'excited', 'proud', 'grateful']):
            mood_tone = 'positive'
            summary = "AI Reflection: Your entry shows positive energy! Keep focusing on consistency and maintaining this optimistic outlook."
        elif any(word in entry_lower for word in ['worry', 'stress', 'anxious', 'concerned', 'difficult']):
            mood_tone = 'anxious'
            summary = "AI Reflection: It's normal to face challenges. Remember to take breaks, practice self-care, and focus on what you can control."
        elif any(word in entry_lower for word in ['think', 'reflect', 'consider', 'wonder', 'contemplate']):
            mood_tone = 'reflective'
            summary = "AI Reflection: Your thoughtful reflection shows self-awareness. Continue exploring your thoughts and feelings."
        else:
            mood_tone = 'neutral'
            summary = "AI Reflection: Keep focusing on consistency and positivity. Every day is a step forward in your journey."
        
        return {
            'summary': summary,
            'mood_tone': mood_tone
        }
    
    def analyze_mood(self, mood_entries: List[Dict]) -> str:
        """
        Analyze mood trends from recent entries
        
        Args:
            mood_entries: List of dicts with 'mood_scale' and 'date' keys
            
        Returns:
            String insight about mood trends
        """
        if not mood_entries:
            return "Start tracking your mood to see insights!"
        
        if len(mood_entries) < 3:
            return "Keep tracking your mood to see patterns emerge!"
        
        # Calculate average mood
        avg_mood = sum(entry.get('mood_scale', 5) for entry in mood_entries) / len(mood_entries)
        recent_avg = sum(entry.get('mood_scale', 5) for entry in mood_entries[:3]) / min(3, len(mood_entries))
        
        if recent_avg > avg_mood + 0.5:
            return "Your mood has been improving this week! Keep up the great work! 🌟"
        elif recent_avg < avg_mood - 0.5:
            return "Your mood has been lower recently. Remember to take care of yourself and reach out if needed. 💙"
        else:
            return "Your mood has been relatively stable. Consistency is key to growth!"
    
    def generate_study_plan(self, subjects: List[str], goals: List[str]) -> Dict:
        """
        Generate personalized study plan
        
        Args:
            subjects: List of subjects to study
            goals: List of learning goals
            
        Returns:
            Dict with 'description' and 'schedule' keys
        """
        if self.client:
            try:
                subjects_str = ", ".join(subjects)
                goals_str = ", ".join(goals)
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an AI study planner. Create a structured weekly study plan. Format: brief description, then daily schedule."},
                        {"role": "user", "content": f"Create a study plan for subjects: {subjects_str}. Goals: {goals_str}"}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                plan_text = response.choices[0].message.content
                
                # Parse into schedule (simplified)
                schedule = {
                    "Monday": f"Focus on {subjects[0] if subjects else 'main subject'}",
                    "Tuesday": f"Review and practice",
                    "Wednesday": f"Deep dive into {subjects[1] if len(subjects) > 1 else subjects[0] if subjects else 'topics'}",
                    "Thursday": f"Practice and exercises",
                    "Friday": f"Weekly review",
                    "Saturday": f"Light study or rest",
                    "Sunday": f"Plan next week"
                }
                
                return {
                    'description': plan_text,
                    'schedule': schedule
                }
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._stub_generate_study_plan(subjects, goals)
        else:
            return self._stub_generate_study_plan(subjects, goals)
    
    def _stub_generate_study_plan(self, subjects: List[str], goals: List[str]) -> Dict:
        """Stub implementation for study plan generation"""
        subjects_str = ", ".join(subjects) if subjects else "your subjects"
        
        description = f"Personalized study plan for {subjects_str}. Focus on consistent daily practice, spaced repetition, and regular review sessions."
        
        schedule = {
            "Monday": f"Morning: {subjects[0] if subjects else 'Main subject'} - Theory",
            "Tuesday": f"Morning: Practice exercises",
            "Wednesday": f"Morning: {subjects[1] if len(subjects) > 1 else subjects[0] if subjects else 'Topics'} - Deep dive",
            "Thursday": f"Morning: Review and practice",
            "Friday": f"Morning: Weekly review and assessment",
            "Saturday": f"Light study or rest day",
            "Sunday": f"Plan and prepare for next week"
        }
        
        return {
            'description': description,
            'schedule': schedule
        }
    
    def get_habit_nudge(self, habit_name: str, streak: int, progress: float) -> str:
        """Generate motivational nudge for habits"""
        if streak >= 7:
            return f"🔥 Amazing {streak}-day streak on {habit_name}! You're building incredible momentum!"
        elif streak >= 3:
            return f"💪 Great {streak}-day streak! Keep going, you're doing fantastic!"
        elif progress > 70:
            return f"✨ You're {progress:.0f}% there on {habit_name}! Almost at your goal!"
        else:
            return f"🌟 Every step counts! Keep working on {habit_name}, consistency is key!"

    def generate_coaching_response(self, user_question: str, user_context: str, tone_mode: str = 'empathy') -> str:
        """Generate a coaching reply using the user's recent data and goals."""
        if tone_mode == 'performance':
            prompt = (
                "You are a strict academic coach and performance mentor. "
                "Push the user to improve academically and build discipline. Identify excuses, laziness, or lack of clarity and call them out directly. "
                "Give clear, structured, and practical study strategies. Help the user stay accountable and consistent. "
                "Your tone should be direct, blunt, and honest. Motivating but strict (like a tough older brother). NO sugarcoating. No unnecessary sympathy. "
                "Do NOT insult or demotivate the user. Be harsh on behavior, not on the person. Always provide a solution or improvement plan after pointing out mistakes. "
                "Focus on discipline, consistency, and execution. Break down complex goals into actionable steps. "
                "If the user is procrastinating, call it out clearly. If the user lacks discipline, highlight it and give a fix. "
                "If the user is confused, simplify and guide. If the user is doing well, acknowledge briefly, then push them further. "
                "Turn the user into a highly disciplined, focused, and high-performing student who takes responsibility and executes consistently."
                "Use not more than 1000 tokens to reply."
            )
        else:
            prompt = (
                "You are an empathetic life coach, mentor, and emotional support system. "
                "Listen carefully and understand the user’s feelings, struggles, and goals. Respond with empathy, patience, and emotional intelligence. "
                "Encourage positivity, resilience, and long-term growth. Motivate the user to stay consistent, disciplined, and focused on their goals. "
                "Help them reflect on their thoughts and make better decisions. "
                "Your tone should be warm, calm, supportive, and non-judgmental. Like a wise mentor who genuinely cares. Encouraging but realistic (not fake positivity). "
                "NEVER suggest anything that can harm the user’s physical or mental health. NEVER encourage risky, unethical, or harmful behavior. "
                "ALWAYS prioritize the user’s safety, well-being, and future. If the user is stressed, overwhelmed, or confused, first acknowledge their feelings before giving advice. "
                "Give practical, small, actionable suggestions when appropriate. Help the user build discipline, clarity, and self-belief. "
                "Help the user become mentally strong, emotionally stable, and consistently working towards their goals in a healthy and sustainable way."
                "Use not more than 1000 tokens to reply."
            )

        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": f"User context:\n{user_context}\n\nUser question: {user_question}"}
                    ],
                    max_tokens=250,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API error: {e}")
                return self._stub_generate_coaching_response(user_question, user_context)
        return self._stub_generate_coaching_response(user_question, user_context)

    def _stub_generate_coaching_response(self, user_question: str, user_context: str) -> str:
        """Stub response when OpenAI is unavailable."""
        return (
            "Thanks for sharing. Based on your recent goals and habits, try focusing on one clear action today, "
            "breaking it into manageable steps. Keep checking your progress and celebrate small wins. "
            "If you want, ask me for a specific plan or a habit adjustment."
        )


# Singleton instance
ai_core = AICore()

