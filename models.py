from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


@dataclass
class CharacterProfile:
    """Immutable character background and traits"""
    age: int
    gender: str
    ethnicity: str
    occupation: str
    core_traits: List[str]
    intrinsic_prefs: List[str]
    lt_memory: List[str] = field(default_factory=list)


@dataclass
class Plan:
    plan_id: str
    status: str  # "pending", "active", "completed", "failed"


@dataclass
class CharacterState:
    """Mutable character state that can be updated by the agent"""
    emotion: str
    location: str
    short_term_beliefs: List[str] = field(default_factory=list)
    short_term_goals: List[str] = field(default_factory=list)
    plans: List[Plan] = field(default_factory=list)


@dataclass
class Character:
    char_id: str
    profile: CharacterProfile
    state: CharacterState


@dataclass
class Claim:
    claim_id: str
    text: str
    type: str  # "event", "belief", "goal", "perception", etc.
    truth_value: bool
    visible_to: List[str]  # list of char_ids or ["narrator"] for omniscient only
    introduced_in_turn: int


@dataclass
class Turn:
    turn_id: int
    speaker: str
    dialogue: str = ""
    actions: List[str] = field(default_factory=list)
    self_updates: Dict[str, Any] = field(default_factory=dict)
    claims_referenced: List[str] = field(default_factory=list)


@dataclass
class WorldState:
    scene: str
    facts: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)


@dataclass
class Episode:
    episode_id: str
    title: str
    genre: str
    creation_time: str
    characters: List[Character]
    world_state: WorldState
    claim_ledger: List[Claim] = field(default_factory=list)
    turns: List[Turn] = field(default_factory=list)

    def to_json(self) -> str:
        """Convert episode to JSON string"""
        def convert_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            else:
                return obj
        
        return json.dumps(convert_to_dict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'Episode':
        """Create episode from JSON string"""
        data = json.loads(json_str)
        
        # Convert characters
        characters = []
        for char_data in data['characters']:
            profile = CharacterProfile(**char_data['profile'])
            
            # Convert plans in state
            plans = [Plan(**plan) for plan in char_data['state']['plans']]
            state_data = char_data['state'].copy()
            state_data['plans'] = plans
            state = CharacterState(**state_data)
            
            characters.append(Character(char_data['char_id'], profile, state))
        
        # Convert world state
        world_state = WorldState(**data['world_state'])
        
        # Convert claims
        claims = [Claim(**claim) for claim in data['claim_ledger']]
        
        # Convert turns
        turns = [Turn(**turn) for turn in data['turns']]
        
        return cls(
            episode_id=data['episode_id'],
            title=data['title'],
            genre=data['genre'],
            creation_time=data['creation_time'],
            characters=characters,
            world_state=world_state,
            claim_ledger=claims,
            turns=turns
        )

    def get_character(self, char_id: str) -> Optional[Character]:
        """Get character by ID"""
        for char in self.characters:
            if char.char_id == char_id:
                return char
        return None

    def add_claim(self, text: str, claim_type: str, truth_value: bool, 
                  visible_to: List[str], turn_id: int) -> str:
        """Add a new claim and return its ID"""
        claim_id = f"c{len(self.claim_ledger):03d}"
        claim = Claim(
            claim_id=claim_id,
            text=text,
            type=claim_type,
            truth_value=truth_value,
            visible_to=visible_to,
            introduced_in_turn=turn_id
        )
        self.claim_ledger.append(claim)
        return claim_id 