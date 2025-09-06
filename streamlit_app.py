# streamlit_app.py
import streamlit as st
from PIL import Image
import os
from your_module import generate_story_scenes, parse_story_scenes, generate_scene_images  # عدل حسب اسم الملف

st.set_page_config(page_title="Story to Images", layout="wide")

st.title("✨ Story to Image Generator")
st.write("Enter a story, split it into scenes, and generate creative images for each scene using Gemini AI.")

# -----------------------------
# User Inputs
# -----------------------------
story_input = st.text_area("Enter your story here:", height=200)
num_scenes = st.number_input("Number of scenes:", min_value=1, max_value=20, value=3, step=1)

if st.button("Generate Scenes & Images"):
    if not story_input.strip():
        st.error("Please enter a story first!")
    else:
        with st.spinner("Generating story scenes..."):
            # Generate & parse scenes
            scene_text = generate_story_scenes(story_input, num_scenes)
            scenes = parse_story_scenes(scene_text)

        st.success(f"Generated {len(scenes)} scenes!")

        # Generate Images
        with st.spinner("Generating images for each scene..."):
            generate_scene_images(scenes)

        st.success("Images generated successfully!")

        # Display scenes & images
        for i, scene in enumerate(scenes, start=1):
            st.subheader(f"Scene {i}: {scene['title']}")
            st.write(scene['storytelling'])

            img_path = f"scene_{i}_0.png"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, use_column_width=True)
            else:
                st.warning("Image not found for this scene.")
