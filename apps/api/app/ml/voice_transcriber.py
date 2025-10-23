"""Voice Transcription Service using OpenAI Whisper.

Handles voice message transcription with automatic language detection.
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

import whisper
import torch

logger = logging.getLogger(__name__)


class VoiceTranscriber:
    """Transcribes voice messages using Whisper model."""

    def __init__(self, model_size: str = "base"):
        """Initialize voice transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                       - tiny: Fastest, least accurate (~1GB RAM)
                       - base: Good balance (~1GB RAM)
                       - small: Better accuracy (~2GB RAM)
                       - medium: High accuracy (~5GB RAM)
                       - large: Best accuracy (~10GB RAM)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()

    def _load_model(self):
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper {self.model_size} model on {self.device}...")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info(f"✅ Whisper {self.model_size} model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> Dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (mp3, wav, m4a, ogg, etc.)
            language: ISO 639-1 language code (e.g., "en", "es", "hi")
                     If None, will auto-detect
            task: "transcribe" or "translate" (translate converts to English)

        Returns:
            Dictionary with transcription result:
            {
                "text": "transcribed text",
                "language": "en",
                "confidence": 0.95,
                "duration": 12.5,
                "segments": [...],  # Word-level timestamps
            }
        """
        try:
            if not Path(audio_path).exists():
                return {
                    "text": "",
                    "error": f"Audio file not found: {audio_path}",
                }

            logger.info(f"Transcribing audio: {audio_path}")

            # Transcribe with Whisper
            options = {
                "task": task,
                "fp16": torch.cuda.is_available(),  # Use fp16 on GPU
            }

            if language:
                options["language"] = language

            result = self.model.transcribe(audio_path, **options)

            # Extract key information
            transcription = {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "duration": self._calculate_duration(result),
                "segments": self._extract_segments(result),
            }

            # Calculate confidence from segment probabilities
            if result.get("segments"):
                avg_confidence = sum(
                    seg.get("no_speech_prob", 0) for seg in result["segments"]
                ) / len(result["segments"])
                transcription["confidence"] = round(1 - avg_confidence, 4)
            else:
                transcription["confidence"] = 0.0

            logger.info(
                f"✅ Transcribed {transcription['duration']}s audio "
                f"({transcription['language']}): {transcription['text'][:100]}..."
            )

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {
                "text": "",
                "error": str(e),
            }

    def transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.ogg",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transcribe audio from bytes (e.g., WhatsApp voice message).

        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for extension detection)
            language: ISO 639-1 language code

        Returns:
            Transcription result dictionary
        """
        try:
            # Save bytes to temporary file
            suffix = Path(filename).suffix or ".ogg"
            with tempfile.NamedTemporaryFile(
                suffix=suffix, delete=False
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            # Transcribe
            result = self.transcribe(temp_path, language=language)

            # Clean up temp file
            try:
                Path(temp_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

            return result

        except Exception as e:
            logger.error(f"Transcription from bytes failed: {e}")
            return {
                "text": "",
                "error": str(e),
            }

    def translate_to_english(
        self, audio_path: str
    ) -> Dict[str, Any]:
        """Transcribe and translate audio to English.

        Args:
            audio_path: Path to audio file

        Returns:
            Translation result with original language detected
        """
        return self.transcribe(audio_path, task="translate")

    def detect_language(self, audio_path: str) -> str:
        """Detect language of audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            ISO 639-1 language code (e.g., "en", "es", "hi")
        """
        try:
            # Load audio
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)

            # Detect language
            mel = whisper.log_mel_spectrogram(audio).to(self.device)
            _, probs = self.model.detect_language(mel)

            detected_lang = max(probs, key=probs.get)
            confidence = probs[detected_lang]

            logger.info(
                f"Detected language: {detected_lang} (confidence: {confidence:.2f})"
            )

            return detected_lang

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "unknown"

    def _calculate_duration(self, result: Dict[str, Any]) -> float:
        """Calculate audio duration from segments."""
        if result.get("segments"):
            last_segment = result["segments"][-1]
            return round(last_segment.get("end", 0), 2)
        return 0.0

    def _extract_segments(self, result: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Extract simplified segment information."""
        if not result.get("segments"):
            return []

        segments = []
        for seg in result["segments"]:
            segments.append(
                {
                    "start": round(seg.get("start", 0), 2),
                    "end": round(seg.get("end", 0), 2),
                    "text": seg.get("text", "").strip(),
                }
            )

        return segments

    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages.

        Returns:
            List of ISO 639-1 language codes
        """
        return [
            "en",  # English
            "zh",  # Chinese
            "de",  # German
            "es",  # Spanish
            "ru",  # Russian
            "ko",  # Korean
            "fr",  # French
            "ja",  # Japanese
            "pt",  # Portuguese
            "tr",  # Turkish
            "pl",  # Polish
            "ca",  # Catalan
            "nl",  # Dutch
            "ar",  # Arabic
            "sv",  # Swedish
            "it",  # Italian
            "id",  # Indonesian
            "hi",  # Hindi
            "fi",  # Finnish
            "vi",  # Vietnamese
            "he",  # Hebrew
            "uk",  # Ukrainian
            "el",  # Greek
            "ms",  # Malay
            "cs",  # Czech
            "ro",  # Romanian
            "da",  # Danish
            "hu",  # Hungarian
            "ta",  # Tamil
            "no",  # Norwegian
            "th",  # Thai
            "ur",  # Urdu
            "hr",  # Croatian
            "bg",  # Bulgarian
            "lt",  # Lithuanian
            "la",  # Latin
            "mi",  # Maori
            "ml",  # Malayalam
            "cy",  # Welsh
            "sk",  # Slovak
            "te",  # Telugu
            "fa",  # Persian
            "lv",  # Latvian
            "bn",  # Bengali
            "sr",  # Serbian
            "az",  # Azerbaijani
            "sl",  # Slovenian
            "kn",  # Kannada
            "et",  # Estonian
            "mk",  # Macedonian
            "br",  # Breton
            "eu",  # Basque
            "is",  # Icelandic
            "hy",  # Armenian
            "ne",  # Nepali
            "mn",  # Mongolian
            "bs",  # Bosnian
            "kk",  # Kazakh
            "sq",  # Albanian
            "sw",  # Swahili
            "gl",  # Galician
            "mr",  # Marathi
            "pa",  # Punjabi
            "si",  # Sinhala
            "km",  # Khmer
            "sn",  # Shona
            "yo",  # Yoruba
            "so",  # Somali
            "af",  # Afrikaans
            "oc",  # Occitan
            "ka",  # Georgian
            "be",  # Belarusian
            "tg",  # Tajik
            "sd",  # Sindhi
            "gu",  # Gujarati
            "am",  # Amharic
            "yi",  # Yiddish
            "lo",  # Lao
            "uz",  # Uzbek
            "fo",  # Faroese
            "ht",  # Haitian Creole
            "ps",  # Pashto
            "tk",  # Turkmen
            "nn",  # Nynorsk
            "mt",  # Maltese
            "sa",  # Sanskrit
            "lb",  # Luxembourgish
            "my",  # Myanmar
            "bo",  # Tibetan
            "tl",  # Tagalog
            "mg",  # Malagasy
            "as",  # Assamese
            "tt",  # Tatar
            "haw",  # Hawaiian
            "ln",  # Lingala
            "ha",  # Hausa
            "ba",  # Bashkir
            "jw",  # Javanese
            "su",  # Sundanese
        ]


# Global singleton instance
_voice_transcriber: Optional[VoiceTranscriber] = None


@lru_cache(maxsize=1)
def get_voice_transcriber(model_size: str = "base") -> VoiceTranscriber:
    """Get or create global voice transcriber instance."""
    global _voice_transcriber
    if _voice_transcriber is None:
        _voice_transcriber = VoiceTranscriber(model_size=model_size)
    return _voice_transcriber
