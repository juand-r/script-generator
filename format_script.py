#!/usr/bin/env python3
"""
Simple script to convert episode JSON files to readable script format
Usage: python format_script.py episode_file.json
"""

import json
import sys
import argparse
from pathlib import Path


def format_actions(actions):
    """Format character actions into parenthetical"""
    if not actions:
        return ""
    return f"({', '.join(actions)}) "


def format_script_from_json(json_file_path):
    """Convert episode JSON to script format"""
    
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        episode_data = json.load(f)
    
    lines = []
    
    # Add header
    lines.append(f"=== {episode_data['title']} ===")
    lines.append(f"Genre: {episode_data['genre']}")
    lines.append(f"Scene: {episode_data['world_state']['scene']}")
    lines.append("")
    
    # Process turns
    for turn in episode_data['turns']:
        speaker = turn['speaker'].upper()
        dialogue = turn.get('dialogue', '')
        actions = turn.get('actions', [])
        
        if dialogue:  # Only show turns with actual dialogue
            action_text = format_actions(actions)
            lines.append(f"{speaker}: {action_text}{dialogue}")
        elif actions:  # Show actions even without dialogue
            action_text = format_actions(actions)
            lines.append(f"({speaker} {', '.join(actions)})")
    
    # Add world state changes if available
    world_history = episode_data['world_state'].get('history', [])
    if world_history:
        lines.append("")
        lines.append("--- Background Events ---")
        for event in world_history[-5:]:  # Show last 5 events
            lines.append(f"(Narrator: {event})")
    
    return "\n".join(lines)


def format_script_with_state_changes(json_file_path):
    """Convert episode JSON to script format with state changes noted"""
    
    with open(json_file_path, 'r') as f:
        episode_data = json.load(f)
    
    lines = []
    
    # Add header
    lines.append(f"=== {episode_data['title']} ===")
    lines.append(f"Genre: {episode_data['genre']}")
    lines.append(f"Scene: {episode_data['world_state']['scene']}")
    lines.append("")
    
    # Process turns with state changes
    for turn in episode_data['turns']:
        speaker = turn['speaker'].upper()
        dialogue = turn.get('dialogue', '')
        actions = turn.get('actions', [])
        self_updates = turn.get('self_updates', {})
        
        # Show dialogue line
        if dialogue:
            action_text = format_actions(actions)
            lines.append(f"{speaker}: {action_text}{dialogue}")
        elif actions:
            action_text = format_actions(actions)
            lines.append(f"({speaker} {', '.join(actions)})")
        
        # Show state changes as world descriptions
        if self_updates:
            state_changes = []
            
            if 'emotion' in self_updates:
                state_changes.append(f"{speaker.lower()} becomes {self_updates['emotion']}")
            
            if 'short_term_beliefs_add' in self_updates:
                for belief in self_updates['short_term_beliefs_add']:
                    state_changes.append(f"{speaker.lower()} now believes: {belief}")
            
            if 'short_term_goals_add' in self_updates:
                for goal in self_updates['short_term_goals_add']:
                    state_changes.append(f"{speaker.lower()} decides to: {goal}")
            
            if 'plans_add' in self_updates:
                for plan in self_updates['plans_add']:
                    state_changes.append(f"{speaker.lower()} plans to: {plan['plan_id']}")
            
            if state_changes:
                lines.append(f"({'; '.join(state_changes)})")
        
        lines.append("")  # Add space between turns
    
    return "\n".join(lines)


def format_dialogue_only(json_file_path):
    """Convert episode JSON to dialogue-only format"""
    
    with open(json_file_path, 'r') as f:
        episode_data = json.load(f)
    
    lines = []
    
    # Add header
    lines.append(f"=== {episode_data['title']} ===")
    lines.append(f"Genre: {episode_data['genre']}")
    lines.append(f"Scene: {episode_data['world_state']['scene']}")
    lines.append("")
    
    # Process turns - dialogue only
    for turn in episode_data['turns']:
        speaker = turn['speaker'].upper()
        dialogue = turn.get('dialogue', '')
        
        if dialogue:  # Only show turns with actual dialogue
            lines.append(f"{speaker}: {dialogue}")
    
    return "\n".join(lines)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Convert episode JSON files to readable script format')
    parser.add_argument('json_file', help='Episode JSON file to convert')
    parser.add_argument('--dialogue-only', '-d', action='store_true', 
                       help='Output only dialogue without actions or state changes')
    parser.add_argument('--output', '-o', help='Output file name (optional)')
    
    args = parser.parse_args()
    
    if not Path(args.json_file).exists():
        print(f"Error: File '{args.json_file}' not found")
        sys.exit(1)
    
    try:
        if args.dialogue_only:
            # Generate dialogue-only format
            print("=== DIALOGUE ONLY ===")
            dialogue_script = format_dialogue_only(args.json_file)
            print(dialogue_script)
            
            # Save to file
            if args.output:
                output_file = args.output
            else:
                output_file = args.json_file.replace('.json', '_dialogue_only.txt')
            
            with open(output_file, 'w') as f:
                f.write(dialogue_script)
            
            print(f"\n💾 Dialogue-only script saved to: {output_file}")
            
        else:
            # Generate both formats (original behavior)
            print("=== SIMPLE SCRIPT FORMAT ===")
            simple_script = format_script_from_json(args.json_file)
            print(simple_script)
            
            print("\n\n=== SCRIPT WITH STATE CHANGES ===")
            detailed_script = format_script_with_state_changes(args.json_file)
            print(detailed_script)
            
            # Save to file
            if args.output:
                output_file = args.output
            else:
                output_file = args.json_file.replace('.json', '_script.txt')
            
            with open(output_file, 'w') as f:
                f.write("=== SIMPLE SCRIPT FORMAT ===\n")
                f.write(simple_script)
                f.write("\n\n=== SCRIPT WITH STATE CHANGES ===\n")
                f.write(detailed_script)
            
            print(f"\n💾 Script saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Show usage example if no arguments provided
    if len(sys.argv) == 1:
        print("Usage examples:")
        print("  python format_script.py episode_file.json")
        print("  python format_script.py episode_file.json --dialogue-only")
        print("  python format_script.py episode_file.json -d -o dialogue.txt")
        print("\nOptions:")
        print("  -d, --dialogue-only    Output only dialogue without actions")
        print("  -o, --output FILE      Specify output filename")
        sys.exit(1)
    
    main() 