from agentlens_ai.privacy import REDACTED, TracePrivacyConfig, sanitize_inputs, sanitize_output, sanitize_value


def test_sanitize_value_redacts_sensitive_keys() -> None:
    payload = {
        "user": "example",
        "api_key": "abc123",
        "nested": {"password": "secret"},
    }

    sanitized = sanitize_value(payload)

    assert sanitized["api_key"] == REDACTED
    assert sanitized["nested"]["password"] == REDACTED
    assert sanitized["user"] == "'example'"


def test_sanitize_inputs_can_be_disabled() -> None:
    config = TracePrivacyConfig(capture_inputs=False)

    assert sanitize_inputs(("hello",), {"token": "abc"}, config) is None


def test_sanitize_output_can_be_disabled() -> None:
    config = TracePrivacyConfig(capture_outputs=False)

    assert sanitize_output({"result": "hello"}, config) is None
