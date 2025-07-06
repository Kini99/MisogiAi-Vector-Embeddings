import os
import whisper
import tempfile
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from typing import Tuple, Optional
import time
from app.config import settings

class VideoProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def extract_audio(self, video_path: str) -> str:
        """Extract audio from video file"""
        try:
            video = VideoFileClip(video_path)
            audio_path = video_path.replace('.mp4', '.wav').replace('.avi', '.wav').replace('.mov', '.wav')
            
            # Extract audio
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
            return audio_path
        except Exception as e:
            raise Exception(f"Error extracting audio: {str(e)}")
    
    def transcribe_audio(self, audio_path: str) -> Tuple[str, float, str]:
        """Transcribe audio using Whisper"""
        try:
            start_time = time.time()
            
            # Transcribe with timestamps
            result = self.model.transcribe(
                audio_path,
                verbose=False,
                word_timestamps=True,
                language="en"
            )
            
            processing_time = time.time() - start_time
            
            # Format transcript with timestamps
            transcript = self._format_transcript_with_timestamps(result)
            
            return transcript, processing_time, result.get("language", "en")
            
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def _format_transcript_with_timestamps(self, result: dict) -> str:
        """Format transcript with timestamps"""
        transcript_parts = []
        
        for segment in result["segments"]:
            start_time = self._format_timestamp(segment["start"])
            end_time = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            transcript_parts.append(f"[{start_time} - {end_time}] {text}")
        
        return "\n".join(transcript_parts)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds"""
        try:
            video = VideoFileClip(video_path)
            duration = video.duration
            video.close()
            return duration
        except Exception as e:
            raise Exception(f"Error getting video duration: {str(e)}")
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    def cleanup_temp_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass 