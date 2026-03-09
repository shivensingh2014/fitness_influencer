"""
Tests for all CrewAI task factories – validates task creation,
description placeholders, and expected outputs.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from crewai import Task, Agent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mock_agent():
    """A lightweight real CrewAI Agent for task creation (no API calls)."""
    return Agent(
        role="Test Agent",
        goal="Test goal for unit tests",
        backstory="A dummy agent used only in task unit tests.",
        llm="gemini/gemini-2.5-flash-lite",
        allow_delegation=False,
        max_iter=1,
        verbose=False,
    )


class TestResearchTask:
    """Tests for tasks/research_task.py."""

    def test_returns_task_instance(self, mock_agent):
        from tasks.research_task import create_research_task
        task = create_research_task(mock_agent)
        assert isinstance(task, Task)

    def test_description_has_placeholders(self, mock_agent):
        from tasks.research_task import create_research_task
        task = create_research_task(mock_agent)
        assert "{post_type_brief}" in task.description
        assert "{creative_direction}" in task.description

    def test_has_expected_output(self, mock_agent):
        from tasks.research_task import create_research_task
        task = create_research_task(mock_agent)
        assert task.expected_output and len(task.expected_output) > 10


class TestPromptTask:
    """Tests for tasks/prompt_task.py."""

    def test_returns_task_instance(self, mock_agent):
        from tasks.prompt_task import create_prompt_task
        task = create_prompt_task(mock_agent, context=[])
        assert isinstance(task, Task)

    def test_description_has_placeholders(self, mock_agent):
        from tasks.prompt_task import create_prompt_task
        task = create_prompt_task(mock_agent, context=[])
        assert "{post_type_brief}" in task.description
        assert "{creative_direction}" in task.description

    def test_context_is_set(self, mock_agent):
        from tasks.prompt_task import create_prompt_task
        from tasks.research_task import create_research_task
        # Use a real Task as context (CrewAI validates types via pydantic)
        research = create_research_task(mock_agent)
        task = create_prompt_task(mock_agent, context=[research])
        assert research in task.context


class TestGenerateImageTask:
    """Tests for tasks/generate_image_task.py."""

    def test_returns_task_instance(self, mock_agent):
        from tasks.generate_image_task import create_generate_image_task
        task = create_generate_image_task(mock_agent, context=[])
        assert isinstance(task, Task)

    def test_description_mentions_generate_image(self, mock_agent):
        from tasks.generate_image_task import create_generate_image_task
        task = create_generate_image_task(mock_agent, context=[])
        assert "generate_image" in task.description.lower()

    def test_expected_output_mentions_path(self, mock_agent):
        from tasks.generate_image_task import create_generate_image_task
        task = create_generate_image_task(mock_agent, context=[])
        assert "path" in task.expected_output.lower()


class TestCaptionHashtagTask:
    """Tests for tasks/caption_hashtag_task.py."""

    def test_returns_task_instance(self, mock_agent):
        from tasks.caption_hashtag_task import create_caption_hashtag_task
        task = create_caption_hashtag_task(mock_agent, context=[])
        assert isinstance(task, Task)

    def test_description_has_placeholders(self, mock_agent):
        from tasks.caption_hashtag_task import create_caption_hashtag_task
        task = create_caption_hashtag_task(mock_agent, context=[])
        assert "{post_type_brief}" in task.description
        assert "{creative_direction}" in task.description

    def test_expected_output_has_format(self, mock_agent):
        from tasks.caption_hashtag_task import create_caption_hashtag_task
        task = create_caption_hashtag_task(mock_agent, context=[])
        assert "CAPTION" in task.expected_output
        assert "HASHTAGS" in task.expected_output


class TestPostToInstagramTask:
    """Tests for tasks/post_to_instagram_task.py."""

    def test_returns_task_instance(self, mock_agent):
        from tasks.post_to_instagram_task import create_post_to_instagram_task
        task = create_post_to_instagram_task(mock_agent, context=[])
        assert isinstance(task, Task)

    def test_pre_approved_mode(self, mock_agent):
        """When called with explicit image_path + caption, those appear in description."""
        from tasks.post_to_instagram_task import create_post_to_instagram_task
        task = create_post_to_instagram_task(
            mock_agent,
            context=[],
            image_path="/fake/image.png",
            caption="Test caption #test",
        )
        assert "/fake/image.png" in task.description
        assert "Test caption #test" in task.description

    def test_context_mode(self, mock_agent):
        """When called without explicit params, description asks to extract from context."""
        from tasks.post_to_instagram_task import create_post_to_instagram_task
        task = create_post_to_instagram_task(mock_agent, context=[])
        assert "extract" in task.description.lower() or "context" in task.description.lower()
