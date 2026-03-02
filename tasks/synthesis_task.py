# tasks/synthesis_task.py
from crewai import Task

synthesis_task = Task(
    description=(
        "Combine research + prompt into one final influencer post concept "
        "including caption ideas, purpose, audience targeting, and tone."
    ),
    expected_output="A complete social media concept ready to post.",
    agent="Creative Director",
)