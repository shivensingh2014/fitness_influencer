"""
Integration tests for crew.py – validates that crews can be assembled
correctly with proper agents, tasks, and wiring.
These tests do NOT call any LLM or external API.
"""
import sys
from pathlib import Path

import pytest
from crewai import Crew, Process

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestBuildGenerationCrew:
    """Tests for build_generation_crew()."""

    def test_returns_crew_instance(self):
        from crew import build_generation_crew
        crew = build_generation_crew()
        assert isinstance(crew, Crew)

    def test_has_5_agents(self):
        from crew import build_generation_crew
        crew = build_generation_crew()
        assert len(crew.agents) == 5

    def test_has_6_tasks(self):
        from crew import build_generation_crew
        crew = build_generation_crew()
        assert len(crew.tasks) == 6

    def test_sequential_process(self):
        from crew import build_generation_crew
        crew = build_generation_crew()
        assert crew.process == Process.sequential

    def test_task_order_is_correct(self):
        """Tasks should be: strategy → research → prompt → image → caption → validation."""
        from crew import build_generation_crew
        crew = build_generation_crew()
        task_descriptions = [t.description for t in crew.tasks]
        assert "strategy brief" in task_descriptions[0].lower() or "persona" in task_descriptions[0].lower()
        assert "trending" in task_descriptions[1].lower() or "research" in task_descriptions[1].lower()
        assert "prompt" in task_descriptions[2].lower()
        assert "generate_image" in task_descriptions[3].lower() or "image" in task_descriptions[3].lower()
        assert "caption" in task_descriptions[4].lower()
        assert "validate" in task_descriptions[5].lower() or "validation" in task_descriptions[5].lower()

    def test_agent_roles_are_distinct(self):
        from crew import build_generation_crew
        crew = build_generation_crew()
        roles = [a.role for a in crew.agents]
        assert len(roles) == len(set(roles)), "Agents must have unique roles"


class TestBuildPostingCrew:
    """Tests for build_posting_crew()."""

    def test_returns_crew_instance(self):
        from crew import build_posting_crew
        crew = build_posting_crew("/fake/img.png", "Test caption")
        assert isinstance(crew, Crew)

    def test_has_1_agent(self):
        from crew import build_posting_crew
        crew = build_posting_crew("/fake/img.png", "Test caption")
        assert len(crew.agents) == 1

    def test_has_1_task(self):
        from crew import build_posting_crew
        crew = build_posting_crew("/fake/img.png", "Test caption")
        assert len(crew.tasks) == 1

    def test_task_description_contains_image_path(self):
        from crew import build_posting_crew
        crew = build_posting_crew("/path/to/image.png", "My caption")
        assert "/path/to/image.png" in crew.tasks[0].description

    def test_task_description_contains_caption(self):
        from crew import build_posting_crew
        crew = build_posting_crew("/path/to/image.png", "My unique caption #tag")
        assert "My unique caption #tag" in crew.tasks[0].description


class TestBuildLegacyCrew:
    """Tests for build_crew() – the legacy full 5-step crew."""

    def test_returns_crew_instance(self):
        from crew import build_crew
        crew = build_crew()
        assert isinstance(crew, Crew)

    def test_has_5_agents(self):
        from crew import build_crew
        crew = build_crew()
        assert len(crew.agents) == 5

    def test_has_5_tasks(self):
        from crew import build_crew
        crew = build_crew()
        assert len(crew.tasks) == 5

    def test_sequential_process(self):
        from crew import build_crew
        crew = build_crew()
        assert crew.process == Process.sequential
