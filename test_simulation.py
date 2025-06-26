#!/usr/bin/env python3
"""
Test suite for the simulation engine (Phase 2)
Tests the full end-to-end episode generation with logging and transcripts
"""

import os
from datetime import datetime
from models import *
from simulation import EpisodeSimulator, TranscriptFormatter, SimulationLogger, quick_simulate


def test_simulation_engine_mock():
    """Test simulation engine with mock responses (no LLM calls)"""
    print("Testing simulation engine with mock responses...")
    
    # Create test episode
    alice_profile = CharacterProfile(
        age=25,
        gender="female",
        ethnicity="Korean-American",
        occupation="software_engineer",
        core_traits=["logical", "introverted", "perfectionist"],
        intrinsic_prefs=["clean_code", "tea", "quiet_workspaces"],
        lt_memory=["graduated Stanford CS", "worked at Google for 2 years"]
    )
    
    alice_state = CharacterState(
        emotion="focused",
        location="office",
        short_term_beliefs=["deadline is approaching", "code review is tomorrow"],
        short_term_goals=["finish the feature", "write unit tests"],
        plans=[Plan("debug_api_issue", "active")]
    )
    
    bob_profile = CharacterProfile(
        age=32,
        gender="male",
        ethnicity="Canadian",
        occupation="product_manager",
        core_traits=["ambitious", "social", "impatient"],
        intrinsic_prefs=["meetings", "spreadsheets", "coffee"],
        lt_memory=["MBA from Wharton", "launched 3 successful products"]
    )
    
    bob_state = CharacterState(
        emotion="stressed",
        location="office",
        short_term_beliefs=["team is behind schedule", "stakeholders are concerned"],
        short_term_goals=["get status update", "push for faster delivery"],
        plans=[Plan("schedule_standup", "pending")]
    )
    
    world_state = WorldState(
        scene="INT. TECH STARTUP OFFICE - LATE AFTERNOON",
        facts=["sprint deadline is tomorrow", "client demo scheduled", "team working overtime"],
        history=["morning standup completed", "requirements changed", "Alice started debugging"]
    )
    
    episode = Episode(
        episode_id="test_simulation_001",
        title="The Sprint Deadline",
        genre="workplace_drama",
        creation_time=datetime.now().isoformat(),
        characters=[Character("alice", alice_profile, alice_state), 
                   Character("bob", bob_profile, bob_state)],
        world_state=world_state
    )
    
    # Mock the LLM calls by patching the agents
    from unittest.mock import patch
    
    mock_character_responses = [
        {
            "dialogue": "Hey Bob, I'm still working on that API bug. It's trickier than expected.",
            "actions": ["look_up_from_screen"],
            "self_updates": {"emotion": "apologetic"}
        },
        {
            "dialogue": "Alice, we really need this done by tomorrow. Can you give me a realistic timeline?",
            "actions": ["approach_alice_desk"],
            "self_updates": {"emotion": "pressured", "short_term_goals_add": ["get firm commitment"]}
        },
        {
            "dialogue": "I think I can have it working by midnight if I skip the unit tests for now.",
            "actions": ["rub_temples"],
            "self_updates": {"emotion": "overwhelmed", "plans_add": [{"plan_id": "work_late", "status": "active"}]}
        }
    ]
    
    mock_author_responses = [
        {
            "stage_directions": "(The office grows quiet as the conversation becomes tense)",
            "world_updates": {"history_add": ["Alice admits delay"]},
            "new_claims": [{"text": "API bug is more complex than estimated", "type": "fact", "truth_value": True, "visible_to": ["alice", "bob"]}]
        },
        {
            "stage_directions": "(Bob's frustration becomes visible)",
            "world_updates": {"history_add": ["Bob pressures Alice for timeline"]},
            "new_claims": [{"text": "Bob is concerned about deadline", "type": "emotion", "truth_value": True, "visible_to": ["alice", "bob"]}]
        },
        {
            "stage_directions": "(Alice makes a difficult decision)",
            "world_updates": {"history_add": ["Alice agrees to work late"]},
            "new_claims": [{"text": "Unit tests will be skipped", "type": "decision", "truth_value": True, "visible_to": ["alice", "bob"]}]
        }
    ]
    
    # Test without actual LLM calls by creating a custom simulator
    class MockSimulator(EpisodeSimulator):
        def __init__(self):
            super().__init__(max_turns=3, enable_logging=True)
            self.mock_char_idx = 0
            self.mock_author_idx = 0
        
        def _mock_character_act(self, character_id, world_context, recent_dialogue):
            response = mock_character_responses[self.mock_char_idx]
            self.mock_char_idx += 1
            return response
        
        def _mock_author_process(self, episode, character_response, character_id, turn_id):
            response = mock_author_responses[self.mock_author_idx]
            self.mock_author_idx += 1
            return response
    
    # Patch the agents to use mock responses
    mock_simulator = MockSimulator()
    
    def mock_char_act(self, world_context, recent_dialogue):
        return mock_simulator._mock_character_act(self.character.char_id, world_context, recent_dialogue)
    
    def mock_author_process(self, episode, char_response, char_id, turn_id):
        return mock_simulator._mock_author_process(episode, char_response, char_id, turn_id)
    
    with patch('agents.CharacterAgent.act', mock_char_act):
        with patch('agents.AuthorAgent.process_turn', mock_author_process):
            result = mock_simulator.simulate_episode(episode)
    
    # Verify results
    assert result["success"]
    assert len(result["episode"].turns) == 3
    assert len(result["episode"].claim_ledger) == 3  # 3 new claims added during simulation
    assert "Alice" in result["dialogue_transcript"] or "ALICE" in result["dialogue_transcript"]
    assert "Bob" in result["dialogue_transcript"] or "BOB" in result["dialogue_transcript"]
    assert "API bug" in result["dialogue_transcript"]
    
    # Check logging
    logs = result["simulation_logs"]
    assert len(logs.state_history) > 0
    assert len(logs.turn_logs) == 3
    
    # Check transcripts
    dialogue_transcript = result["dialogue_transcript"]
    assert "The Sprint Deadline" in dialogue_transcript
    assert "ALICE:" in dialogue_transcript
    assert "BOB:" in dialogue_transcript
    
    detailed_transcript = result["detailed_transcript"]
    assert "DETAILED TRANSCRIPT" in detailed_transcript
    assert "State Changes:" in detailed_transcript
    assert "FINAL STATE" in detailed_transcript
    
    print("✓ Simulation engine mock test passed")


def test_transcript_formatting():
    """Test transcript formatting utilities"""
    print("Testing transcript formatting...")
    
    # Create minimal episode for testing
    profile = CharacterProfile(25, "female", "American", "teacher", ["kind"], ["books"])
    state = CharacterState("happy", "classroom")
    character = Character("alice", profile, state)
    
    episode = Episode(
        episode_id="test_formatting",
        title="Test Episode",
        genre="educational",
        creation_time="2024-01-01T10:00:00",
        characters=[character],
        world_state=WorldState("INT. CLASSROOM - DAY", ["students present"], ["bell rang"])
    )
    
    # Add some turns
    episode.turns = [
        Turn(1, "alice", "Good morning, class!", ["smile", "wave"]),
        Turn(2, "alice", "Today we'll learn about photosynthesis.", ["point_to_board"])
    ]
    
    # Test dialogue transcript
    dialogue = TranscriptFormatter.format_dialogue_transcript(episode)
    assert "Test Episode" in dialogue
    assert "ALICE: Good morning, class!" in dialogue
    assert "(ALICE smile, wave)" in dialogue
    
    # Test detailed transcript (requires SimulationLogger)
    logger = SimulationLogger("test_formatting")
    logger.log_character_state_change("alice", 1, {}, {}, {"emotion": "cheerful"})
    
    detailed = TranscriptFormatter.format_detailed_transcript(episode, logger)
    assert "DETAILED TRANSCRIPT" in detailed
    assert "teacher" in detailed
    assert "TURN 1" in detailed
    assert "State Changes:" in detailed
    
    print("✓ Transcript formatting tests passed")


def test_simulation_logger():
    """Test simulation logging functionality"""
    print("Testing simulation logger...")
    
    logger = SimulationLogger("test_episode")
    
    # Test state change logging
    old_state = {"emotion": "neutral", "beliefs": ["test"]}
    new_state = {"emotion": "excited", "beliefs": ["test", "new_info"]}
    updates = {"emotion": "excited", "beliefs_add": ["new_info"]}
    
    logger.log_character_state_change("alice", 1, old_state, new_state, updates)
    
    assert len(logger.state_history) == 1
    assert logger.state_history[0]["character_id"] == "alice"
    assert logger.state_history[0]["turn_id"] == 1
    assert logger.state_history[0]["updates_applied"] == updates
    
    # Test turn completion logging
    logger.log_turn_completion(1, "alice", "Hello world", ["wave"], {"facts_add": ["greeting"]}, [])
    
    assert len(logger.turn_logs) == 1
    assert logger.turn_logs[0]["speaker"] == "alice"
    assert logger.turn_logs[0]["dialogue"] == "Hello world"
    
    print("✓ Simulation logger tests passed")


def test_quick_simulate():
    """Test the convenience quick_simulate function"""
    print("Testing quick_simulate function...")
    
    from unittest.mock import patch
    
    # Create minimal episode
    profile = CharacterProfile(30, "male", "British", "chef", ["creative"], ["cooking"])
    state = CharacterState("excited", "kitchen")
    character = Character("gordon", profile, state)
    
    episode = Episode(
        episode_id="quick_test",
        title="Quick Test",
        genre="cooking_show",
        creation_time=datetime.now().isoformat(),
        characters=[character],
        world_state=WorldState("INT. KITCHEN - DAY")
    )
    
    # Test that quick_simulate returns a string (even if mocked)
    # In real usage this would call LLMs, but we're testing the structure
    with patch('agents.CharacterAgent.act', return_value={"dialogue": "Let's cook!", "actions": [], "self_updates": {}}):
        with patch('agents.AuthorAgent.process_turn', return_value={"stage_directions": "", "world_updates": {}, "new_claims": []}):
            transcript = quick_simulate(episode, max_turns=2)
    
    assert isinstance(transcript, str)
    assert "Quick Test" in transcript
    
    print("✓ Quick simulate test passed")


def run_simulation_tests():
    """Run all simulation tests"""
    print("Running Phase 2 simulation tests...\n")
    
    try:
        test_simulation_logger()
        test_transcript_formatting()
        test_simulation_engine_mock()
        test_quick_simulate()
        
        print("\n🎉 All Phase 2 simulation tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_simulation_tests()
    exit(0 if success else 1) 