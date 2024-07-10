from django.shortcuts import render

# Create your views here.
# views.py
import os
# import openai
from openai import OpenAI
import requests
from django.shortcuts import render
from .forms import SearchForm, NoteForm
from .models import SearchResults, Note, Question,  QuestionType, NoteQuestionType
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
            selected_question_types = request.POST.getlist('question_types')
            for q_type_name in selected_question_types:
                q_type, created = QuestionType.objects.get_or_create(name=q_type_name)
                NoteQuestionType.objects.create(note=note, question_type=q_type)
            return redirect('generate_questions', note_id = note.id)  # Redirect as appropriate
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
    return text  # Ensure the function returns the extracted text


def generate_questions(note, text, question_type):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=openai_api_key)

    # Adjust the prompt based on the question type
    if question_type == 'multiple_choice':
        prompt_content = f'''Imagine you are a subject tutor on this topic. 
        You are setting a test for a student on the subject.
        Generate multiple-choice questions based on the following text:\n\n{text}'''
    elif question_type == 'true_false':
        prompt_content = f'''Imagine you are a subject tutor on this topic. 
        You are setting a test for a student on the subject.
        Generate true/false questions based on the following text:\n\n{text}'''
    elif question_type == 'short_answer':
        prompt_content = f'''Imagine you are a subject tutor on this topic. 
        You are setting a test for a student on the subject.
        Generate short answer questions based on the following text:\n\n{text}'''
    else:
        raise ValueError("Unsupported question type")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt_content,
            },
        ],
    )

    print(response.choices[0].message.content)

    questions_text = response.choices[0].message.content.strip().split('\n')
    for question in questions_text:
        if question.strip():
            # Save the question with its specified type
            Question.objects.create(note=note, question_text=question.strip(), question_type=question_type, difficulty='Medium')

def extract_text_from_note(note):
    text = process_note_file(note)
    return text

def generate_questions_view(request, note_id):
    note = Note.objects.get(id=note_id)
    text = extract_text_from_note(note)
    note_question_types = NoteQuestionType.objects.filter(note_id=note.id).order_by('question_type')


    for nqt in note_question_types:
        print("test ", nqt)
        fixed_question_type_id = nqt.question_type_id

        question_type_name = QuestionType.objects.get(id=fixed_question_type_id).name
        questions = generate_questions(note, text, question_type_name)
        

    questions_dict = {}
    # Assuming you want to fetch and display questions after generation
    questions = Question.objects.filter(note=note).order_by('question_type')
    

    for question in questions:
        
        question_type_name = QuestionType.objects.get(id=question.id).name
        if question_type_name not in questions_dict:
            questions_dict[question_type_name] = [question.question_text]  # Initialize with a list containing the question text
        else:
            #append to the existing key
            questions_dict[question_type_name].append(question.question_text)
        # final format
        # {multiple_choice: [question1, question2], 
        # true_false: [question1, question2]
        # short_answer: [question1, question2]}

    return render(request, 'generate_questions.html', {
        'note': note, 
        'questions_dict': questions_dict
    })