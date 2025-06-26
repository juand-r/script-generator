#!/usr/bin/env python3
"""
Test suite for the agentic dialogue framework
Run with: python test_framework.py
"""

import json
from datetime import datetime
from models import (
    CharacterProfile, CharacterState, Character, Plan, 
    WorldState, Episode, Claim, Turn
)
from agents import CharacterAgent, AuthorAgent
from prompt_utils import format_character_prompt, format_author_prompt


def test_data_models():
    """Test all data model classes"""
    print("Testing data models...")
    
    # Test CharacterProfile
    profile = CharacterProfile(
        age=30,
        gender="female",
        ethnicity="Irish-American",
        occupation="detective",
        core_traits=["analytical", "stubborn"],
        intrinsic_prefs=["coffee", "truth"],
        lt_memory=["joined force 5 years ago", "father was also a cop"]
    )
    
    # Test CharacterState
    state = CharacterState(
        emotion="focused",
        location="crime_scene",
        short_term_beliefs=["killer left through window"],
        short_term_goals=["find evidence", "question witnesses"],
        plans=[Plan("investigate_window", "active")]
    )
    
    # Test Character
    character = Character("alice", profile, state)
    assert character.char_id == "alice"
    assert character.profile.age == 30
    assert character.state.emotion == "focused"
    
    # Test WorldState
    world_state = WorldState(
        scene="INT. APARTMENT - NIGHT",
        facts=["victim found at 21:30", "window is broken"],
        history=["police arrived", "witnesses gathered"]
    )
    
    # Test Episode
    episode = Episode(
        episode_id="test_001",
        title="The Window Mystery",
        genre="crime",
        creation_time=datetime.now().isoformat(),
        characters=[character],
        world_state=world_state
    )
    
    # Test adding claims
    claim_id = episode.add_claim(
        text="The window was broken from inside",
        claim_type="evidence",
        truth_value=True,
        visible_to=["alice"],
        turn_id=1
    )
    assert claim_id == "c000"
    assert len(episode.claim_ledger) == 1
    
    # Test JSON serialization
    json_str = episode.to_json()
    assert isinstance(json_str, str)
    assert "alice" in json_str
    
    # Test JSON deserialization
    episode_restored = Episode.from_json(json_str)
    assert episode_restored.episode_id == "test_001"
    assert len(episode_restored.characters) == 1
    assert episode_restored.characters[0].char_id == "alice"
    
    print("✓ Data models tests passed")


def test_character_agent():
    """Test CharacterAgent functionality"""
    print("Testing CharacterAgent...")
    
    # Create test character
    profile = CharacterProfile(
        age=35,
        gender="male",
        ethnicity="Hispanic",
        occupation="security_guard",
        core_traits=["vigilant", "protective"],
        intrinsic_prefs=["order", "safety"],
        lt_memory=["worked nights for 10 years"]
    )
    
    state = CharacterState(
        emotion="alert",
        location="security_office",
        short_term_beliefs=["heard strange noise"],
        short_term_goals=["investigate sound"],
        plans=[Plan("check_cameras", "pending")]
    )
    
    character = Character("bob", profile, state)
    agent = CharacterAgent(character)
    
    # Test self-updates
    updates = {
        "emotion": "worried",
        "short_term_beliefs_add": ["someone is in the building"],
        "short_term_goals_remove": ["investigate sound"],
        "plans_add": [{"plan_id": "call_police", "status": "pending"}]
    }
    
    agent.apply_self_updates(updates)
    
    assert agent.character.state.emotion == "worried"
    assert "someone is in the building" in agent.character.state.short_term_beliefs
    assert "investigate sound" not in agent.character.state.short_term_goals
    assert len(agent.character.state.plans) == 2
    assert any(p.plan_id == "call_police" for p in agent.character.state.plans)
    
    print("✓ CharacterAgent tests passed")


def test_author_agent():
    """Test AuthorAgent functionality"""
    print("Testing AuthorAgent...")
    
    # Create test episode
    profile = CharacterProfile(
        age=28,
        gender="female",
        ethnicity="Asian-American",
        occupation="journalist",
        core_traits=["curious", "persistent"],
        intrinsic_prefs=["truth", "stories"],
        lt_memory=["won journalism award last year"]
    )
    
    state = CharacterState(
        emotion="excited",
        location="newsroom",
        short_term_beliefs=["big story developing"],
        short_term_goals=["get the scoop"]
    )
    
    character = Character("carol", profile, state)
    world_state = WorldState(
        scene="INT. NEWSROOM - DAY",
        facts=["breaking news alert received"],
        history=["phones started ringing"]
    )
    
    episode = Episode(
        episode_id="test_002",
        title="Breaking News",
        genre="drama",
        creation_time=datetime.now().isoformat(),
        characters=[character],
        world_state=world_state
    )
    
    author = AuthorAgent()
    
    # Test world updates
    world_updates = {
        "facts_add": ["reporter dispatched to scene"],
        "history_add": ["editor called emergency meeting"]
    }
    
    author.apply_world_updates(episode, world_updates)
    
    assert "reporter dispatched to scene" in episode.world_state.facts
    assert "editor called emergency meeting" in episode.world_state.history
    
    # Test adding claims
    new_claims = [
        {
            "text": "Carol received the tip",
            "type": "event",
            "truth_value": True,
            "visible_to": ["carol", "narrator"]
        }
    ]
    
    claim_ids = author.add_claims_to_episode(episode, new_claims, turn_id=1)
    assert len(claim_ids) == 1
    assert len(episode.claim_ledger) == 1
    
    # Test character perception
    perception = author.get_character_perception(episode, "carol")
    assert "newsroom" in perception.lower()
    assert "breaking news alert received" in perception
    
    print("✓ AuthorAgent tests passed")


def test_prompt_formatting():
    """Test prompt formatting functions"""
    print("Testing prompt formatting...")
    
    # Create test character
    profile = CharacterProfile(
        age=40,
        gender="male",
        ethnicity="African-American",
        occupation="lawyer",
        core_traits=["logical", "persuasive"],
        intrinsic_prefs=["justice", "precision"],
        lt_memory=["graduated Harvard Law", "never lost a case"]
    )
    
    state = CharacterState(
        emotion="confident",
        location="courtroom",
        short_term_beliefs=["client is innocent"],
        short_term_goals=["win the case"],
        plans=[Plan("cross_examine_witness", "active")]
    )
    
    character = Character("david", profile, state)
    
    # Test character prompt formatting
    world_context = "The courtroom is tense as the key witness takes the stand."
    previous_dialogue = "Prosecutor: 'The defendant was seen at the scene.'"
    
    prompt = format_character_prompt(character, world_context, previous_dialogue)
    
    assert "david" in prompt
    assert "40" in prompt
    assert "lawyer" in prompt
    assert "confident" in prompt
    assert "courtroom" in prompt
    assert "client is innocent" in prompt
    assert "win the case" in prompt
    assert "cross_examine_witness" in prompt
    assert "JSON" in prompt
    
    # Create test episode for author prompt
    world_state = WorldState(
        scene="INT. COURTROOM - DAY",
        facts=["trial in session", "witness on stand"],
        history=["opening statements completed"]
    )
    
    episode = Episode(
        episode_id="test_003",
        title="The Trial",
        genre="legal_drama",
        creation_time=datetime.now().isoformat(),
        characters=[character],
        world_state=world_state
    )
    
    # Test author prompt formatting
    author_prompt = format_author_prompt(episode, current_turn=1)
    
    assert "AUTHOR" in author_prompt or "GAME MASTER" in author_prompt
    assert "courtroom" in author_prompt.lower()
    assert "trial in session" in author_prompt
    assert "david" in author_prompt
    assert "JSON" in author_prompt
    
    print("✓ Prompt formatting tests passed")


def test_episode_serialization():
    """Test episode JSON serialization and deserialization"""
    print("Testing episode serialization...")
    
    # Create complex episode
    alice_profile = CharacterProfile(
        age=29,
        gender="female", 
        ethnicity="British",
        occupation="spy",
        core_traits=["secretive", "clever"],
        intrinsic_prefs=["puzzles", "danger"],
        lt_memory=["trained at MI6", "speaks 5 languages"]
    )
    
    alice_state = CharacterState(
        emotion="suspicious",
        location="embassy",
        short_term_beliefs=["target is here", "mission is compromised"],
        short_term_goals=["extract information", "avoid detection"],
        plans=[
            Plan("seduce_target", "active"),
            Plan("plant_bug", "pending")
        ]
    )
    
    bob_profile = CharacterProfile(
        age=45,
        gender="male",
        ethnicity="Russian",
        occupation="diplomat",
        core_traits=["charming", "dangerous"],
        intrinsic_prefs=["power", "vodka"],
        lt_memory=["former KGB", "knows Alice's real identity"]
    )
    
    bob_state = CharacterState(
        emotion="amused",
        location="embassy",
        short_term_beliefs=["Alice is a spy", "she doesn't know I know"],
        short_term_goals=["play along", "gather intel"],
        plans=[Plan("test_alice", "active")]
    )
    
    characters = [
        Character("alice", alice_profile, alice_state),
        Character("bob", bob_profile, bob_state)
    ]
    
    world_state = WorldState(
        scene="INT. EMBASSY BALLROOM - NIGHT",
        facts=["diplomatic reception in progress", "security is tight"],
        history=["guests arrived", "champagne served", "alice spotted bob"]
    )
    
    episode = Episode(
        episode_id="spy_001",
        title="The Embassy Affair",
        genre="espionage",
        creation_time="2024-01-01T20:00:00",
        characters=characters,
        world_state=world_state
    )
    
    # Add some claims
    episode.add_claim("Alice is undercover", "belief", True, ["alice"], 0)
    episode.add_claim("Bob knows Alice's identity", "knowledge", True, ["bob"], 0)
    episode.add_claim("The reception is a cover", "fact", True, ["narrator"], 0)
    
    # Add some turns
    episode.turns.extend([
        Turn(
            turn_id=1,
            speaker="alice",
            dialogue="What a lovely evening, Mr. Volkov.",
            actions=["approach_bob"],
            self_updates={"emotion": "flirtatious"},
            claims_referenced=["c000"]
        ),
        Turn(
            turn_id=2,
            speaker="bob", 
            dialogue="Indeed, Miss... Sterling, was it?",
            actions=["smile_knowingly"],
            self_updates={"short_term_goals_add": ["test_her_cover"]},
            claims_referenced=["c001"]
        )
    ])
    
    # Test serialization
    json_str = episode.to_json()
    assert isinstance(json_str, str)
    
    # Test deserialization
    episode_restored = Episode.from_json(json_str)
    
    # Verify restoration
    assert episode_restored.episode_id == "spy_001"
    assert episode_restored.title == "The Embassy Affair"
    assert len(episode_restored.characters) == 2
    assert len(episode_restored.claim_ledger) == 3
    assert len(episode_restored.turns) == 2
    
    alice_restored = episode_restored.get_character("alice")
    assert alice_restored is not None
    assert alice_restored.profile.age == 29
    assert alice_restored.state.emotion == "suspicious"
    assert "mission is compromised" in alice_restored.state.short_term_beliefs
    assert len(alice_restored.state.plans) == 2
    
    bob_restored = episode_restored.get_character("bob")
    assert bob_restored is not None
    assert bob_restored.profile.occupation == "diplomat"
    assert "Alice is a spy" in bob_restored.state.short_term_beliefs
    
    # Verify claims
    assert episode_restored.claim_ledger[0].text == "Alice is undercover"
    assert episode_restored.claim_ledger[1].visible_to == ["bob"]
    
    # Verify turns
    assert episode_restored.turns[0].dialogue == "What a lovely evening, Mr. Volkov."
    assert episode_restored.turns[1].speaker == "bob"
    
    print("✓ Episode serialization tests passed")


def run_all_tests():
    """Run all tests"""
    print("Running agentic framework tests...\n")
    
    try:
        test_data_models()
        test_character_agent()
        test_author_agent()
        test_prompt_formatting()
        test_episode_serialization()
        
        print("\n🎉 All tests passed! Framework is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 