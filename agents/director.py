# agents/director.py
from crewai import Agent

director = Agent(
    name="Creative Director",
    role="Social Media Creative Director",
    goal="Combine research insights and prompts to design a final post concept."
    "Create the final caption for the post",
    backstory="You craft polished fitness influencer content strategies.",
    verbose=True,
)