from django.shortcuts import render

# Create your views here.
# views.py
import os
# import openai
from openai import OpenAI
import requests
from django.shortcuts import render
from .forms import SearchForm, NoteForm
from .models import SearchResults, Note, Question
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.conf import settings
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

load_dotenv()

def generate_image(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            openai_api_key = os.getenv('OPENAI_API_KEY')
            client = OpenAI(api_key=openai_api_key)
            
            # Updated request to OpenAI for image generation using the provided guide
            response = client.images.generate(
                model="dall-e-3",
                prompt=query,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
             # Since the response object does not have a 'status_code' attribute, we directly access the data
            if response.data:  # Check if response data is not empty
                # print("hey ",response.data)
                image_url = response.data[0].url  # Extracting the image URL from the response
                created_obj = SearchResults.objects.create(url=image_url, description=query)
                print(f"SearchResults object created: {created_obj}")  # Debugging print statement
                return render(request, 'generate_image.html', {'form': form, 'image_url': image_url})
            else:
                print(f"Failed to generate image: {response.status_code}, Content: {response.text}")
    else:
        form = SearchForm()
    return render(request, 'generate_image.html', {'form': form})


def upload_note_view(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save()
            process_note_file(note)
            return redirect('generate_questions', note_id=note.id)
    else:
        form = NoteForm()
    return render(request, 'upload_note.html', {'form': form})

def process_note_file(note):
    text = ''
    file_path = note.file.path
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.pdf':
        pages = convert_from_path(file_path, 500)
        for page in pages:
            text += pytesseract.image_to_string(page)
    elif file_ext in ['.jpg', '.jpeg', '.png']:
        text = pytesseract.image_to_string(Image.open(file_path))
    elif file_ext in ['.txt']:
        with open(file_path, 'r') as file:
            text = file.read()

    generate_questions(note, text)

def generate_questions(note, text):
    # response = openai.Completion.create(
    #     engine="text-davinci-003",
    #     prompt=f"Generate multiple-choice questions, true/false questions, and short answer questions based on the following text:\n\n{text}",
    #     max_tokens=1000
    # )

    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                        {
                            "role": "user",
                            # "content":f"Generate multiple-choice questions, true/false questions, and short answer questions based on the following text:\n\n{text}",
                            
                            "content":f'''Imagine you are a subject tutor on this topic. 
                            You are setting a test for a student on the subject.
                            Generate multiple-choice questions, based on the following text:\n\n{text}''',

                        },
                    ],
                    # max_tokens=2000
                )
    
    print(response.choices[0].message.content)
     
    questions_text = response.choices[0].message.content.strip().split('\n')
    # questions_text = response.choices[0].text.strip().split('\n')
    for question in questions_text:
        if question.strip():
            Question.objects.create(note=note, question_text=question.strip(), question_type='Mixed', difficulty='Medium')

def generate_questions_view(request, note_id):
    note = Note.objects.get(id=note_id)
    questions = Question.objects.filter(note=note)

    grouped_questions = {
        'multiple_choice': [q for q in questions if q.type == 'multiple_choice'],
        'true_false': [q for q in questions if q.type == 'true_false'],
        'short_answer': [q for q in questions if q.type == 'short_answer'],
    }
    # return render(request, 'generate_questions.html', {'note': note, 'questions': questions})
    return render(request, 'generate_questions.html', {'note': note, 'grouped_questions': grouped_questions})