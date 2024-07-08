from django.shortcuts import render

# Create your views here.
# views.py
import os
# import openai
from openai import OpenAI
import requests
from django.shortcuts import render
from .forms import SearchForm
from .models import SearchResults
from dotenv import load_dotenv

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
                print("hey ",response.data)
                image_url = response.data[0].url  # Extracting the image URL from the response
                created_obj = SearchResults.objects.create(url=image_url, description=query)
                print(f"SearchResults object created: {created_obj}")  # Debugging print statement
                return render(request, 'generate_image.html', {'form': form, 'image_url': image_url})
            else:
                print(f"Failed to generate image: {response.status_code}, Content: {response.text}")
    else:
        form = SearchForm()
    return render(request, 'generate_image.html', {'form': form})