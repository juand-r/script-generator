#!/usr/bin/env python3
"""
Main simulation engine for the agentic dialogue framework
Orchestrates multi-agent conversations with state tracking and logging
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from copy import deepcopy

from models import Episode, Character, Turn
from agents import CharacterAgent, AuthorAgent
from prompt_utils import call_openai


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulationLogger:
    """Tracks state changes and simulation progress"""
    
    def __init__(self, episode_id: str):
        self.episode_id = episode_id
        self.state_history = []
        self.turn_logs = []
        self.start_time = datetime.now()
    
    def log_character_state_change(self, character_id: str, turn_id: int, 
                                  old_state: Dict, new_state: Dict, updates: Dict):
        """Log character state changes"""
        state_change = {
            "timestamp": datetime.now().isoformat(),
            "turn_id": turn_id,
            "character_id": character_id,
            "old_state": old_state,
            "new_state": new_state,
            "updates_applied": updates
        }
        self.state_history.append(state_change)
        
        logger.info(f"Turn {turn_id} - {character_id} state change: {updates}")
    
    def log_turn_completion(self, turn_id: int, speaker: str, dialogue: str, 
                           actions: List[str], world_updates: Dict, new_claims: List):
        """Log completed turn with all details"""
        turn_log = {
            "timestamp": datetime.now().isoformat(),
            "turn_id": turn_id,
            "speaker": speaker,
            "dialogue": dialogue,
            "actions": actions,
            "world_updates": world_updates,
            "new_claims": len(new_claims),
            "claims_detail": new_claims
        }
        self.turn_logs.append(turn_log)
        
        logger.info(f"Turn {turn_id} completed - {speaker}: {dialogue[:50]}...")
    
    def log_simulation_summary(self, episode: Episode):
        """Log final simulation summary"""
        duration = datetime.now() - self.start_time
        
        summary = {
            "episode_id": episode.episode_id,
            "duration_seconds": duration.total_seconds(),
            "total_turns": len(episode.turns),
            "total_claims": len(episode.claim_ledger),
            "characters": len(episode.characters),
            "final_world_facts": len(episode.world_state.facts),
            "state_changes": len(self.state_history)
        }
        
        logger.info(f"Simulation completed: {summary}")
        return summary


class TranscriptFormatter:
    """Formats episode data into readable transcripts"""
    
    @staticmethod
    def format_dialogue_transcript(episode: Episode) -> str:
        """Create a clean dialogue-only transcript"""
        lines = []
        lines.append(f"=== {episode.title} ===")
        lines.append(f"Genre: {episode.genre}")
        lines.append(f"Scene: {episode.world_state.scene}")
        lines.append("")
        
        for turn in episode.turns:
            if turn.dialogue.strip():
                speaker_name = turn.speaker.upper()
                lines.append(f"{speaker_name}: {turn.dialogue}")
                
                if turn.actions:
                    action_text = ", ".join(turn.actions)
                    lines.append(f"    ({speaker_name} {action_text})")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_detailed_transcript(episode: Episode, sim_logger: SimulationLogger) -> str:
        """Create detailed transcript with state changes and metadata"""
        lines = []
        lines.append(f"=== DETAILED TRANSCRIPT: {episode.title} ===")
        lines.append(f"Episode ID: {episode.episode_id}")
        lines.append(f"Created: {episode.creation_time}")
        lines.append(f"Genre: {episode.genre}")
        lines.append("")
        
        # Characters
        lines.append("CHARACTERS:")
        for char in episode.characters:
            lines.append(f"  • {char.char_id}: {char.profile.occupation}, {char.profile.age}yo")
            lines.append(f"    Traits: {', '.join(char.profile.core_traits)}")
            lines.append(f"    Initial emotion: {char.state.emotion}")
        lines.append("")
        
        # Initial world state
        lines.append("INITIAL WORLD STATE:")
        lines.append(f"  Scene: {episode.world_state.scene}")
        for fact in episode.world_state.facts:
            lines.append(f"  • {fact}")
        lines.append("")
        
        # Turn-by-turn with state changes
        lines.append("DIALOGUE & STATE CHANGES:")
        for turn in episode.turns:
            lines.append(f"\n--- TURN {turn.turn_id} ---")
            
            if turn.dialogue:
                lines.append(f"{turn.speaker.upper()}: {turn.dialogue}")
            
            if turn.actions:
                action_text = ", ".join(turn.actions)
                lines.append(f"  Actions: {action_text}")
            
            # Find state changes for this turn
            turn_state_changes = [
                log for log in sim_logger.state_history 
                if log["turn_id"] == turn.turn_id
            ]
            
            if turn_state_changes:
                lines.append("  State Changes:")
                for change in turn_state_changes:
                    updates = change["updates_applied"]
                    if updates:
                        lines.append(f"    {change['character_id']}: {updates}")
        
        # Final state summary
        lines.append("\n=== FINAL STATE ===")
        for char in episode.characters:
            lines.append(f"{char.char_id}:")
            lines.append(f"  Emotion: {char.state.emotion}")
            lines.append(f"  Location: {char.state.location}")
            if char.state.short_term_beliefs:
                lines.append(f"  Beliefs: {'; '.join(char.state.short_term_beliefs)}")
            if char.state.short_term_goals:
                lines.append(f"  Goals: {'; '.join(char.state.short_term_goals)}")
        
        lines.append(f"\nTotal Claims Generated: {len(episode.claim_ledger)}")
        
        return "\n".join(lines)


class EpisodeSimulator:
    """Main simulator that orchestrates the multi-agent conversation"""
    
    def __init__(self, max_turns: int = 10, enable_logging: bool = True):
        self.max_turns = max_turns
        self.enable_logging = enable_logging
        self.author = AuthorAgent()
        
    def simulate_episode(self, episode: Episode, 
                        character_order: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a complete episode simulation
        
        Args:
            episode: Episode with initial characters and world state
            character_order: Optional list specifying speaker order, otherwise alternates
        
        Returns:
            Dictionary with episode, transcripts, logs, and metadata
        """
        
        sim_logger = SimulationLogger(episode.episode_id)
        logger.info(f"Starting simulation: {episode.title}")
        
        # Create character agents
        agents = {}
        for char in episode.characters:
            agents[char.char_id] = CharacterAgent(char)
        
        # Determine speaking order
        if character_order is None:
            character_order = [char.char_id for char in episode.characters]
        
        # Main simulation loop
        for turn_id in range(1, self.max_turns + 1):
            speaker_id = character_order[(turn_id - 1) % len(character_order)]
            
            logger.info(f"Turn {turn_id}: {speaker_id} to speak")
            
            # Get character's perception of current world
            world_context = self.author.get_character_perception(episode, speaker_id)
            
            # Get recent dialogue for context
            recent_dialogue = self._get_recent_dialogue(episode, last_n_turns=10)
            
            # Character acts
            speaker_agent = agents[speaker_id]
            
            # Store old state for logging
            old_state = self._capture_character_state(speaker_agent.character)
            
            try:
                character_response = speaker_agent.act(world_context, recent_dialogue)
                
                # Apply self-updates
                self_updates = character_response.get("self_updates", {})
                if self_updates:
                    speaker_agent.apply_self_updates(self_updates)
                
                # Log state changes
                new_state = self._capture_character_state(speaker_agent.character)
                if self.enable_logging:
                    sim_logger.log_character_state_change(
                        speaker_id, turn_id, old_state, new_state, self_updates
                    )
                
                # Author processes the turn
                author_response = self.author.process_turn(
                    episode, character_response, speaker_id, turn_id
                )
                
                # Apply world updates
                world_updates = author_response.get("world_updates", {})
                self.author.apply_world_updates(episode, world_updates)
                
                # Add new claims
                new_claims = author_response.get("new_claims", [])
                claim_ids = self.author.add_claims_to_episode(episode, new_claims, turn_id)
                
                # Create and add turn record
                turn = Turn(
                    turn_id=turn_id,
                    speaker=speaker_id,
                    dialogue=character_response.get("dialogue", ""),
                    actions=character_response.get("actions", []),
                    self_updates=self_updates,
                    claims_referenced=claim_ids
                )
                episode.turns.append(turn)
                
                # Log turn completion
                if self.enable_logging:
                    sim_logger.log_turn_completion(
                        turn_id, speaker_id, turn.dialogue, turn.actions,
                        world_updates, new_claims
                    )
                
                # Check for natural stopping conditions
                if self._should_end_episode(character_response, author_response):
                    logger.info(f"Episode ended naturally at turn {turn_id}")
                    break
                    
            except Exception as e:
                logger.error(f"Error in turn {turn_id}: {e}")
                # Continue simulation despite errors
                continue
        
        # Generate transcripts and summary
        dialogue_transcript = TranscriptFormatter.format_dialogue_transcript(episode)
        detailed_transcript = TranscriptFormatter.format_detailed_transcript(episode, sim_logger)
        
        if self.enable_logging:
            simulation_summary = sim_logger.log_simulation_summary(episode)
        else:
            simulation_summary = {"episode_id": episode.episode_id}
        
        return {
            "episode": episode,
            "dialogue_transcript": dialogue_transcript,
            "detailed_transcript": detailed_transcript,
            "simulation_logs": sim_logger,
            "summary": simulation_summary,
            "success": True
        }
    
    def _capture_character_state(self, character: Character) -> Dict[str, Any]:
        """Capture character state for logging"""
        return {
            "emotion": character.state.emotion,
            "location": character.state.location,
            "short_term_beliefs": character.state.short_term_beliefs.copy(),
            "short_term_goals": character.state.short_term_goals.copy(),
            "plans": [{"plan_id": p.plan_id, "status": p.status} for p in character.state.plans]
        }
    
    def _get_recent_dialogue(self, episode: Episode, last_n_turns: int = 3) -> str:
        """Get recent dialogue for context"""
        recent_turns = episode.turns[-last_n_turns:] if episode.turns else []
        dialogue_lines = []
        
        for turn in recent_turns:
            if turn.dialogue.strip():
                dialogue_lines.append(f"{turn.speaker}: {turn.dialogue}")
        
        return "\n".join(dialogue_lines) if dialogue_lines else "No previous dialogue."
    
    def _should_end_episode(self, character_response: Dict[str, Any], 
                          author_response: Dict[str, Any]) -> bool:
        """Determine if episode should end naturally"""
        # Simple heuristics for now - can be made more sophisticated
        dialogue = character_response.get("dialogue", "").lower()
        
        # End if someone says goodbye or indicates conversation is over
        end_phrases = ["goodbye", "see you later", "that's all", "conversation over", 
                      "end scene", "fade out"]
        
        return any(phrase in dialogue for phrase in end_phrases)


# Convenience function for quick episode generation
def quick_simulate(episode: Episode, max_turns: int = 8) -> str:
    """
    Quick simulation that returns just the dialogue transcript
    
    Args:
        episode: Episode to simulate
        max_turns: Maximum number of turns
        
    Returns:
        Clean dialogue transcript string
    """
    simulator = EpisodeSimulator(max_turns=max_turns, enable_logging=False)
    result = simulator.simulate_episode(episode)
    return result["dialogue_transcript"] 