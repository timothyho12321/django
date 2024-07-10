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
    
#  list of questions names
class QuestionType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
# one to many, one question can have only one question type
class Question(models.Model):
    question_text = models.TextField()
    difficulty = models.CharField(max_length=50)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)  # Changed from CharField to ForeignKey
    
    def __str__(self):
        return f'{self.question_type}: {self.question_text}'
    
# many to many, one note can have multiple question types
class NoteQuestionType(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)

