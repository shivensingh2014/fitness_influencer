"""
Tests for all 5 CrewAI agents – validates their structure, attributes,
and LLM configuration without making any API calls.
"""
import sys
from pathlib import Path

import pytest
from crewai import Agent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestResearcher:
    """Tests for agents/researcher.py."""

    def test_is_agent_instance(self):
        from agents.researcher import researcher
        assert isinstance(researcher, Agent)

    def test_has_google_search_tool(self):
        from agents.researcher import researcher
        tool_names = [t.name for t in researcher.tools]
        assert "google_search" in tool_names

    def test_delegation_disabled(self):
        from agents.researcher import researcher
        assert researcher.allow_delegation is False

    def test_max_iter_is_3(self):
        from agents.researcher import researcher
        assert researcher.max_iter == 3

    def test_has_role(self):
        from agents.researcher import researcher
        assert researcher.role and len(researcher.role) > 5


class TestPromptCreator:
    """Tests for agents/prompt_creator.py."""

    def test_is_agent_instance(self):
        from agents.prompt_creator import prompt_creator
        assert isinstance(prompt_creator, Agent)

    def test_has_no_tools(self):
        from agents.prompt_creator import prompt_creator
        assert len(prompt_creator.tools) == 0

    def test_delegation_disabled(self):
        from agents.prompt_creator import prompt_creator
        assert prompt_creator.allow_delegation is False

    def test_max_iter_is_3(self):
        from agents.prompt_creator import prompt_creator
        assert prompt_creator.max_iter == 3


class TestImageGenerator:
    """Tests for agents/image_generator.py."""

    def test_is_agent_instance(self):
        from agents.image_generator import image_generator
        assert isinstance(image_generator, Agent)

    def test_has_generate_image_tool(self):
        from agents.image_generator import image_generator
        tool_names = [t.name for t in image_generator.tools]
        assert "generate_image" in tool_names

    def test_delegation_disabled(self):
        from agents.image_generator import image_generator
        assert image_generator.allow_delegation is False


class TestCaptionCreator:
    """Tests for agents/caption_creator.py."""

    def test_is_agent_instance(self):
        from agents.caption_creator import caption_creator
        assert isinstance(caption_creator, Agent)

    def test_has_no_tools(self):
        from agents.caption_creator import caption_creator
        assert len(caption_creator.tools) == 0

    def test_delegation_disabled(self):
        from agents.caption_creator import caption_creator
        assert caption_creator.allow_delegation is False


class TestInstagramPoster:
    """Tests for agents/instagram_poster.py."""

    def test_is_agent_instance(self):
        from agents.instagram_poster import instagram_poster
        assert isinstance(instagram_poster, Agent)

    def test_has_post_tool(self):
        from agents.instagram_poster import instagram_poster
        tool_names = [t.name for t in instagram_poster.tools]
        assert "post_to_instagram" in tool_names

    def test_delegation_disabled(self):
        from agents.instagram_poster import instagram_poster
        assert instagram_poster.allow_delegation is False


class TestAllAgentsConventions:
    """Cross-cutting checks that enforce project conventions on ALL agents."""

    @pytest.fixture
    def all_agents(self):
        from agents.researcher import researcher
        from agents.prompt_creator import prompt_creator
        from agents.image_generator import image_generator
        from agents.caption_creator import caption_creator
        from agents.instagram_poster import instagram_poster
        return [researcher, prompt_creator, image_generator, caption_creator, instagram_poster]

    def test_all_agents_are_agent_instances(self, all_agents):
        for agent in all_agents:
            assert isinstance(agent, Agent), f"{agent} is not an Agent"

    def test_all_agents_have_max_iter_3(self, all_agents):
        for agent in all_agents:
            assert agent.max_iter == 3, f"{agent.role} max_iter != 3"

    def test_all_agents_have_delegation_off(self, all_agents):
        for agent in all_agents:
            assert agent.allow_delegation is False, f"{agent.role} has delegation on"

    def test_all_agents_have_role(self, all_agents):
        for agent in all_agents:
            assert agent.role and len(agent.role) > 3

    def test_all_agents_have_goal(self, all_agents):
        for agent in all_agents:
            assert agent.goal and len(agent.goal) > 10

    def test_all_agents_have_backstory(self, all_agents):
        for agent in all_agents:
            assert agent.backstory and len(agent.backstory) > 10
