#!/usr/bin/env python3
"""
Demo script for Phase 2: End-to-end episode generation
Shows the complete simulation pipeline with real LLM calls, logging, and transcript generation
"""

import os
from datetime import datetime
from models import *
from simulation import EpisodeSimulator, quick_simulate


def create_heist_episode():
    """Create a thrilling heist episode with conflicting character motivations"""
    
    # The Mastermind - Ana
    ana_profile = CharacterProfile(
        age=42,
        gender="female",
        ethnicity="Spanish",
        occupation="art_appraiser",
        core_traits=["calculating", "sophisticated", "ruthless"],
        intrinsic_prefs=["fine_art", "expensive_wine", "chess"],
        lt_memory=[
            "daughter of famous art forger",
            "lost family fortune to legal fees",
            "knows every security system in the city"
        ]
    )
    
    ana_state = CharacterState(
        emotion="focused",
        location="warehouse",
        short_term_beliefs=[
            "tonight's the perfect opportunity",
            "Marcus is getting cold feet",
            "security rotation changes at midnight"
        ],
        short_term_goals=[
            "keep the team motivated",
            "finalize escape route",
            "ensure no witnesses"
        ],
        plans=[
            Plan("neutralize_guards", "pending"),
            Plan("crack_vault_code", "active")
        ]
    )
    
    # The Hacker - Marcus
    marcus_profile = CharacterProfile(
        age=29,
        gender="male",
        ethnicity="African-American",
        occupation="cybersecurity_consultant",
        core_traits=["brilliant", "anxious", "moral"],
        intrinsic_prefs=["video_games", "energy_drinks", "coding"],
        lt_memory=[
            "parents were teachers",
            "arrested for hacking at 16",
            "promised girlfriend he'd go straight"
        ]
    )
    
    marcus_state = CharacterState(
        emotion="nervous",
        location="warehouse",
        short_term_beliefs=[
            "this job feels wrong",
            "Ana is hiding something",
            "museum has upgraded security"
        ],
        short_term_goals=[
            "disable alarm system",
            "find excuse to leave",
            "protect his reputation"
        ],
        plans=[
            Plan("hack_security_cameras", "active"),
            Plan("create_backup_plan", "pending")
        ]
    )
    
    # The Inside Woman - Sofia
    sofia_profile = CharacterProfile(
        age=35,
        gender="female",
        ethnicity="Italian-American",
        occupation="museum_curator",
        core_traits=["passionate", "conflicted", "desperate"],
        intrinsic_prefs=["Renaissance_art", "classical_music", "old_books"],
        lt_memory=[
            "PhD in Art History from Yale",
            "mother needs expensive cancer treatment",
            "discovered the painting's true origin"
        ]
    )
    
    sofia_state = CharacterState(
        emotion="torn",
        location="museum_office",
        short_term_beliefs=[
            "the painting was stolen from my family",
            "museum board won't listen to evidence",
            "this is my only chance for justice"
        ],
        short_term_goals=[
            "provide building access",
            "avoid security cameras",
            "document the theft properly"
        ],
        plans=[
            Plan("disable_door_locks", "pending"),
            Plan("plant_evidence", "active")
        ]
    )
    
    world_state = WorldState(
        scene="INT. ABANDONED WAREHOUSE / INT. MUSEUM - NIGHT",
        facts=[
            "Monet painting worth $50M on display",
            "museum has motion sensors and cameras",
            "night security makes rounds every 2 hours",
            "painting was looted from Sofia's family in WWII",
            "Ana hired the team through intermediaries"
        ],
        history=[
            "team assembled 3 months ago",
            "Sofia provided museum blueprints",
            "Marcus hacked preliminary security",
            "Ana studied guard patterns for weeks",
            "tonight is the museum's gala fundraiser"
        ]
    )
    
    episode = Episode(
        episode_id="heist_001",
        title="The Monet Vindication",
        genre="heist_thriller",
        creation_time=datetime.now().isoformat(),
        characters=[
            Character("ana", ana_profile, ana_state),
            Character("marcus", marcus_profile, marcus_state),
            Character("sofia", sofia_profile, sofia_state)
        ],
        world_state=world_state
    )
    
    # Add initial claims for faithfulness evaluation
    episode.add_claim("Ana is the mastermind of the heist", "fact", True, ["narrator"], 0)
    episode.add_claim("Marcus has moral reservations", "psychological", True, ["marcus"], 0)
    episode.add_claim("Sofia believes the painting belongs to her family", "belief", True, ["sofia"], 0)
    episode.add_claim("The painting was stolen during WWII", "historical_fact", True, ["sofia", "narrator"], 0)
    episode.add_claim("Ana's true motives are unknown to the team", "hidden_knowledge", True, ["narrator"], 0)
    episode.add_claim("Security changes shifts at midnight", "intelligence", True, ["ana", "marcus", "sofia"], 0)
    
    return episode


def create_family_dinner_episode():
    """Create a domestic drama with family secrets"""
    
    # The Mother - Elena
    elena_profile = CharacterProfile(
        age=58,
        gender="female",
        ethnicity="Mexican-American",
        occupation="retired_nurse",
        core_traits=["protective", "traditional", "intuitive"],
        intrinsic_prefs=["family_traditions", "telenovelas", "cooking"],
        lt_memory=[
            "immigrated at age 20",
            "worked double shifts to support family",
            "suspects husband's affair"
        ]
    )
    
    elena_state = CharacterState(
        emotion="suspicious",
        location="dining_room",
        short_term_beliefs=[
            "David is hiding something",
            "Carmen seems upset tonight",
            "this might be the last family dinner"
        ],
        short_term_goals=[
            "keep family together",
            "find out what's wrong",
            "protect her children"
        ]
    )
    
    # The Father - David
    david_profile = CharacterProfile(
        age=61,
        gender="male", 
        ethnicity="Mexican-American",
        occupation="construction_foreman",
        core_traits=["proud", "stubborn", "guilty"],
        intrinsic_prefs=["soccer", "beer", "old_music"],
        lt_memory=[
            "built the family business from nothing",
            "missed many family events for work",
            "made a terrible mistake last month"
        ]
    )
    
    david_state = CharacterState(
        emotion="ashamed",
        location="dining_room", 
        short_term_beliefs=[
            "Elena suspects something",
            "business is failing",
            "family will hate him when they know"
        ],
        short_term_goals=[
            "avoid Elena's questions",
            "tell them about the business",
            "ask for forgiveness"
        ]
    )
    
    # The Daughter - Carmen  
    carmen_profile = CharacterProfile(
        age=32,
        gender="female",
        ethnicity="Mexican-American", 
        occupation="doctor",
        core_traits=["ambitious", "stressed", "caring"],
        intrinsic_prefs=["medical_journals", "yoga", "helping_others"],
        lt_memory=[
            "first in family to go to college",
            "struggling with work-life balance",
            "recently discovered she's pregnant"
        ]
    )
    
    carmen_state = CharacterState(
        emotion="overwhelmed",
        location="dining_room",
        short_term_beliefs=[
            "parents are acting strange",
            "need to tell family about pregnancy",
            "husband doesn't know yet"
        ],
        short_term_goals=[
            "find right moment to share news",
            "assess family stability",
            "get parents' support"
        ]
    )
    
    world_state = WorldState(
        scene="INT. FAMILY HOME - SUNDAY EVENING",
        facts=[
            "family gathers every Sunday for dinner",
            "David's construction business is bankrupt",
            "Carmen is 8 weeks pregnant",
            "Elena found suspicious receipts",
            "this house may be foreclosed"
        ],
        history=[
            "Elena cooked all day",
            "David arrived late from work",
            "Carmen canceled her date to be here",
            "tension has been building for weeks"
        ]
    )
    
    episode = Episode(
        episode_id="family_001",
        title="Sunday Dinner Confessions",
        genre="family_drama",
        creation_time=datetime.now().isoformat(),
        characters=[
            Character("elena", elena_profile, elena_state),
            Character("david", david_profile, david_state),
            Character("carmen", carmen_profile, carmen_state)
        ],
        world_state=world_state
    )
    
    # Add claims
    episode.add_claim("David's business is failing", "fact", True, ["david", "narrator"], 0)
    episode.add_claim("Carmen is pregnant", "fact", True, ["carmen", "narrator"], 0)
    episode.add_claim("Elena suspects her husband", "belief", True, ["elena"], 0)
    episode.add_claim("The family is about to face major changes", "foreshadowing", True, ["narrator"], 0)
    
    return episode


def demo_simulation_with_logging():
    """Demonstrate full simulation with detailed logging"""
    
    print("🎬 PHASE 2 DEMO: Agentic Dialogue Framework")
    print("=" * 60)
    
    # Choose episode
    print("\nChoose an episode to simulate:")
    print("1. The Monet Vindication (heist thriller)")
    print("2. Sunday Dinner Confessions (family drama)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        episode = create_heist_episode()
        max_turns = 12
    elif choice == "2":
        episode = create_family_dinner_episode()
        max_turns = 10
    else:
        print("Invalid choice, defaulting to heist...")
        episode = create_heist_episode()
        max_turns = 12
    
    print(f"\n🎭 Creating episode: {episode.title}")
    print(f"Characters: {[char.char_id for char in episode.characters]}")
    print(f"Initial claims: {len(episode.claim_ledger)}")
    print(f"Genre: {episode.genre}")
    
    # Run simulation
    print(f"\n🚀 Starting simulation (max {max_turns} turns)...")
    print("This will make real LLM calls - please wait...\n")
    
    simulator = EpisodeSimulator(max_turns=max_turns, enable_logging=True)
    
    try:
        result = simulator.simulate_episode(episode)
        
        if result["success"]:
            print("✅ Simulation completed successfully!")
            
            # Show dialogue transcript
            print("\n" + "="*60)
            print("📝 DIALOGUE TRANSCRIPT")
            print("="*60)
            print(result["dialogue_transcript"])
            
            # Show key statistics
            print("\n" + "="*60)
            print("📊 SIMULATION STATISTICS")
            print("="*60)
            summary = result["summary"]
            print(f"Episode ID: {summary['episode_id']}")
            print(f"Duration: {summary['duration_seconds']:.1f} seconds")
            print(f"Total turns: {summary['total_turns']}")
            print(f"Total claims generated: {summary['total_claims']}")
            print(f"Character state changes: {summary['state_changes']}")
            print(f"Final world facts: {summary['final_world_facts']}")
            
            # Show state evolution
            print("\n" + "="*60)
            print("🔄 CHARACTER STATE EVOLUTION")
            print("="*60)
            logs = result["simulation_logs"]
            
            for change in logs.state_history:
                if change["updates_applied"]:
                    print(f"Turn {change['turn_id']} - {change['character_id'].upper()}:")
                    print(f"  Updates: {change['updates_applied']}")
            
            # Show claims analysis
            print("\n" + "="*60)
            print("🎯 CLAIMS ANALYSIS (for faithfulness evaluation)")
            print("="*60)
            
            final_episode = result["episode"]
            
            # Group claims by visibility
            character_visible = {}
            narrator_only = []
            
            for claim in final_episode.claim_ledger:
                if claim.visible_to == ["narrator"]:
                    narrator_only.append(claim)
                else:
                    for char_id in claim.visible_to:
                        if char_id != "narrator":
                            if char_id not in character_visible:
                                character_visible[char_id] = []
                            character_visible[char_id].append(claim)
            
            print(f"Narrator-only claims (hidden): {len(narrator_only)}")
            for claim in narrator_only[:3]:  # Show first 3
                print(f"  • {claim.text}")
            
            print(f"\nCharacter-visible claims:")
            for char_id, claims in character_visible.items():
                print(f"  {char_id}: {len(claims)} claims")
                for claim in claims[:2]:  # Show first 2 per character
                    print(f"    • {claim.text}")
            
            # Save detailed transcript
            filename = f"episode_{episode.episode_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(result["detailed_transcript"])
            
            print(f"\n💾 Detailed transcript saved to: {filename}")
            
            # Save episode JSON
            json_filename = f"episode_{episode.episode_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_filename, 'w') as f:
                f.write(final_episode.to_json())
            
            print(f"💾 Episode JSON saved to: {json_filename}")
            
        else:
            print("❌ Simulation failed!")
            
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()


def demo_quick_simulate():
    """Demonstrate the quick simulate function"""
    
    print("\n" + "="*60)
    print("⚡ QUICK SIMULATE DEMO")
    print("="*60)
    
    # Create simple episode
    profile = CharacterProfile(
        age=28,
        gender="female",
        ethnicity="American",
        occupation="journalist",
        core_traits=["curious", "persistent"],
        intrinsic_prefs=["truth", "coffee"],
        lt_memory=["uncovered city corruption scandal"]
    )
    
    state = CharacterState(
        emotion="determined",
        location="newsroom",
        short_term_beliefs=["mayor is hiding something"],
        short_term_goals=["get the story"]
    )
    
    episode = Episode(
        episode_id="quick_demo",
        title="Breaking News",
        genre="journalism",
        creation_time=datetime.now().isoformat(),
        characters=[Character("sarah", profile, state)],
        world_state=WorldState("INT. NEWSROOM - LATE NIGHT", ["deadline approaching"])
    )
    
    print("Running quick simulation (5 turns, no detailed logging)...")
    
    try:
        transcript = quick_simulate(episode, max_turns=5)
        print("\n📝 Quick Transcript:")
        print("-" * 40)
        print(transcript)
        
    except Exception as e:
        print(f"❌ Quick simulate failed: {e}")


if __name__ == "__main__":
    print("Welcome to the Agentic Dialogue Framework Phase 2 Demo!")
    print("This demonstrates end-to-end episode generation with LLM agents.\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("The simulation may fail without a valid API key.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'\n")
    
    demo_simulation_with_logging()
    demo_quick_simulate()
    
    print("\n🎉 Phase 2 demo completed!")
    print("\nNext steps:")
    print("- Run test_simulation.py to verify all components")
    print("- Create your own episodes with custom characters")
    print("- Use the generated transcripts for summarization evaluation")
    print("- Implement Phase 3: claim extraction and faithfulness scoring") 