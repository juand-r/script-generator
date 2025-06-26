#!/usr/bin/env python3
"""
Medical Episode Demo: Kitchen Accident
A patient visits the doctor after cutting her arm while cooking
"""

import os
from datetime import datetime
from models import *
from simulation import EpisodeSimulator


def create_kitchen_accident_episode():
    """Create a medical episode where Sarah cut her arm while chopping onions"""
    
    # The Patient - Sarah
    sarah_profile = CharacterProfile(
        age=32,
        gender="female",
        ethnicity="Asian-American",
        occupation="software_engineer",
        core_traits=["anxious", "loves to sing and dance when it's not appropriate", "shy", "detail_oriented", "health_conscious", "scatterbrained", "has no filter", "does not repeat herself"],
        intrinsic_prefs=["cooking", "organization", "hiking", "climbing", "classical Indian music"],
        lt_memory=[
            "always careful in the kitchen",
            "has health insurance through work",
            "mother is a nurse"
        ]
    )
    
    sarah_state = CharacterState(
        emotion="worried",
        location="emergency_room",
        short_term_beliefs=[
            "the cut looks deep",
            "I might need stitches",
            "I should have been more careful",
            "the bleeding has mostly stopped",
            "Tell my boyfriend I love him",
            "I am anxious about whether I will be able to climb Mount Kilimanjaro next month"
        ],
        short_term_goals=[
            "get proper medical care",
            "make sure there's no nerve damage",
            "avoid infection",
            "get back to work tomorrow"

        ],
        plans=[
            Plan("describe_accident_clearly", "active"),
            Plan("ask_about_scar_prevention", "pending")
        ]
    )
    
    # The Doctor - Dr. Martinez
    doctor_profile = CharacterProfile(
        age=45,
        gender="male", 
        ethnicity="Hispanic",
        occupation="emergency_physician",
        core_traits=["experienced", "thorough", "reassuring"],
        intrinsic_prefs=["evidence_based_medicine", "patient_education", "efficiency"],
        lt_memory=[
            "15 years in emergency medicine",
            "sees many kitchen accidents",
            "loves his golden retriever",
            "loves talking about his personal life with patients"
        ]
    )
    
    doctor_state = CharacterState(
        emotion="professional",
        location="emergency_room",
        short_term_beliefs=[
            "patient seems anxious but cooperative",
            "wound needs proper assessment",
            "looks like a clean laceration",
            "patient is stable but a bit weird"
        ],
        short_term_goals=[
            "assess wound depth and damage",
            "clean and treat the laceration",
            "reassure the patient",
            "provide proper wound care instructions"
        ],
        plans=[
            Plan("examine_wound_thoroughly", "active"),
            Plan("will dictate the entire proocedure to the patient and for an ambient smartphone app to record and create a medical record.", "active"),
            Plan("check_for_nerve_damage", "pending"),
            Plan("apply_local_anesthetic", "pending"),
            Plan("will tell the patient that he loves his golden retriever", "activate")
        ]
    )
    
    # Create world state
    world_state = WorldState(
        scene="INT. EMERGENCY ROOM EXAMINATION ROOM - AFTERNOON",
        facts=[
            "patient has 3-inch laceration on left forearm",
            "accident occurred 45 minutes ago while cooking",
            "bleeding has been controlled with pressure",
            "patient is alert and oriented",
            "wound appears clean with no foreign objects",
            "patient's tetanus vaccination is current"
        ],
        history=[
            "Sarah was chopping onions for dinner",
            "knife slipped on wet cutting board",
            "she applied pressure with clean towel",
            "friend drove her to emergency room",
            "triage nurse cleaned and bandaged wound",
            "Dr. Martinez called in to examine patient"
        ]
    )
    
    episode = Episode(
        episode_id="medical_001",
        title="The Kitchen Accident",
        genre="medical_drama",
        creation_time=datetime.now().isoformat(),
        characters=[
            Character("sarah", sarah_profile, sarah_state),
            Character("dr_martinez", doctor_profile, doctor_state)
        ],
        world_state=world_state
    )
    
    # Add initial claims for faithfulness evaluation
    episode.add_claim("Sarah cut her arm while chopping onions", "fact", True, ["sarah", "dr_martinez"], 0)
    episode.add_claim("The laceration is 3 inches long", "medical_fact", True, ["dr_martinez"], 0)
    episode.add_claim("Sarah is worried about scarring", "patient_concern", True, ["sarah"], 0)
    episode.add_claim("Dr. Martinez has 15 years of emergency experience", "background", True, ["narrator"], 0)
    episode.add_claim("The wound needs stitches", "medical_assessment", False, ["narrator"], 0)  # To be determined
    episode.add_claim("Patient's tetanus vaccination is current", "medical_record", True, ["dr_martinez"], 0)
    episode.add_claim("Sarah is anxious about the procedure", "psychological", True, ["sarah", "dr_martinez"], 0)
    
    return episode


def demo_medical_episode():
    """Run the medical episode demo"""
    
    print("🏥 MEDICAL EPISODE DEMO: The Kitchen Accident")
    print("=" * 60)
    
    # Create episode
    episode = create_kitchen_accident_episode()
    
    print(f"\n🏥 Episode: {episode.title}")
    print(f"Setting: {episode.world_state.scene}")
    print(f"Characters: {[char.char_id for char in episode.characters]}")
    print(f"Initial medical facts: {len([f for f in episode.world_state.facts if 'patient' in f or 'wound' in f])}")
    print(f"Initial claims: {len(episode.claim_ledger)}")
    
    # Show character details
    print(f"\n👤 CHARACTERS:")
    for char in episode.characters:
        print(f"  • {char.char_id}: {char.profile.occupation}, {char.profile.age}yo")
        print(f"    Emotion: {char.state.emotion}")
        print(f"    Key goals: {char.state.short_term_goals[:2]}")
    
    # Run simulation
    print(f"\n🩺 Starting medical consultation simulation...")
    print("This will make real LLM calls - please wait...\n")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found")
        print("Set it with: export OPENAI_API_KEY='your-key-here'\n")
        return
    
    simulator = EpisodeSimulator(max_turns=30, enable_logging=True)
    
    try:
        result = simulator.simulate_episode(episode)
        
        if result["success"]:
            print("✅ Medical consultation completed!")
            
            # Show dialogue transcript
            print("\n" + "="*60)
            print("📋 MEDICAL CONSULTATION TRANSCRIPT")
            print("="*60)
            print(result["dialogue_transcript"])
            
            # Medical-specific analysis
            print("\n" + "="*60)
            print("🩺 MEDICAL ANALYSIS")
            print("="*60)
            
            final_episode = result["episode"]
            
            # Extract medical claims
            medical_claims = [c for c in final_episode.claim_ledger if c.type in ["medical_fact", "medical_assessment", "medical_record"]]
            patient_concerns = [c for c in final_episode.claim_ledger if c.type == "patient_concern"]
            
            print(f"Medical facts established: {len(medical_claims)}")
            for claim in medical_claims:
                print(f"  • {claim.text} (visible to: {claim.visible_to})")
            
            print(f"\nPatient concerns addressed: {len(patient_concerns)}")
            for claim in patient_concerns:
                print(f"  • {claim.text}")
            
            # Character state evolution
            print(f"\n🔄 CHARACTER STATE EVOLUTION:")
            logs = result["simulation_logs"]
            
            for change in logs.state_history:
                if change["updates_applied"]:
                    print(f"  {change['character_id']}: {change['updates_applied']}")
            
            # Save files
            print(f"\n💾 Saving medical consultation files...")
            
            # Save detailed transcript
            filename = f"medical_{episode.episode_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(result["detailed_transcript"])
            print(f"  Medical transcript: {filename}")
            
            # Save episode JSON
            json_filename = f"medical_{episode.episode_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_filename, 'w') as f:
                f.write(final_episode.to_json())
            print(f"  Medical episode JSON: {json_filename}")
            
            # Medical faithfulness summary
            print(f"\n🎯 MEDICAL FAITHFULNESS SUMMARY:")
            print(f"  Total claims: {len(final_episode.claim_ledger)}")
            print(f"  Patient-visible: {len([c for c in final_episode.claim_ledger if 'sarah' in c.visible_to])}")
            print(f"  Doctor-only: {len([c for c in final_episode.claim_ledger if c.visible_to == ['dr_martinez']])}")
            print(f"  Medical records: {len([c for c in final_episode.claim_ledger if c.type == 'medical_record'])}")
            
        else:
            print("❌ Medical consultation failed!")
            
    except Exception as e:
        print(f"❌ Error during medical simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🏥 Medical Episode Demo: Kitchen Accident")
    print("This demonstrates medical dialogue generation with patient-doctor interaction.\n")
    
    demo_medical_episode()
    
    print("\n🎉 Medical demo completed!")
    print("\nThis episode demonstrates:")
    print("- Medical knowledge and terminology")
    print("- Patient anxiety and concerns")
    print("- Doctor-patient communication")
    print("- Medical procedure explanation")
    print("- Claims about medical facts vs. patient perceptions") 