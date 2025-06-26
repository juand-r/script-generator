# Agentic Dialogue Framework

A framework for generating multi-agent conversations with **faithful claims tracking** designed to evaluate summarization systems. Each character is powered by an LLM agent that can modify its own internal state (beliefs, goals, emotions, plans) while engaging in realistic dialogue.

## 🎯 Purpose

This framework generates synthetic dialogue datasets where:
- **Every claim is tracked** with visibility metadata (who knows what, when)
- **Character states evolve** through self-modification during conversation  
- **Faithfulness evaluation** is built-in (claims vs. summary accuracy)
- **Rich character profiles** enable consistent, believable behavior

Perfect for testing summarization models on:
- Character knowledge vs. narrator omniscience
- Temporal claim evolution  
- False beliefs and unreliable narrators
- Multi-perspective narratives

## 🏗️ Architecture

```
Episode (JSON serializable)
├── Characters (with profiles & dynamic state)
├── World State (managed by AuthorAgent)  
├── Claim Ledger (for faithfulness evaluation)
└── Turns (dialogue + actions + self-updates)

Agents:
├── CharacterAgent (handles dialogue + self-state modification)
└── AuthorAgent (world state + claim tracking)
```

## 🚀 Quick Start

### 1. Setup

```bash
# Activate your virtual environment

# Install dependencies  
pip install openai

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"
# Or add it to your ~/.bashrc for persistence
```

### 2. Run Tests

```bash
python test_framework.py
```

You should see:
```
🎉 All tests passed! Framework is working correctly.
```

### 3. Generate Your First Episode

```python
from example_usage import create_sample_episode
from simulation import EpisodeSimulator

# Create episode with pre-defined characters
episode = create_sample_episode()

# Run simulation
simulator = EpisodeSimulator(max_turns=8)
result = simulator.simulate_episode(episode)

# Access results
print("🎬 Dialogue Transcript:")
print(result["dialogue_transcript"])

print("\n📊 Detailed Analysis:")  
print(result["detailed_transcript"])

print(f"\n📈 Simulation Summary:")
print(result["summary"])
```

## 📝 Creating Custom Episodes

### Basic Episode Structure

```python
from datetime import datetime
from models import *
from simulation import EpisodeSimulator

# 1. Create character profiles
alice_profile = CharacterProfile(
    age=30,
    gender="female", 
    ethnicity="Italian-American",
    occupation="detective",
    core_traits=["analytical", "skeptical", "persistent"],
    intrinsic_prefs=["truth", "justice", "strong_coffee"],
    lt_memory=["solved the riverside murders", "doesn't trust politicians"]
)

# 2. Set initial character state  
alice_state = CharacterState(
    emotion="focused",
    location="crime_scene",
    short_term_beliefs=["killer knew the victim", "this wasn't random"],
    short_term_goals=["find physical evidence", "interview witnesses"],
    plans=[Plan("check_security_cameras", "pending")]
)

alice = Character("alice", alice_profile, alice_state)

# 3. Create world state
world_state = WorldState(
    scene="INT. LUXURY APARTMENT - NIGHT",
    facts=["victim found at 23:30", "door was unlocked", "no signs of struggle"],
    history=["police arrived", "EMTs pronounced victim dead", "scene secured"]
)

# 4. Create episode
episode = Episode(
    episode_id="murder_mystery_001",
    title="The Unlocked Door",
    genre="crime_thriller", 
    creation_time=datetime.now().isoformat(),
    characters=[alice, bob],  # add more characters
    world_state=world_state
)

# 5. Add initial claims (optional)
episode.add_claim("Victim knew their killer", "hypothesis", True, ["alice"], 0)
episode.add_claim("Door lock was picked", "evidence", False, ["narrator"], 0)

# 6. Simulate!
simulator = EpisodeSimulator(max_turns=10)
result = simulator.simulate_episode(episode)
```

### Character Design Tips

**Rich Profiles Drive Better Dialogue:**

```python
# ✅ Good: Specific, conflicting traits
core_traits=["brilliant", "paranoid", "lonely", "protective"]
intrinsic_prefs=["encrypted_communication", "classical_music", "stray_cats"] 
lt_memory=["parents died in car crash", "won MIT scholarship", "betrayed by best friend"]

# ❌ Avoid: Generic traits
core_traits=["nice", "smart"]
intrinsic_prefs=["food", "movies"]
```

**Dynamic States Create Evolution:**

```python
# Characters can change during conversation:
{
  "dialogue": "I... I think I was wrong about you.",
  "self_updates": {
    "emotion": "remorseful", 
    "short_term_beliefs_remove": ["John is lying"],
    "short_term_beliefs_add": ["John was protecting someone"],
    "short_term_goals_add": ["apologize to John"]
  }
}
```

## 📊 Working with Results

### Access Transcripts

```python
result = simulator.simulate_episode(episode)

# Clean dialogue only
dialogue = result["dialogue_transcript"]

# Detailed with state changes  
detailed = result["detailed_transcript"]

# JSON for further processing
episode_json = result["episode"].to_json()
```

### Logging & State Tracking

```python
# Access simulation logs
logs = result["simulation_logs"]

# Character state changes over time
for change in logs.state_history:
    print(f"Turn {change['turn_id']}: {change['character_id']} -> {change['updates_applied']}")

# Turn-by-turn progression
for turn_log in logs.turn_logs:
    print(f"Turn {turn_log['turn_id']}: {turn_log['dialogue'][:50]}...")
```

### Claims for Evaluation

```python
episode = result["episode"]

# All claims generated
for claim in episode.claim_ledger:
    print(f"{claim.claim_id}: {claim.text}")
    print(f"  Visible to: {claim.visible_to}")
    print(f"  Truth value: {claim.truth_value}")
    print(f"  Type: {claim.type}")

# Filter by visibility (for faithfulness testing)
observer_claims = [c for c in episode.claim_ledger if "alice" in c.visible_to]
narrator_only = [c for c in episode.claim_ledger if c.visible_to == ["narrator"]]
```

## 🔧 Configuration Options

### Simulation Parameters

```python
simulator = EpisodeSimulator(
    max_turns=15,           # Maximum conversation length
    enable_logging=True     # Track state changes  
)

# Custom speaker order
result = simulator.simulate_episode(
    episode, 
    character_order=["alice", "bob", "alice", "carol"]  # Specific sequence
)
```

### LLM Settings

Edit `prompt_utils.py`:

```python
def call_openai(
    system_prompt: str,
    user_prompt: str, 
    model: str = "gpt-4o-mini",     # Change model
    temperature: float = 0.7,       # Creativity level
    max_tokens: int = 1000,         # Response length
    expect_json: bool = True
):
```

## 📁 File Structure

```
synthetic-agents/
├── models.py              # Data models (Episode, Character, etc.)
├── agents.py              # CharacterAgent & AuthorAgent classes  
├── prompt_utils.py        # OpenAI integration & prompt formatting
├── simulation.py          # Main simulation engine (NEW!)
├── test_framework.py      # Comprehensive tests
├── example_usage.py       # Sample episode creation
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🎬 Example Output

```
=== The Network Anomaly ===
Genre: corporate_thriller
Scene: INT. SECURE CORPORATE OFFICE - LATE EVENING

ALICE: Bob, you've been working late a lot lately. Everything alright?
    (ALICE approach_bob_desk, cross_arms)

BOB: Oh, just trying to catch up on some system maintenance. You know how it is.
    (BOB minimize_screen, turn_to_face_alice)

ALICE: System maintenance that requires accessing the financial database at 9 PM?
    (ALICE point_at_screen)

BOB: Look, Alice, I can explain...
```

**With detailed state tracking:**
```
--- TURN 2 ---
BOB: Oh, just trying to catch up on some system maintenance. You know how it is.
  Actions: minimize_screen, turn_to_face_alice
  State Changes:
    bob: {'emotion': 'defensive', 'short_term_beliefs_add': ['Alice is definitely suspicious']}
```

## 🔍 Next Steps

1. **Generate diverse episodes** with different genres/scenarios
2. **Create claim extraction tools** for summary evaluation  
3. **Build faithfulness metrics** (precision/recall over claims)
4. **Scale up** with batch episode generation

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'openai'"**
- Activate the correct virtual environment: `source ~/Dev/.venv/bin/activate`

**"OpenAI API key not found"**  
- Set environment variable: `export OPENAI_API_KEY="your-key"`
- Or add to `~/.bashrc` for persistence

**JSON parsing errors**
- Check LLM temperature (lower = more structured)
- Verify prompt format in `prompt_utils.py`

**Characters acting inconsistently**
- Add more specific `core_traits` and `lt_memory`
- Reduce `max_turns` for focused conversations

---

Built with ❤️ for faithful dialogue generation and summarization evaluation. 