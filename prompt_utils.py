import os
import json
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 1.0,
    max_tokens: int = 1000,
    expect_json: bool = True
) -> Dict[str, Any]:
    """
    Call OpenAI API with structured output support
    
    Args:
        system_prompt: System message to set context
        user_prompt: User message with the actual request
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        expect_json: Whether to expect JSON response format
    
    Returns:
        Dictionary with 'content' and optional 'json_data' keys
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if expect_json else {"type": "text"}
        )
        
        content = response.choices[0].message.content
        
        result = {
            "content": content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        # Try to parse JSON if expected
        if expect_json and content:
            try:
                result["json_data"] = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Warning: Expected JSON but couldn't parse: {e}")
                result["json_data"] = None
        
        return result
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "content": None,
            "error": str(e),
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }


def format_character_prompt(character, world_context: str, previous_dialogue: str) -> str:
    """
    Format the system prompt for a character agent
    
    Args:
        character: Character object with profile and state
        world_context: Current world state description
        previous_dialogue: Recent dialogue history
    
    Returns:
        Formatted system prompt string
    """
    
    profile = character.profile
    state = character.state
    
    prompt = f"""You are {character.char_id}.

STABLE ATTRIBUTES:
Age: {profile.age}
Gender: {profile.gender}
Ethnicity: {profile.ethnicity}
Occupation: {profile.occupation}
Core traits: {', '.join(profile.core_traits)}
Intrinsic preferences: {', '.join(profile.intrinsic_prefs)}
Long-term memories: {'; '.join(profile.lt_memory)}

CURRENT MUTABLE STATE:
Emotion: {state.emotion}
Location: {state.location}
Short-term beliefs: {'; '.join(state.short_term_beliefs)}
Short-term goals: {'; '.join(state.short_term_goals)}
Active plans: {'; '.join([f"{p.plan_id} ({p.status})" for p in state.plans])}

CURRENT SITUATION:
{world_context}

RECENT DIALOGUE:
{previous_dialogue}

RULES:
1. Respond with either or both:
   a. dialogue: what you say aloud
   b. actions: what you physically do
2. Optionally output self_updates to revise your own state (beliefs, goals, emotion, location, plans).
3. Stay true to your character traits and current emotional state.

Return valid JSON in this format:
{{
  "dialogue": "...optional line here...",
  "actions": ["optional", "list"],
  "self_updates": {{
    "emotion": "new_emotion_if_changed",
    "short_term_beliefs_add": ["new belief"],
    "short_term_beliefs_remove": ["belief to remove"],
    "short_term_goals_add": ["new goal"],
    "short_term_goals_remove": ["goal to remove"],
    "plans_add": [{{"plan_id": "new_plan", "status": "pending"}}],
    "plans_remove": ["plan_id_to_remove"]
  }}
}}"""
    
    return prompt


def format_author_prompt(episode, current_turn: int) -> str:
    """
    Format the system prompt for the author/game master agent
    
    Args:
        episode: Current episode state
        current_turn: Current turn number
    
    Returns:
        Formatted system prompt string
    """
    
    world_state = episode.world_state
    characters_summary = []
    
    for char in episode.characters:
        char_summary = f"- {char.char_id}: {char.state.emotion} at {char.state.location}"
        characters_summary.append(char_summary)
    
    recent_turns = episode.turns[-3:] if episode.turns else []
    recent_dialogue = []
    for turn in recent_turns:
        if turn.dialogue:
            recent_dialogue.append(f"{turn.speaker}: {turn.dialogue}")
        if turn.actions:
            recent_dialogue.append(f"({turn.speaker} {', '.join(turn.actions)})")
    
    prompt = f"""You are the AUTHOR/GAME MASTER of this simulation.

CURRENT WORLD STATE:
Scene: {world_state.scene}
Facts: {'; '.join(world_state.facts)}
Recent history: {'; '.join(world_state.history[-5:])}

CHARACTER POSITIONS:
{chr(10).join(characters_summary)}

RECENT EVENTS:
{chr(10).join(recent_dialogue)}

Your job is to:
1. Update the world state based on character actions
2. Add stage directions or environmental descriptions
3. Track new claims/facts that emerge
4. Determine what each character can perceive

Return valid JSON in this format:
{{
  "stage_directions": "Optional parenthetical description",
  "world_updates": {{
    "facts_add": ["new fact"],
    "facts_remove": ["fact no longer true"],
    "history_add": ["event that just happened"]
  }},
  "new_claims": [
    {{
      "text": "claim description",
      "type": "event|belief|goal|perception",
      "truth_value": true,
      "visible_to": ["char_id1", "char_id2"]
    }}
  ]
}}"""
    
    return prompt 