import os
import json
from typing import Optional

try:
    import openai
except Exception:
    openai = None


class BitNetLLM:
    """Simple wrapper providing an analysis on why an emotion changed and suggestions.

    Behavior:
    - If `OPENAI_API_KEY` is set and `openai` is installed, call OpenAI ChatCompletion.
    - Otherwise, use a small heuristic/template-based fallback.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and openai is not None:
            openai.api_key = api_key

    def analyze(self, text: str, from_emotion: Optional[str], to_emotion: Optional[str]) -> dict:
        """Return a dict with keys: reason, how_to_improve, confidence, raw (optional).

        Args:
            text: user input string (what was said)
            from_emotion: emotion before (e.g., "neutral")
            to_emotion: emotion after (e.g., "sad")
        """
        prompt = self._build_prompt(text, from_emotion, to_emotion)

        # If OpenAI available, try to call it
        if openai is not None and os.environ.get("OPENAI_API_KEY"):
            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=400,
                )
                content = resp["choices"][0]["message"]["content"].strip()
                return {"reasoning": content, "confidence": None, "raw": resp}
            except Exception as e:
                # fall through to heuristic
                pass

        # Heuristic fallback
        return self._heuristic_response(text, from_emotion, to_emotion)

    def _build_prompt(self, text: str, frm: Optional[str], to: Optional[str]) -> str:
        return (
            f"You are an assistant that explains why a listener's emotion changed.\n"
            f"Input text: \"{text}\"\nFrom emotion: {frm}\nTo emotion: {to}\n"
            "Provide a concise explanation (2-4 sentences) of likely reasons the emotion changed, "
            "and 3 practical suggestions the speaker can use to improve how they say things next time. "
            "Return results in JSON with keys: reason, suggestions."
        )

    def _heuristic_response(self, text: str, frm: Optional[str], to: Optional[str]) -> dict:
        # Basic heuristics based on keywords and emotion shifts
        lower = (text or "").lower()
        reasons = []
        suggestions = []

        # Keyword heuristics
        if any(w in lower for w in ["sorry", "apolog", "regret"]):
            reasons.append("The speaker apologized or expressed regret, which can signal vulnerability.")
            suggestions.append("Be specific about what you regret and avoid over-apologizing; offer a clear next step.")
        if any(w in lower for w in ["but", "however"]):
            reasons.append("Using contrast words like 'but' may have negated prior positive statements.")
            suggestions.append("Use 'and' instead of 'but', or rephrase to keep the positive clause intact.")
        if any(w in lower for w in ["you always", "you never", "always", "never"]):
            reasons.append("Absolute statements can feel accusatory and escalate emotions.")
            suggestions.append("Avoid absolutes; describe specific behaviors and how they affected you.")
        if any(w in lower for w in ["i feel", "i'm hurt", "upset", "angry"]):
            reasons.append("The speaker expressed feelings directly, which can make the listener empathetic or defensive depending on tone.")
            suggestions.append("Speak in 'I' statements and keep tone calm; offer context and invite dialogue.")
        if not reasons:
            reasons.append("The change may be due to tone, timing, or the listener's own context rather than the exact words.")
            suggestions.append("Ask an open question to clarify how the listener felt and show willingness to listen.")

        # Adjust suggestion count
        while len(suggestions) < 3:
            suggestions.append("Use a calm tone and check for understanding: ask 'How did that come across?' ")

        reason_text = " ".join(reasons)
        return {"reason": reason_text, "suggestions": suggestions, "confidence": 0.4}


def get_default_bitnet():
    return BitNetLLM()
