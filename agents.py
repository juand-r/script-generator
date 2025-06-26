from typing import Dict, Any, List, Optional
from models import Character, Episode, Plan, Turn
from prompt_utils import call_openai, format_character_prompt, format_author_prompt


class CharacterAgent:
    """Agent that represents a character in the simulation"""
    
    def __init__(self, character: Character):
        self.character = character
    
    def act(self, world_context: str, previous_dialogue: str) -> Dict[str, Any]:
        """
        Generate character response and potential self-updates
        
        Args:
            world_context: Description of current world state from character's POV
            previous_dialogue: Recent dialogue history
        
        Returns:
            Dictionary with dialogue, actions, and self_updates
        """
        
        system_prompt = format_character_prompt(self.character, world_context, previous_dialogue)
        user_prompt = f"What do you do or say next? Remember to respond in valid JSON format."
        
        response = call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            expect_json=True
        )
        
        if response.get("json_data"):
            return response["json_data"]
        else:
            # Fallback if JSON parsing failed
            return {
                "dialogue": "",
                "actions": [],
                "self_updates": {}
            }
    
    def apply_self_updates(self, updates: Dict[str, Any]) -> None:
        """
        Apply self-updates to character state
        
        Args:
            updates: Dictionary containing state updates
        """
        
        state = self.character.state
        
        # Update emotion if provided
        if "emotion" in updates:
            state.emotion = updates["emotion"]
        
        # Update location if provided
        if "location" in updates:
            state.location = updates["location"]
        
        # Handle belief updates
        if "short_term_beliefs_add" in updates:
            for belief in updates["short_term_beliefs_add"]:
                if belief not in state.short_term_beliefs:
                    state.short_term_beliefs.append(belief)
        
        if "short_term_beliefs_remove" in updates:
            for belief in updates["short_term_beliefs_remove"]:
                if belief in state.short_term_beliefs:
                    state.short_term_beliefs.remove(belief)
        
        # Handle goal updates
        if "short_term_goals_add" in updates:
            for goal in updates["short_term_goals_add"]:
                if goal not in state.short_term_goals:
                    state.short_term_goals.append(goal)
        
        if "short_term_goals_remove" in updates:
            for goal in updates["short_term_goals_remove"]:
                if goal in state.short_term_goals:
                    state.short_term_goals.remove(goal)
        
        # Handle plan updates
        if "plans_add" in updates:
            for plan_data in updates["plans_add"]:
                plan = Plan(plan_id=plan_data["plan_id"], status=plan_data["status"])
                # Check if plan already exists
                existing_plan_ids = [p.plan_id for p in state.plans]
                if plan.plan_id not in existing_plan_ids:
                    state.plans.append(plan)
        
        if "plans_remove" in updates:
            for plan_id in updates["plans_remove"]:
                state.plans = [p for p in state.plans if p.plan_id != plan_id]


class AuthorAgent:
    """Agent that manages world state and orchestrates the simulation (Game Master)"""
    
    def __init__(self):
        pass
    
    def process_turn(self, episode: Episode, character_response: Dict[str, Any], 
                    character_id: str, turn_id: int) -> Dict[str, Any]:
        """
        Process a character's turn and update world state
        
        Args:
            episode: Current episode state
            character_response: Character's response (dialogue, actions, self_updates)
            character_id: ID of the character who acted
            turn_id: Current turn number
        
        Returns:
            Author's response with world updates and new claims
        """
        
        system_prompt = format_author_prompt(episode, turn_id)
        
        # Format the user prompt with character's actions
        user_prompt = f"""Character {character_id} just acted:
Dialogue: {character_response.get('dialogue', '')}
Actions: {character_response.get('actions', [])}

Please update the world state and identify any new claims that emerged.
Respond in valid JSON format."""
        
        response = call_openai(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            expect_json=True
        )
        
        if response.get("json_data"):
            return response["json_data"]
        else:
            # Fallback if JSON parsing failed
            return {
                "stage_directions": "",
                "world_updates": {},
                "new_claims": []
            }
    
    def apply_world_updates(self, episode: Episode, updates: Dict[str, Any]) -> None:
        """
        Apply world state updates to the episode
        
        Args:
            episode: Episode to update
            updates: Dictionary containing world updates
        """
        
        world_state = episode.world_state
        
        # Add new facts
        if "facts_add" in updates:
            for fact in updates["facts_add"]:
                if fact not in world_state.facts:
                    world_state.facts.append(fact)
        
        # Remove facts
        if "facts_remove" in updates:
            for fact in updates["facts_remove"]:
                if fact in world_state.facts:
                    world_state.facts.remove(fact)
        
        # Add history events
        if "history_add" in updates:
            for event in updates["history_add"]:
                world_state.history.append(event)
    
    def add_claims_to_episode(self, episode: Episode, new_claims: List[Dict[str, Any]], 
                             turn_id: int) -> List[str]:
        """
        Add new claims to the episode claim ledger
        
        Args:
            episode: Episode to add claims to
            new_claims: List of claim dictionaries
            turn_id: Turn when claims were introduced
        
        Returns:
            List of claim IDs that were added
        """
        
        claim_ids = []
        
        for claim_data in new_claims:
            claim_id = episode.add_claim(
                text=claim_data["text"],
                claim_type=claim_data["type"],
                truth_value=claim_data["truth_value"],
                visible_to=claim_data["visible_to"],
                turn_id=turn_id
            )
            claim_ids.append(claim_id)
        
        return claim_ids
    
    def get_character_perception(self, episode: Episode, character_id: str) -> str:
        """
        Generate what a character can perceive in the current world state
        
        Args:
            episode: Current episode
            character_id: Character whose perception to generate
        
        Returns:
            String description of what the character perceives
        """
        
        character = episode.get_character(character_id)
        if not character:
            return ""
        
        world_state = episode.world_state
        
        # For now, simple implementation - character sees general scene and location-based facts
        perception = f"Scene: {world_state.scene}\n"
        perception += f"You are at: {character.state.location}\n"
        
        # Add visible facts (in a real implementation, this would be more sophisticated)
        if world_state.facts:
            perception += f"Apparent facts: {'; '.join(world_state.facts[:3])}\n"
        
        return perception 