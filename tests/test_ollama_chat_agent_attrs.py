"""Test suite for refactored OllamaChatAgent with attrs features."""
import httpx
import pytest

from app.config import ChatConfig
from app.services.chat_agent import LocalEchoAgent, OllamaChatAgent, build_chat_agent


class TestOllamaChatAgentAttrsFeatures:
    """Test the attrs library implementation and features."""

    def test_instantiation_with_valid_config(self):
        """Test basic instantiation with valid configuration."""
        agent = OllamaChatAgent(model="llama3.2", base_url="http://localhost:11434/v1")
        assert agent.model == "llama3.2"
        assert agent.base_url == "http://localhost:11434/v1"
        assert agent.timeout == 60.0

    def test_url_validation_rejects_non_http_schemes(self):
        """Test that base_url validator rejects non-HTTP schemes."""
        with pytest.raises(ValueError, match="must be HTTP"):
            OllamaChatAgent(model="llama3.2", base_url="ftp://invalid.com")

    def test_url_validation_rejects_missing_host(self):
        """Test that base_url validator rejects URLs without a host."""
        with pytest.raises(ValueError, match="must include a host"):
            OllamaChatAgent(model="llama3.2", base_url="http://")

    def test_timeout_validation_rejects_negative(self):
        """Test that timeout validator rejects negative values."""
        with pytest.raises(ValueError, match="must be positive"):
            OllamaChatAgent(
                model="llama3.2",
                base_url="http://localhost:11434/v1",
                timeout=-5.0,
            )

    def test_timeout_validation_rejects_zero(self):
        """Test that timeout validator rejects zero."""
        with pytest.raises(ValueError, match="must be positive"):
            OllamaChatAgent(
                model="llama3.2",
                base_url="http://localhost:11434/v1",
                timeout=0.0,
            )

    def test_timeout_converter_string_to_float(self):
        """Test that timeout converter coerces strings to float."""
        agent = OllamaChatAgent(
            model="llama3.2",
            base_url="http://localhost:11434/v1",
            timeout="30",  # Pass as string
        )
        assert isinstance(agent.timeout, float)
        assert agent.timeout == 30.0

    def test_factory_initialization_of_client(self):
        """Test that _client is created via factory function."""
        agent = OllamaChatAgent(model="llama3.2", base_url="http://localhost:11434/v1")
        assert hasattr(agent, "_client")
        assert isinstance(agent._client, httpx.AsyncClient)
        # httpx normalizes URLs by adding a trailing slash
        assert str(agent._client.base_url) == "http://localhost:11434/v1/"
        assert agent._client.timeout == httpx.Timeout(60.0)

    def test_slots_enabled_no_dict(self):
        """Test that slots=True prevents __dict__ attribute."""
        agent = OllamaChatAgent(model="llama3.2", base_url="http://localhost:11434/v1")
        # With slots=True, instances shouldn't have __dict__
        # (unless also inherited from a class with __dict__)
        assert not hasattr(agent, "__dict__")

    def test_equality_disabled(self):
        """Test that eq=False means instances are not equal even with same values."""
        agent1 = OllamaChatAgent(
            model="llama3.2", base_url="http://localhost:11434/v1"
        )
        agent2 = OllamaChatAgent(
            model="llama3.2", base_url="http://localhost:11434/v1"
        )
        # With eq=False, only identity comparison works
        assert agent1 != agent2
        assert agent1 == agent1

    def test_repr_hides_client(self):
        """Test that repr=False on _client hides it from string representation."""
        agent = OllamaChatAgent(model="llama3.2", base_url="http://localhost:11434/v1")
        agent_repr = repr(agent)
        # _client should not appear in repr
        assert "_client" not in agent_repr
        # But model and base_url should
        assert "llama3.2" in agent_repr
        assert "localhost" in agent_repr

    def test_build_chat_agent_factory_still_works(self):
        """Test that the build_chat_agent factory function works unchanged."""
        config = ChatConfig(backend="stub")
        local_agent = build_chat_agent(config)
        assert isinstance(local_agent, LocalEchoAgent)

    def test_build_chat_agent_ollama_backend(self):
        """Test that build_chat_agent can create OllamaChatAgent."""
        config = ChatConfig(
            backend="ollama",
            base_url="http://localhost:11434/v1",
            model="llama3.2",
        )
        agent = build_chat_agent(config)
        assert isinstance(agent, OllamaChatAgent)
        assert agent.model == "llama3.2"
        assert agent.base_url == "http://localhost:11434/v1"

    def test_https_urls_accepted(self):
        """Test that HTTPS URLs are properly accepted."""
        agent = OllamaChatAgent(
            model="llama3.2", base_url="https://api.example.com/v1"
        )
        assert agent.base_url == "https://api.example.com/v1"

    def test_metadata_annotations_present(self):
        """Test that metadata is properly attached to fields."""
        import attrs

        fields = attrs.fields(OllamaChatAgent)
        model_field = fields.model
        assert "description" in model_field.metadata
        assert "LLM model identifier" in model_field.metadata["description"]

        base_url_field = fields.base_url
        assert "description" in base_url_field.metadata
        assert "OpenAI-compatible" in base_url_field.metadata["description"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

