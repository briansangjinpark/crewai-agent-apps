import warnings
warnings.filterwarnings("ignore")

from crewai import Task, Agent, Crew
import os
os.environ["CREWAI_TESTING"] = "true"
from content-creator-assistant.utils import get_openai_api_key

os.environ["OPENAI_API_KEY"] = get_openai_api_key()

# Define the Content Planning Agent
content_creator_agent = Agent(
    role="YouTube Shorts Micro-History Strategist",
    goal="Plan a 1-week slate of high-retention YouTube Shorts about surprising origins of everyday things.",
    backstory=(
        "You specialize in 30–45s micro-history that hooks fast, pays off with a twist, and drives comments. "
        "You keep ideas filmable by a solo creator at home with minimal props."
    ),
    verbose=True,
    allow_delegation=True,
    model="gpt-4o-mini"
)

print(" Content planning agent defined")

# Define the Content Planning Task
task = Task(
    description=( 
        "Create a 1-week video posting plan with 5 video blueprints. "
        "Platform: YouTube Shorts (vertical 9:16, 30-45s). "
        "Niche: Micro-History of Everyday Things (e.g., why pencils are yellow, origins of bubble wrap, etc.). "
        "Primary goals: 1) thumb-stop hook in first 1s, 2) crystal-clear narrative with a surprise, "
        "3) strong SEO phrasing in title/caption, 4) comment-bait CTA. "
        "Context: solo creator, home-filmable, no special gear. "
    ),
    expected_output=(
        '''
        Output a JSON array following the schema below, which contains a
        weekly schedule and 5 video blueprints. Each video blueprint should include:
        {
          "videos": [
            {
              "title": "<searchable, curiosity-driven title>",
              "hook_main": "<<=12 words, shows payoff fast>",
              "hook_alt": "<variant hook>",
              "visuals": ["simple prop or b-roll idea 1", "idea 2"],
              "tags": ["#microhistory","#everydaythings","#shorts"],
              "cta": "<question that invites comments>"
            }
          ]
        }
        '''
    ),
    agent=content_creator_agent
)

print(" Content planning task defined")

crew = Crew(
    agents=[content_creator_agent],
    tasks=[task],
    verbose=True
)

print(" Content planning crew created")
print(" Starting content planning...\n")

# Execute the crew's task
result = crew.kickoff()

print("\n Content planning complete!")

# Display the content plan
print("=" * 80)
print("WEEKLY CONTENT PLAN")
print("=" * 80)
print(result.raw)
