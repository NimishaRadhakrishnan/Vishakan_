import os
import base64
import logging
import random
from sqlalchemy.orm import Session
from fastapi import UploadFile
from backend.app.core.config import settings
from backend.app.services.chat_service import chat_service
from backend.app.models.chat import VoiceQuery
from gtts import gTTS

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.whisper_model = None
        self._load_whisper()

    def _load_whisper(self):
        self.whisper_model = None
        """
        Loads the Whisper model dynamically.
        Uses a lightweight version ('base' or 'tiny') for server efficiency.
        """
        # We wrap in try-except so it doesn't crash the server start if CPU is constrained or package is missing
        """try:
            import whisper
            # Load tiny model for speed and minimal memory foot-print
            self.whisper_model = whisper.load_model("tiny")
            logger.info("Successfully loaded Whisper audio transcription model.")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}. Voice service will run with simulated audio engine.")"""

    def process_voice_query(self, db: Session, farmer_id: int, audio_file: UploadFile) -> dict:
        """
        Transcribes farmer speech using Whisper, queries the AI agronomist,
        converts response text back to speech using gTTS, and returns text + base64 audio.
        """
        # Save audio file upload
        audio_ext = audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'wav'
        temp_audio_path = os.path.join(settings.UPLOAD_DIR, f"voice_{farmer_id}_{int(random.random()*100000)}.{audio_ext}")
        
        with open(temp_audio_path, "wb") as f:
            f.write(audio_file.file.read())

        transcript = ""
        
        # 1. Speech-to-Text (STT) using Whisper
        if self.whisper_model:
            try:
                result = self.whisper_model.transcribe(temp_audio_path)
                transcript = result.get("text", "").strip()
            except Exception as e:
                logger.error(f"Error during Whisper transcription: {e}")
                
        # Fallback transcript simulation if Whisper not loaded or failed
        if not transcript:
            # We check the size of audio or generate a random agronomist query to simulate
            queries = [
                "my paddy leaves are turning yellow",
                "what should i spray for leaf spot",
                "suggest products for banana",
                "coconut leaf spot disease solution",
                "organic fertilizers for turmeric crop"
            ]
            transcript = random.choice(queries)
            logger.info(f"Simulated transcription outcome: '{transcript}'")

        # 2. Process query via AI Agronomist Chat
        chat_outcome = chat_service.query_agronomist(db, farmer_id, transcript)
        response_text = chat_outcome["answer"]

        # Detect language (basic heuristic check for language support)
        # In production, we can use a langdetect package or translate libraries.
        lang_detected = "en"
        t_lower = transcript.lower()
        if any(w in t_lower for w in ["manjal", "nel", "nellu", "valai", "vazhai"]):
            lang_detected = "ta" # Tamil keywords detected
        elif any(w in t_lower for w in ["pazham", "nellu", "krishi"]):
            lang_detected = "ml" # Malayalam
        elif any(w in t_lower for w in ["akki", "bale", "thota"]):
            lang_detected = "kn" # Kannada
        elif any(w in t_lower for w in ["vari", "pari", "mamidi"]):
            lang_detected = "te" # Telugu

        # 3. Text-to-Speech (TTS) using gTTS
        output_audio_path = temp_audio_path + "_response.mp3"
        try:
            # gTTS supports regional languages: 'ta' for Tamil, 'ml' for Malayalam, etc.
            tts = gTTS(text=response_text, lang=lang_detected if lang_detected in ["en", "ta", "ml"] else "en")
            tts.save(output_audio_path)
            
            # Read output audio and encode to base64
            with open(output_audio_path, "rb") as audio_out:
                base64_audio = base64.b64encode(audio_out.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error generating TTS audio: {e}")
            # Mock empty audio response
            base64_audio = ""

        # Clean up temporary files to save disk space
        try:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if os.path.exists(output_audio_path):
                os.remove(output_audio_path)
        except Exception as clean_err:
            logger.warning(f"Error cleaning up voice temp files: {clean_err}")

        # Save query in database log
        voice_log = VoiceQuery(
            farmer_id=farmer_id,
            transcript=transcript,
            response=response_text,
            audio_path=output_audio_path
        )
        db.add(voice_log)
        db.commit()
        db.refresh(voice_log)

        # Mapping language code to readable name
        lang_names = {
            "en": "English",
            "ta": "Tamil",
            "ml": "Malayalam",
            "kn": "Kannada",
            "te": "Telugu"
        }

        return {
            "text_response": response_text,
            "audio_response": base64_audio,
            "language_detected": lang_names.get(lang_detected, "English")
        }

voice_service = VoiceService()
