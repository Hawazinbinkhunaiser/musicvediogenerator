import streamlit as st
from moviepy.editor import AudioFileClip, TextClip, ColorClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import tempfile
import os

# Optional: For lyrics fetching
# import lyricsgenius

st.title("Lyrics Music Video Generator 🎬🎵")

# Step 1: Upload audio file
audio_file = st.file_uploader("Upload a music track (mp3, wav, etc.):", type=["mp3", "wav", "m4a"])

# Step 2: Enter or fetch lyrics
st.markdown("**Enter lyrics (one line per row, or paste full lyrics):**")

lyrics_text = st.text_area("Lyrics:", height=200, placeholder="Paste your lyrics here...")

# Optionally, you can fetch lyrics using a Genius API key
# st.markdown("Or fetch lyrics automatically:")
# genius_token = st.text_input("Enter your Genius API token:")
# if genius_token and st.button("Fetch Lyrics"):
#     genius = lyricsgenius.Genius(genius_token)
#     title = st.text_input("Song Title")
#     artist = st.text_input("Artist")
#     if title and artist:
#         song = genius.search_song(title, artist)
#         lyrics_text = song.lyrics if song else ""
#         st.text_area("Lyrics:", value=lyrics_text, height=200)

# Step 3: Set video style
bg_color = st.color_picker("Choose background color:", "#222244")
font_size = st.slider("Font size:", 20, 80, 40)
font_color = st.color_picker("Choose font color:", "#FFFFFF")
duration_per_line = st.slider("Seconds per lyric line (if no timestamps):", 2, 10, 4)

# Step 4: Generate video
if st.button("Generate Lyrics Video"):
    if not audio_file or not lyrics_text.strip():
        st.warning("Please upload an audio file and enter lyrics.")
    else:
        with st.spinner("Generating video..."):
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tmp_audio.write(audio_file.read())
                audio_path = tmp_audio.name

            # Prepare lyrics lines
            lyrics_lines = [line.strip() for line in lyrics_text.split("\n") if line.strip()]
            n_lines = len(lyrics_lines)
            
            # Get audio duration
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            per_line = min(duration_per_line, audio_duration / max(1, n_lines))
            
            # Generate subtitles list [(start, end, text), ...]
            subs = []
            curr_time = 0
            for line in lyrics_lines:
                end_time = curr_time + per_line
                if end_time > audio_duration:
                    end_time = audio_duration
                subs.append(((curr_time, end_time), line))
                curr_time = end_time
                if curr_time >= audio_duration:
                    break

            # Subtitle generator function
            def make_textclip(txt):
                return TextClip(txt, fontsize=font_size, color=font_color, font="Arial", size=(1280, 720), method='caption', align='center', bg_color=bg_color)
            
            # Make subtitles clip
            subtitles = SubtitlesClip(subs, make_textclip)
            
            # Make background and overlay subtitles
            video = ColorClip(size=(1280, 720), color=tuple(int(bg_color[i:i+2],16) for i in (1,3,5)), duration=audio_duration)
            video = video.set_audio(audio_clip)
            final = CompositeVideoClip([video, subtitles.set_position(('center','center'))])
            
            # Write to temp file
            outpath = tempfile.mktemp(suffix=".mp4")
            final.write_videofile(outpath, fps=24, codec="libx264", audio_codec="aac", threads=2, verbose=False, logger=None)
            
            # Display video
            with open(outpath, "rb") as f:
                st.video(f.read())

            # Clean up temp files
            os.remove(audio_path)
            os.remove(outpath)
