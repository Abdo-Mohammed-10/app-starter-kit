# -*- coding: utf-8 -*-
import streamlit as st
from PIL import Image
import os
import mimetypes
from google import genai
from google.genai import types

# -----------------------------
# Gemini API Key
# -----------------------------
gemini_api_key = "YOUR_GEMINI_API_KEY"  # ضع هنا مفتاحك
client = genai.Client(api_key=gemini_api_key)

# -----------------------------
# الدوال الأساسية
# -----------------------------
def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

def generate_story_scenes(story_prompt, num_scenes: int):
    full_prompt = (
        f"Break this story into {num_scenes} short scenes. "
        "For each scene, provide a short description and storytelling suitable for generating creative images.\n\n"
        f"Story: {story_prompt}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[full_prompt]
    )
    return response.text

def parse_story_scenes(text: str):
    scenes = []
    raw_scenes = [s.strip() for s in text.split("### Scene") if s.strip()]
    for raw_scene in raw_scenes:
        lines = [line.strip() for line in raw_scene.split("\n") if line.strip()]
        if not lines:
            continue
        first_line = lines[0]
        title = first_line.split(":",1)[1].strip() if ":" in first_line else first_line.strip()
        description = ""
        storytelling = ""
        capture_story = False
        for line in lines[1:]:
            if line.startswith("**Description:**"):
                description = line.replace("**Description:**", "").strip()
            elif line.startswith("**Storytelling for Creative Images:**"):
                storytelling = line.replace("**Storytelling for Creative Images:**", "").strip()
                capture_story = True
            elif capture_story:
                storytelling += " " + line
        storytelling = storytelling.replace("---", "").strip()
        if title or description or storytelling:
            scenes.append({
                "title": title or "Untitled Scene",
                "description": description,
                "storytelling": storytelling,
            })
    return scenes

def generate_scene_images(scenes):
    model = "gemini-2.5-flash-image-preview"
    for idx, scene in enumerate(scenes, 1):
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=scene['storytelling'])]
            )
        ]
        config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        file_index = 0
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config
        ):
            if chunk.candidates is None or chunk.candidates[0].content is None or chunk.candidates[0].content.parts is None:
                continue
            part = chunk.candidates[0].content.parts[0]
            if part.inline_data and part.inline_data.data:
                ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
                file_name = f"scene_{idx}_{file_index}{ext}"
                file_index += 1
                save_binary_file(file_name, part.inline_data.data)

# -----------------------------
# واجهة Streamlit
# -----------------------------
st.set_page_config(page_title="Story to Images", layout="wide")
st.title("✨ Story to Image Generator")
st.write("Enter a story, split it into scenes, and generate creative images for each scene using Gemini AI.")

story_input = st.text_area("Enter your story here:", height=200)
num_scenes = st.number_input("Number of scenes:", min_value=1, max_value=20, value=3, step=1)

if st.button("Generate Scenes & Images"):
    if not story_input.strip():
        st.error("Please enter a story first!")
    else:
        with st.spinner("Generating story scenes..."):
            scene_text = generate_story_scenes(story_input, num_scenes)
            scenes = parse_story_scenes(scene_text)
        st.success(f"Generated {len(scenes)} scenes!")

        with st.spinner("Generating images for each scene..."):
            generate_scene_images(scenes)
        st.success("Images generated successfully!")

        for i, scene in enumerate(scenes, start=1):
            st.subheader(f"Scene {i}: {scene['title']}")
            st.write(scene['storytelling'])
            img_path = f"scene_{i}_0.png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, use_column_width=True)
            else:
                st.warning("Image not found for this scene.")
