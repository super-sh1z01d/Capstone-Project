import json

from backend.gemini_client import GeminiClient, build_synthesis_prompt


def test_gemini_client_posts_generate_content_request():
    captured = {}

    def fake_transport(url, payload, timeout):
        captured["url"] = url
        captured["payload"] = payload
        captured["timeout"] = timeout
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Gemini synthesis: investigate the invite step first.",
                            }
                        ]
                    }
                }
            ]
        }

    client = GeminiClient(api_key="test-key", model="gemini-2.5-flash", transport=fake_transport)

    text = client.generate_text("Summarize this report.")

    assert text == "Gemini synthesis: investigate the invite step first."
    assert (
        captured["url"]
        == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=test-key"
    )
    assert captured["payload"]["contents"][0]["parts"][0]["text"] == "Summarize this report."
    assert captured["payload"]["generationConfig"]["temperature"] == 0.2
    assert captured["timeout"] == 20.0


def test_build_synthesis_prompt_contains_tool_evidence(sample_report):
    prompt = build_synthesis_prompt(sample_report)

    assert "Activation moved from" in prompt
    assert "Metric Analyst" in prompt
    assert "Return a concise executive synthesis" in prompt
    json.dumps(prompt)
