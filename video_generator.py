import os
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip
import requests
from io import BytesIO
from dotenv import load_dotenv
from gtts import gTTS
import srt
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables!")

client = OpenAI(api_key=api_key)

def add_text_to_frame(frame, text, add_watermark=True):
    """Add text overlay and watermark to a frame using PIL"""
    # Convert numpy array to PIL Image
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    
    # Calculate text size and position
    img_w, img_h = img.size
    text_w = int(img_w * 0.8)  # Use 80% of image width
    
    # Wrap text
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(' '.join(current_line)) > 40:  # Adjust based on your needs
            lines.append(' '.join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    text = '\\n'.join(lines)
    
    # Add text with black outline
    x = img_w // 2
    y = int(img_h * 0.85)  # Position at 85% of height
    
    # Draw text outline
    for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
        draw.text((x + offset[0], y + offset[1]), text,
                 font=None, fill='black', anchor='mm', align='center')
    
    # Draw main text
    draw.text((x, y), text, fill='white', anchor='mm', align='center')
    
    # Add watermark
    if add_watermark:
        watermark = "Creator: Souvik Roy"
        watermark_x = int(img_w * 0.95)  # Position at 95% of width
        watermark_y = int(img_h * 0.95)  # Position at 95% of height
        
        # Draw watermark outline
        for offset in [(1,1), (-1,-1), (1,-1), (-1,1)]:
            draw.text((watermark_x + offset[0], watermark_y + offset[1]), watermark,
                     font=None, fill='black', anchor='rb')  # right-bottom alignment
        
        # Draw watermark text
        draw.text((watermark_x, watermark_y), watermark,
                 fill='white', anchor='rb')  # right-bottom alignment
    
    return np.array(img)

def get_enhanced_prompt(user_input):
    """
    Use OpenAI to enhance the user's input prompt based on video instructions
    """
    try:
        # Read video instructions
        with open('video_instruction.txt', 'r') as f:
            instructions = f.read()

        # Create a prompt for OpenAI
        system_prompt = f"""
        You are a video description expert. Use these video creation guidelines:
        {instructions}
        
        Generate a detailed, visual description that will work well for AI video generation.
        Focus on visual elements, movement, and atmosphere.
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Enhance this video description: {user_input}"}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error in prompt enhancement: {e}")
        return user_input

def generate_image_from_text(prompt):
    """Generate an image using DALL-E"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Get the image URL
        image_url = response.data[0].url
        
        # Download the image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def generate_audio_and_subtitles(text, duration):
    """Generate audio narration and subtitles from text"""
    try:
        # Generate audio using gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        audio_path = "temp_audio.mp3"
        tts.save(audio_path)
        
        # Create subtitle
        subtitle = srt.Subtitle(
            index=1,
            start=timedelta(seconds=0),
            end=timedelta(seconds=duration),
            content=text
        )
        
        # Save subtitle to file
        subtitle_path = "subtitle.srt"
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(srt.compose([subtitle]))
            
        return audio_path, subtitle_path
        
    except Exception as e:
        print(f"Error generating audio and subtitles: {e}")
        return None, None

def generate_video_from_text(prompt, duration=10, quality="standard"):
    """
    Generate video from the enhanced text prompt using DALL-E for frames with audio and subtitles
    """
    try:
        # Generate base images for key frames
        num_key_frames = 4  # Generate 4 key frames for variation
        key_frames = []
        
        for i in range(num_key_frames):
            # Modify prompt slightly for each key frame to create variation
            frame_prompt = f"{prompt} Frame {i+1}: With slight variation in perspective, lighting, or movement"
            frame_img = generate_image_from_text(frame_prompt)
            if frame_img is None:
                raise Exception(f"Failed to generate frame {i+1}")
            key_frames.append(np.array(frame_img))

        # Create interpolated frames between key frames
        frames = []
        fps = 24
        total_frames = duration * fps
        frames_per_transition = total_frames // (num_key_frames - 1)

        for i in range(num_key_frames - 1):
            start_frame = key_frames[i]
            end_frame = key_frames[i + 1]
            
            # Generate transition frames using linear interpolation
            for j in range(frames_per_transition):
                alpha = j / frames_per_transition
                interpolated_frame = (1 - alpha) * start_frame + alpha * end_frame
                frames.append(interpolated_frame.astype(np.uint8))

        # Add remaining frames from the last key frame if needed
        remaining_frames = total_frames - len(frames)
        if remaining_frames > 0:
            frames.extend([key_frames[-1]] * remaining_frames)

        # Add text overlay to all frames
        frames_with_text = [add_text_to_frame(frame, prompt) for frame in frames]

        # Create video clip with the generated frames
        video_clip = ImageSequenceClip(frames_with_text, fps=fps)
        
        # Generate audio narration
        audio_path, _ = generate_audio_and_subtitles(prompt, duration)
        
        if audio_path:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            video_clip = video_clip.set_audio(audio_clip)
        
        # Save the final video
        output_path = "generated_video.mp4"
        video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac' if audio_path else None)
        
        # Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            
        return output_path

    except Exception as e:
        print(f"Error in video generation: {e}")
        raise Exception("Video generation failed: " + str(e))
