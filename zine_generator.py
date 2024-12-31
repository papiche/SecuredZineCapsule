#!/usr/bin/env python3
import argparse
import requests
import json
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import os

try:
    from ollama import generate
except ImportError:
    print("Ollama library not found. Please install 'pip install ollama'")
    generate = lambda **kwargs: {'response': 'Ollama not available'}

# ----------------------
# CONFIGURATION
# ----------------------
OLLAMA_MODEL = 'llama2'  # Modify to use the Ollama model
COMFYUI_URL = "http://127.0.0.1:8188/prompt"  # ComfyUI API URL (change as needed)
OUTPUT_DIR = "generated_zines"  # Store the generated HTML and images

# ----------------------
# FUNCTIONS
# ----------------------

def get_movie_data(movie_name):
    """Fetches movie data from TMDB."""

    TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your actual TMDB API key
    TMDB_BASE_URL = "https://api.themoviedb.org/3"

    search_url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name,
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDB: {e}")
        return None

    results = data.get("results", [])

    if not results:
        print("No movies found with that name.")
        return None

    print("Select a movie: ")
    for idx, movie in enumerate(results):
        print(f"{idx+1} : {movie['title']} ({movie.get('release_date','')})")

    selected_movie = None
    while selected_movie is None:
      try:
        choice = int(input("Enter your choice [1]: ")) if len(results) > 1 else 1
        selected_movie = results[choice-1]
      except (ValueError, IndexError):
        print("Invalid choice. Please enter a valid option")

    movie_id = selected_movie['id']
    details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"

    params = {
        "api_key": TMDB_API_KEY,
    }

    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        movie_details = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from TMDB: {e}")
        return None
    return movie_details


def generate_text(prompt, model_name = OLLAMA_MODEL):
    """Generates text using Ollama."""

    print(f"Generating text with Ollama using prompt: {prompt}")
    try:
      response = generate(model=model_name, prompt=prompt)
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"Ollama Generation Error: {e}"
    return response['response'].strip()


def generate_image(prompt):
    """Generates an image using ComfyUI."""

    print(f"Generating Image with ComfyUI using prompt: {prompt}")
    payload = {
        "prompt": {
            "1": {
                "inputs": {"text": prompt},
                "class_type": "CLIPTextEncode",
            },
            "2": {
                "inputs": {"samples": ["1", 0]},
                "class_type": "VAEEncode",
            },
            "3": {
                "inputs": {"latent_image": ["2", 0]},
                "class_type": "KSampler",
            },
            "4": {
                "inputs": {"samples": ["3", 0]},
                "class_type": "VAEDecode",
            },
            "5": {
                "inputs": {
                    "images": ["4", 0],
                    "filename_prefix": "output",
                    "output_path": "output",
                },
                "class_type": "SaveImage",
            },
        }
    }

    try:
        response = requests.post(COMFYUI_URL, json=payload)
        response.raise_for_status()
        output_name = response.json().get("output", {}).get("images", [])[0]
        print(f"Image Generated: {output_name}")
        return f"http://127.0.0.1:8188/view?filename={output_name}"
    except Exception as e:
        print(f"ComfyUI Error: {e}")
        return "ComfyUI Image Generation Error"


def create_zine(movie_data):
    """Creates the Zine HTML."""
    print("Starting Zine Generation")

    # Template loading
    env = Environment(loader=FileSystemLoader('.')) # Assumes the template in same dir
    template = env.get_template('zine_template.html') # Template name

    movie_title = movie_data['title']
    movie_description = movie_data['overview']
    # generate subtitle
    sub_title_prompt = f"Write a short, one sentence subtitle for the movie {movie_title} about its genre"
    movie_subtitle = generate_text(sub_title_prompt)
    # Cover image generation
    cover_prompt = f"a movie poster for the movie {movie_title}"
    cover_image_url = generate_image(cover_prompt)

    # Page 2 content generation
    page2_prompt = f"Write a paragraph about the movie {movie_title} plot summary"
    page2_content = generate_text(page2_prompt)

    # Page 3 content generation
    page3_prompt = f"List the main characters of the movie {movie_title} and a one line description for each"
    page3_content = generate_text(page3_prompt)

    # Page 4 content generation
    page4_prompt = f"Write a paragraph about how this movie {movie_title} is unique among other movies of the same genre"
    page4_content = generate_text(page4_prompt)

    # Page 5 content generation
    page5_prompt = f"Suggest 3 things someone should watch before watching the movie {movie_title} based on similar genre"
    page5_content = generate_text(page5_prompt)

    # Page 6 content generation
    page6_prompt = f"Write 3 questions to check if someone understands the movie {movie_title}"
    page6_content = generate_text(page6_prompt)

    # Page 7 content generation
    page7_prompt = f"Write the correct answer for the previous questions about the movie {movie_title}"
    page7_content = generate_text(page7_prompt)


    # Fill the template with generated data
    rendered_zine = template.render(
       _TITLE_ = movie_title,
        _ONE_SENTENCE_SUBTITLE_ = movie_subtitle,
        _FULL_IMG_URL_ = cover_image_url,
        page_2 = page2_content,
        page_3 = page3_content,
        page_4 = page4_content,
        page_5 = page5_content,
        page_6 = page6_content,
        page_7 = page7_content
    )
    return rendered_zine


def save_zine(html_content, movie_title):
    """Saves the Zine HTML to a file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"{movie_title.replace(' ','_')}_zine.html")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Zine saved to: {filename}")
    return filename



# ----------------------
# CLI AND UI
# ----------------------

def cli_interface():
    """Command line interface for generating a zine."""
    parser = argparse.ArgumentParser(description="Generate a movie zine.")
    parser.add_argument("movie_title", help="The title of the movie.")
    args = parser.parse_args()

    movie_data = get_movie_data(args.movie_title)
    if not movie_data:
        print("Error getting movie data.")
        return

    zine_html = create_zine(movie_data)
    save_zine(zine_html, movie_data["title"])


def ui_interface():
    """Web user interface for generating a zine."""
    from flask import Flask, render_template, request

    app = Flask(__name__)

    @app.route('/', methods=['GET','POST'])
    def index():
      if request.method == 'GET':
        return render_template("form.html")
      else:
        movie_title = request.form["movie_title"]
        movie_data = get_movie_data(movie_title)
        if not movie_data:
          return render_template("error.html", message="Could not retrieve the movie details")

        zine_html = create_zine(movie_data)
        output_path = save_zine(zine_html, movie_data["title"])
        return render_template("success.html", filename=output_path)


    if __name__ == "__main__":
        app.run(debug=True)


# ----------------------
# MAIN ENTRYPOINT
# ----------------------

if __name__ == "__main__":
    mode = input("Choose interface (cli/ui): ").strip().lower()
    if mode == "cli":
        cli_interface()
    elif mode == "ui":
      ui_interface()
    else:
        print("Invalid mode. Please choose 'cli' or 'ui'.")
