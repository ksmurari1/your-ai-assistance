import unittest
from unittest.mock import patch
from guardrails import check_text_with_moderation

class FakeModerationResponse:
    def __init__(self, payload):
        self.payload = payload
        self.results = [FakeResult(payload["results"][0])]

    def model_dump(self):
        return self.payload

class FakeResult:
    def __init__(self, payload):
        self.payload = payload
    def model_dump(self):
        return self.payload

class FakeClient:
    def __init__(self, response):
        self.moderations = FakeModerations(response)

class FakeModerations:
    def __init__(self, response):
        self.response = response
    def create(self, **kwargs):
        return self.response

def fake_response(flagged=False, category=None):
    categories = {"sexual": False, "violence": False, "self-harm": False, "illicit": False}
    if category:
        categories[category] = True
    return FakeModerationResponse({"results": [{
        "flagged": flagged,
        "categories": categories,
        "category_scores": {},
    }]})

class GuardrailTests(unittest.TestCase):
    @patch("guardrails.OpenAI")
    def test_safe_text_allowed(self, openai_mock):
        openai_mock.return_value = FakeClient(fake_response())
        result = check_text_with_moderation("Five healthy breakfast ideas")
        self.assertTrue(result.allowed)

    @patch("guardrails.OpenAI")
    def test_flagged_sexual_text_blocked(self, openai_mock):
        openai_mock.return_value = FakeClient(fake_response(flagged=True, category="sexual"))
        result = check_text_with_moderation("explicit content")
        self.assertFalse(result.allowed)
        self.assertIn("sexual", result.reason)

    def test_empty_text_blocked_without_api(self):
        result = check_text_with_moderation("  ")
        self.assertFalse(result.allowed)
        self.assertIn("Empty input", result.reason)

if __name__ == "__main__":
    unittest.main()
