import os
import time
from dotenv import load_dotenv

load_dotenv()


class GeminiDocumentGenerator:
    """Gemini-powered legal document drafting with retry handling."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        self.max_retries = 3
        self.retry_delays = [3, 7, 15]

    def generate_document(
        self,
        document_type,
        parties,
        terms,
        effective_date,
        jurisdiction,
        additional_instructions=""
    ):
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to your .env file and restart the backend."
            )

        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)

            prompt = f"""Draft a clear, editable first draft of a {document_type} using the details below.

Parties: {parties}

Effective date: {effective_date}

Jurisdiction: {jurisdiction}

Requested terms (preserve their meaning): {terms}

Additional instructions: {additional_instructions or 'None'}

Requirements:
- Use a professional title and numbered headings.
- Include definitions, obligations, term/termination, confidentiality (if relevant), dispute resolution, governing law, signature blocks, and other clauses appropriate to this document.
- Mark missing facts as [TO BE COMPLETED]; do not invent names, dates, amounts, or legal requirements.
- Clearly label this as a draft for review.
- Do not claim it is legally valid or a substitute for advice from a qualified lawyer.

Return only the document text."""

            last_error = None

            for attempt in range(self.max_retries + 1):

                try:
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt
                    )

                    text = getattr(response, "text", None)

                    if not text:
                        raise RuntimeError(
                            "Gemini returned an empty response. "
                            "Please try again."
                        )

                    return text.strip()

                except Exception as exc:

                    last_error = exc
                    error_text = str(exc).upper()

                    # Quota / rate limit error:
                    # Do not waste retries when Gemini explicitly
                    # says the quota has been exceeded.
                    if (
                        "429" in error_text
                        or "RESOURCE_EXHAUSTED" in error_text
                    ):
                        raise RuntimeError(
                            "Gemini API quota has been exceeded. "
                            "Please wait and try again later, "
                            "or check your Gemini API usage and billing limits."
                        ) from exc

                    # Temporary server errors can be retried.
                    retryable = (
                        "503" in error_text
                        or "UNAVAILABLE" in error_text
                        or "500" in error_text
                        or "INTERNAL" in error_text
                    )

                    if attempt >= self.max_retries:
                        break

                    if not retryable:
                        raise RuntimeError(
                            f"Gemini request failed: {exc}"
                        ) from exc

                    delay = self.retry_delays[attempt]

                    print(
                        f"Gemini temporary error detected "
                        f"(attempt {attempt + 1}/{self.max_retries + 1}). "
                        f"Retrying in {delay} seconds..."
                    )

                    time.sleep(delay)

            raise RuntimeError(
                f"Gemini request failed after "
                f"{self.max_retries + 1} attempts: {last_error}"
            ) from last_error

        except RuntimeError:
            raise

        except Exception as exc:
            raise RuntimeError(
                f"Gemini request failed: {exc}"
            ) from exc