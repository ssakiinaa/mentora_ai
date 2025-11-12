from django.db import models

class Academic(models.Model):
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=5)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.grade}"
    
    class Meta:
        ordering = ['-created_at']

class Wellbeing(models.Model):
    mood = models.CharField(max_length=50)
    sleep_hours = models.PositiveIntegerField()
    remarks = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.mood} - {self.sleep_hours}h sleep"
    
    class Meta:
        ordering = ['-created_at']
