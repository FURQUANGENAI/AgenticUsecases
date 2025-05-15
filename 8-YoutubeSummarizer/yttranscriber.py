import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("API key not found in environment variables.")
else:
    genai.configure(api_key=api_key)

# Prompt for summarization
prompt = """Summarize the YouTube video transcript in 250 words or less, focusing on key points: """

# Function to extract video ID from YouTube URL
def extract_video_id(youtube_video_url):
    try:
        parsed_url = urlparse(youtube_video_url)
        if parsed_url.hostname in ['youtu.be']:
            return parsed_url.path[1:]  # Extract video ID from short URLs
        elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]  # Extract video ID from standard URLs
        else:
            raise ValueError("Invalid YouTube URL")
    except Exception as e:
        st.error(f"Error parsing URL: {str(e)}")
        return None

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        # Truncate transcript to reduce token usage
        transcript = transcript[:10000]  # Limit to ~10,000 characters
        return transcript
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

# Function to generate summary using Gemini with retry logic
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted)
)
def generate_gemini_content(transcript_text, prompt):
    try:
        # Use gemini-1.5-flash for higher quota limits
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except google.api_core.exceptions.ResourceExhausted as e:
        st.warning(f"Quota exceeded: {str(e)}. Retrying...")
        raise
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg",  use_container_width=True)
    else:
        st.warning("Please enter a valid YouTube URL.")

if st.button("Get Detailed Notes"):
    if youtube_link:
        with st.spinner("Fetching transcript and generating summary..."):
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                summary = generate_gemini_content(transcript_text, prompt)
                if summary:
                    st.markdown("## Detailed Notes:")
                    st.write(summary)
                else:
                    st.error("Failed to generate summary.")
            else:
                st.error("Failed to fetch transcript.")
    else:
        st.warning("Please enter a YouTube video link.")