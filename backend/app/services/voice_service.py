import logging
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Voice AI Service for CampusConnect:
    - Deepgram Speech-to-Text (STT) for voice input processing
    - ElevenLabs Text-to-Speech (TTS) for natural voice assistant output
    """

    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (clear natural conversational voice)

    @classmethod
    async def transcribe_audio(
        cls,
        audio_bytes: bytes,
        content_type: str = "audio/wav"
    ) -> Dict[str, Any]:
        """
        Transcribes speech using Deepgram Nova-2 API.
        """
        if not settings.DEEPGRAM_API_KEY:
            return {
                "status": "error",
                "error": "DEEPGRAM_API_KEY is not configured.",
                "transcript": ""
            }

        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
        headers = {
            "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
            "Content-Type": content_type
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, headers=headers, content=audio_bytes)
                if res.status_code == 200:
                    data = res.json()
                    channels = data.get("results", {}).get("channels", [])
                    if channels:
                        alts = channels[0].get("alternatives", [])
                        if alts:
                            transcript = alts[0].get("transcript", "").strip()
                            confidence = alts[0].get("confidence", 0.0)
                            return {
                                "status": "success",
                                "transcript": transcript,
                                "confidence": confidence,
                                "provider": "Deepgram (Nova-2)"
                            }
                logger.warning(f"Deepgram transcription error: HTTP {res.status_code} - {res.text[:150]}")
                return {
                    "status": "error",
                    "error": f"Deepgram returned HTTP {res.status_code}",
                    "transcript": ""
                }
        except Exception as e:
            logger.warning(f"Deepgram transcription exception: {e}")
            return {
                "status": "error",
                "error": str(e),
                "transcript": ""
            }

    @classmethod
    async def synthesize_speech(
        cls,
        text: str,
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes speech using ElevenLabs API.
        Returns audio bytes or error status.
        """
        if not settings.ELEVENLABS_API_KEY:
            return {
                "status": "error",
                "error": "ELEVENLABS_API_KEY is not configured.",
                "audio_bytes": None
            }

        target_voice = voice_id or cls.DEFAULT_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        payload = {
            "text": text[:1000],  # Clip to 1000 chars for responsive audio
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    return {
                        "status": "success",
                        "audio_bytes": res.content,
                        "content_type": "audio/mpeg",
                        "provider": "ElevenLabs"
                    }
                logger.warning(f"ElevenLabs synthesis error: HTTP {res.status_code} - {res.text[:150]}")
                return {
                    "status": "error",
                    "error": f"ElevenLabs returned HTTP {res.status_code}",
                    "audio_bytes": None
                }
        except Exception as e:
            logger.warning(f"ElevenLabs synthesis exception: {e}")
            return {
                "status": "error",
                "error": str(e),
                "audio_bytes": None
            }

