import os
import tempfile
import streamlit as st
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from pytube import YouTube
from pydub import AudioSegment

def transcribe_audio(audio_file_path, language):
    recognizer = sr.Recognizer()
    audio_data = sr.AudioFile(audio_file_path)
    with audio_data as source:
        audio = recognizer.record(source) 
    
    try:
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        return "Google Web Speech API could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"

def process_video(video_file_path, language):
    video = VideoFileClip(video_file_path)
    audio = video.audio
    audio_file = "temp_audio.wav"
    audio.write_audiofile(audio_file)
    return transcribe_audio(audio_file, language)

def process_youtube(youtube_link, language):
    yt = YouTube(youtube_link)
    video = yt.streams.filter(file_extension='mp4').first()
    video.download(filename='temp_video.mp4')
    return process_video('temp_video.mp4', language)

def create_app():
    st.title('Transcription App')
    st.subheader('Upload your audio or video file')
    
    uploaded_file = st.file_uploader("Choose a file", type=['mp3', 'mp4', 'wav', 'flv', 'avi', 'mov'])
    language = st.selectbox('Select Language', ['en-US', 'es-ES', 'fr-FR'])  # Add languages as needed
    
    st.subheader('Or input a YouTube link')
    youtube_link = st.text_input("Enter the YouTube link here")
    
    if uploaded_file:
        file_details = {"FileName":uploaded_file.name,"FileType":uploaded_file.type,"FileSize":uploaded_file.size}
        st.write(file_details)
        
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_details['FileType'].split('/')[-1]}") 
        tfile.write(uploaded_file.read())
        
        # Convert audio to wav format
        audio = AudioSegment.from_file(tfile.name, format=file_details['FileType'].split('/')[-1])
        audio.export("temp_audio.wav", format="wav")
        
        st.write("File uploaded. Proceeding to transcription...")
        transcription = transcribe_audio("temp_audio.wav", language)
        st.write("Transcription:", transcription)
        
        st.download_button("Download Transcription", data=transcription, file_name='transcription.txt', mime='text/plain')
        
    elif youtube_link:
        st.write("YouTube link provided. Proceeding to transcription...")
        transcription = process_youtube(youtube_link, language)
        st.write("Transcription:", transcription)
        
        st.download_button("Download Transcription", data=transcription, file_name='transcription.txt', mime='text/plain')

if __name__ == "__main__":
    create_app()
