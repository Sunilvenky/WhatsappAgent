"""Translation Service using Google Translate API.

Provides automatic language detection and translation for multilingual campaigns.
"""

import logging
from typing import Dict, Any, Optional, List
from functools import lru_cache

from googletrans import Translator as GoogleTranslator, LANGUAGES
from langdetect import detect, detect_langs, LangDetectException

logger = logging.getLogger(__name__)


class Translator:
    """Translates text between languages using Google Translate."""

    def __init__(self):
        """Initialize translator."""
        self.translator = GoogleTranslator()
        self.supported_languages = LANGUAGES

    def translate(
        self,
        text: str,
        target_language: str = "en",
        source_language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Translate text to target language.

        Args:
            text: Text to translate
            target_language: ISO 639-1 target language code (e.g., "en", "es", "hi")
            source_language: ISO 639-1 source language code (auto-detect if None)

        Returns:
            Dictionary with translation result:
            {
                "translated_text": "Hello world",
                "source_language": "es",
                "target_language": "en",
                "confidence": 0.95,
                "original_text": "Hola mundo"
            }
        """
        if not text or not text.strip():
            return {
                "translated_text": "",
                "error": "Empty text provided",
            }

        try:
            # Validate target language
            if target_language not in self.supported_languages:
                return {
                    "translated_text": text,
                    "error": f"Unsupported target language: {target_language}",
                }

            # Auto-detect source language if not provided
            if not source_language:
                detected = self.detect_language(text)
                source_language = detected["language"]

            # Skip translation if source and target are the same
            if source_language == target_language:
                return {
                    "translated_text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "confidence": 1.0,
                    "original_text": text,
                    "skipped": True,
                }

            # Translate
            result = self.translator.translate(
                text,
                src=source_language,
                dest=target_language,
            )

            return {
                "translated_text": result.text,
                "source_language": result.src,
                "target_language": result.dest,
                "confidence": getattr(result, "confidence", None),
                "original_text": text,
            }

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "translated_text": text,  # Return original on error
                "error": str(e),
                "original_text": text,
            }

    def translate_batch(
        self,
        texts: List[str],
        target_language: str = "en",
        source_language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Translate multiple texts efficiently.

        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)

        Returns:
            List of translation results
        """
        if not texts:
            return []

        results = []
        for text in texts:
            result = self.translate(
                text,
                target_language=target_language,
                source_language=source_language,
            )
            results.append(result)

        return results

    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with detection result:
            {
                "language": "en",
                "language_name": "english",
                "confidence": 0.95,
                "all_probabilities": [...]
            }
        """
        if not text or not text.strip():
            return {
                "language": "unknown",
                "confidence": 0.0,
                "error": "Empty text provided",
            }

        try:
            # Detect with langdetect (more reliable than googletrans)
            detected_lang = detect(text)

            # Get all probabilities
            all_langs = detect_langs(text)

            # Find confidence for detected language
            confidence = 0.0
            for lang in all_langs:
                if lang.lang == detected_lang:
                    confidence = lang.prob
                    break

            return {
                "language": detected_lang,
                "language_name": self.supported_languages.get(
                    detected_lang, "unknown"
                ),
                "confidence": round(confidence, 4),
                "all_probabilities": [
                    {
                        "language": lang.lang,
                        "probability": round(lang.prob, 4),
                    }
                    for lang in all_langs
                ],
            }

        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}")
            return {
                "language": "unknown",
                "confidence": 0.0,
                "error": str(e),
            }

    def translate_message_for_campaign(
        self,
        message: str,
        contact_language: str,
        campaign_language: str = "en",
    ) -> Dict[str, Any]:
        """Translate campaign message to contact's preferred language.

        Args:
            message: Campaign message (in campaign_language)
            contact_language: Contact's preferred language
            campaign_language: Original message language

        Returns:
            Translation result with metadata
        """
        # Skip if languages match
        if contact_language == campaign_language:
            return {
                "message": message,
                "translated": False,
                "source_language": campaign_language,
                "target_language": contact_language,
            }

        # Translate
        result = self.translate(
            message,
            target_language=contact_language,
            source_language=campaign_language,
        )

        return {
            "message": result.get("translated_text", message),
            "translated": True,
            "source_language": result.get("source_language"),
            "target_language": result.get("target_language"),
            "confidence": result.get("confidence"),
            "original_message": message,
        }

    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names.

        Returns:
            Dictionary mapping language codes to names:
            {"en": "english", "es": "spanish", ...}
        """
        return self.supported_languages.copy()

    def get_popular_languages(self) -> List[Dict[str, str]]:
        """Get list of popular languages for WhatsApp marketing.

        Returns:
            List of language dictionaries with code and name
        """
        popular = [
            "en",  # English
            "es",  # Spanish
            "hi",  # Hindi
            "pt",  # Portuguese
            "zh-cn",  # Chinese (Simplified)
            "ar",  # Arabic
            "bn",  # Bengali
            "ru",  # Russian
            "ja",  # Japanese
            "pa",  # Punjabi
            "de",  # German
            "jw",  # Javanese
            "ko",  # Korean
            "fr",  # French
            "te",  # Telugu
            "mr",  # Marathi
            "tr",  # Turkish
            "ta",  # Tamil
            "vi",  # Vietnamese
            "ur",  # Urdu
        ]

        return [
            {
                "code": code,
                "name": self.supported_languages.get(code, "Unknown"),
            }
            for code in popular
            if code in self.supported_languages
        ]

    def translate_with_fallback(
        self,
        text: str,
        target_languages: List[str],
    ) -> Dict[str, str]:
        """Translate text to multiple languages with fallback.

        Args:
            text: Text to translate
            target_languages: List of target language codes (in priority order)

        Returns:
            Dictionary mapping language codes to translated texts:
            {"en": "Hello", "es": "Hola", ...}
        """
        translations = {}

        for lang in target_languages:
            result = self.translate(text, target_language=lang)
            if "error" not in result:
                translations[lang] = result["translated_text"]
            else:
                logger.warning(
                    f"Failed to translate to {lang}: {result.get('error')}"
                )
                translations[lang] = text  # Fallback to original

        return translations

    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported.

        Args:
            language_code: ISO 639-1 language code

        Returns:
            True if supported, False otherwise
        """
        return language_code in self.supported_languages


# Global singleton instance
_translator: Optional[Translator] = None


@lru_cache(maxsize=1)
def get_translator() -> Translator:
    """Get or create global translator instance."""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator
