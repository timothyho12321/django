from django.db import models

# Create your models here.

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    age = models.CharField(max_length=100, default='0')
    
    
class SearchResults(models.Model):
    url = models.URLField(max_length=2048)  # Increase the max_length to accommodate longer URLs
    description = models.TextField()


class Note(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    question_types = models.ManyToManyField('QuestionType', through='NoteQuestionType')

    def __str__(self):
        return self.title

class Question(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.question_type}: {self.question_text}'
    
class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class NoteQuestionType(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)

