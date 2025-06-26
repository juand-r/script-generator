#!/usr/bin/env python3
"""
Example usage of the agentic dialogue framework
This demonstrates creating characters and running a simple simulation
"""

import os
from datetime import datetime
from models import CharacterProfile, CharacterState, Character, WorldState, Episode
from agents import CharacterAgent, AuthorAgent


def create_sample_episode():
    """Create a sample episode with two characters"""
    
    # Create Alice - a paranoid security expert
    alice_profile = CharacterProfile(
        age=34,
        gender="female",
        ethnicity="German-American", 
        occupation="cybersecurity_analyst",
        core_traits=["paranoid", "methodical", "brilliant"],
        intrinsic_prefs=["privacy", "encrypted_communications", "black_coffee"],
        lt_memory=[
            "discovered major corporate hack 2 years ago",
            "doesn't trust cloud storage",
            "parents were East German refugees"
        ]
    )
    
    alice_state = CharacterState(
        emotion="suspicious",
        location="secure_office",
        short_term_beliefs=[
            "someone is monitoring the network",
            "Bob seems nervous today",
            "the new firewall logs look suspicious"
        ],
        short_term_goals=[
            "investigate network anomalies",
            "confront Bob about his behavior"
        ],
        plans=[]
    )
    
    alice = Character("alice", alice_profile, alice_state)
    
    # Create Bob - a corporate spy
    bob_profile = CharacterProfile(
        age=41,
        gender="male",
        ethnicity="British",
        occupation="it_manager",
        core_traits=["charming", "deceptive", "ambitious"],
        intrinsic_prefs=["expensive_whiskey", "classical_music", "manipulation"],
        lt_memory=[
            "recruited by competitor company 6 months ago",
            "has gambling debts",
            "Alice is getting too close to the truth"
        ]
    )
    
    bob_state = CharacterState(
        emotion="nervous",
        location="secure_office", 
        short_term_beliefs=[
            "Alice suspects something",
            "need to finish data extraction today",
            "my cover story is holding"
        ],
        short_term_goals=[
            "deflect Alice's suspicions",
            "complete the data theft",
            "plan exit strategy"
        ],
        plans=[]
    )
    
    bob = Character("bob", bob_profile, bob_state)
    
    # Create world state
    world_state = WorldState(
        scene="INT. SECURE CORPORATE OFFICE - LATE EVENING",
        facts=[
            "building is mostly empty",
            "security cameras are recording", 
            "network activity is elevated",
            "Bob has been working late frequently"
        ],
        history=[
            "Alice noticed unusual network patterns",
            "Bob volunteered to stay late again",
            "office cleaning crew left an hour ago"
        ]
    )
    
    # Create episode
    episode = Episode(
        episode_id="corp_espionage_001",
        title="The Network Anomaly",
        genre="corporate_thriller",
        creation_time=datetime.now().isoformat(),
        characters=[alice, bob],
        world_state=world_state
    )
    
    # Add initial claims
    episode.add_claim("Bob is stealing corporate data", "fact", True, ["narrator"], 0)
    episode.add_claim("Alice suspects Bob", "belief", True, ["alice"], 0)
    episode.add_claim("Network logs show unauthorized access", "evidence", True, ["alice"], 0)
    episode.add_claim("Bob is being paid by a competitor", "fact", True, ["narrator"], 0)
    
    return episode


def simulate_without_llm(episode):
    """
    Simulate a few turns without actually calling LLM APIs
    This is useful for testing the framework structure
    """
    
    print("🎬 Starting simulation (mock mode - no LLM calls)\n")
    
    # Create agents
    alice_agent = CharacterAgent(episode.get_character("alice"))
    bob_agent = CharacterAgent(episode.get_character("bob"))
    author = AuthorAgent()
    
    # Mock character responses (what an LLM might return)
    mock_responses = [
        {
            "speaker": "alice",
            "response": {
                "dialogue": "Bob, you've been working late a lot lately. Everything alright?",
                "actions": ["approach_bob_desk", "cross_arms"],
                "self_updates": {
                    "emotion": "interrogative",
                    "short_term_goals_add": ["read Bob's body language"]
                }
            }
        },
        {
            "speaker": "bob", 
            "response": {
                "dialogue": "Oh, just trying to catch up on some system maintenance. You know how it is.",
                "actions": ["minimize_screen", "turn_to_face_alice"],
                "self_updates": {
                    "emotion": "defensive",
                    "short_term_beliefs_add": ["Alice is definitely suspicious"],
                    "plans_add": [{"plan_id": "deflect_suspicion", "status": "active"}]
                }
            }
        },
        {
            "speaker": "alice",
            "response": {
                "dialogue": "System maintenance that requires accessing the financial database at 9 PM?",
                "actions": ["point_at_screen"],
                "self_updates": {
                    "emotion": "accusatory",
                    "short_term_beliefs_add": ["Bob is lying"],
                    "short_term_goals_add": ["confront Bob directly"]
                }
            }
        }
    ]
    
    for i, turn_data in enumerate(mock_responses):
        turn_id = i + 1
        speaker = turn_data["speaker"]
        response = turn_data["response"]
        
        print(f"Turn {turn_id} - {speaker.upper()}:")
        print(f"  Dialogue: {response['dialogue']}")
        print(f"  Actions: {response['actions']}")
        print(f"  Self-updates: {response['self_updates']}")
        
        # Apply character self-updates
        if speaker == "alice":
            alice_agent.apply_self_updates(response["self_updates"])
        elif speaker == "bob":
            bob_agent.apply_self_updates(response["self_updates"])
        
        # Mock author response
        mock_author_response = {
            "stage_directions": f"(The tension in the room increases as {speaker} acts)",
            "world_updates": {
                "history_add": [f"{speaker} {response['actions'][0]} at turn {turn_id}"]
            },
            "new_claims": [
                {
                    "text": f"{speaker} said: {response['dialogue']}",
                    "type": "dialogue",
                    "truth_value": True,
                    "visible_to": ["alice", "bob"]
                }
            ]
        }
        
        # Apply author updates
        author.apply_world_updates(episode, mock_author_response["world_updates"])
        author.add_claims_to_episode(episode, mock_author_response["new_claims"], turn_id)
        
        # Add turn to episode
        from models import Turn
        episode.turns.append(Turn(
            turn_id=turn_id,
            speaker=speaker,
            dialogue=response["dialogue"],
            actions=response["actions"],
            self_updates=response["self_updates"]
        ))
        
        print(f"  Stage directions: {mock_author_response['stage_directions']}")
        print()
    
    print("📊 Final episode state:")
    print(f"  Total turns: {len(episode.turns)}")
    print(f"  Total claims: {len(episode.claim_ledger)}")
    print(f"  Alice emotion: {episode.get_character('alice').state.emotion}")
    print(f"  Bob emotion: {episode.get_character('bob').state.emotion}")
    print(f"  World history events: {len(episode.world_state.history)}")


def main():
    """Main example function"""
    print("🤖 Agentic Dialogue Framework Example\n")
    
    # Create sample episode
    episode = create_sample_episode()
    print(f"Created episode: {episode.title}")
    print(f"Characters: {[char.char_id for char in episode.characters]}")
    print(f"Initial claims: {len(episode.claim_ledger)}")
    print()
    
    # Run simulation without LLM calls
    simulate_without_llm(episode)
    
    # Show JSON serialization
    print("\n💾 JSON serialization example:")
    json_str = episode.to_json()
    print(f"Episode serialized to {len(json_str)} characters")
    
    # Test deserialization
    episode_restored = episode.from_json(json_str)
    print(f"Successfully restored episode: {episode_restored.title}")
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main() 