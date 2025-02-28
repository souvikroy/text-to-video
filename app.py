# Load environment variables at the very beginning
from dotenv import load_dotenv
load_dotenv()

# Import after environment variables are loaded
import streamlit as st
import os
from video_generator import generate_video_from_text, get_enhanced_prompt

# Check if API key is set
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found! Please make sure you have set it in the .env file.")
    st.stop()

def main():
    st.set_page_config(
        page_title="Text to Video Generator",
        page_icon="🎬",
        layout="wide"
    )

    st.title("🎬 Text to Video Generator")
    st.write("Transform your text descriptions into engaging videos!")

    # Text input for video description
    text_input = st.text_area(
        "Enter your video description",
        height=150,
        placeholder="Describe the video you want to create..."
    )

    # Advanced options
    with st.expander("Advanced Options"):
        duration = st.slider("Video Duration (seconds)", 5, 30, 10)
        quality = st.select_slider(
            "Generation Quality",
            options=["Draft", "Standard", "High"],
            value="Standard"
        )

    if st.button("Generate Video", type="primary"):
        if not text_input:
            st.error("Please enter a video description first!")
            return

        try:
            with st.spinner("🎨 Generating your video..."):
                # Progress indicators
                progress_text = st.empty()
                progress_bar = st.progress(0)

                # Step 1: Enhanced prompt generation
                progress_text.text("Enhancing your description with AI...")
                progress_bar.progress(20)
                enhanced_prompt = get_enhanced_prompt(text_input)

                # Step 2: Video generation
                progress_text.text("Generating video frames...")
                progress_bar.progress(50)
                video_path = generate_video_from_text(
                    enhanced_prompt,
                    duration=duration,
                    quality=quality.lower()
                )

                progress_bar.progress(100)
                progress_text.text("✨ Video generation complete!")

                # Display the generated video
                st.video(video_path)
                
                # Download button
                with open(video_path, 'rb') as f:
                    st.download_button(
                        label="Download Video",
                        data=f,
                        file_name="generated_video.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"An error occurred during video generation: {str(e)}")

    # Instructions and tips
    with st.expander("📝 Tips for better results"):
        st.markdown("""
        - Be specific and detailed in your description
        - Include information about mood, setting, and action
        - Mention any specific visual elements you want to see
        - Consider the pacing and flow of the video
        """)

if __name__ == "__main__":
    main()
