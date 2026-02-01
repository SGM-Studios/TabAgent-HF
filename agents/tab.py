"""
TabAgent - MIDI to Tablature Conversion
Uses Viterbi dynamic programming for optimal fingering
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

from .ear import Note


@dataclass
class TabNote:
    """A note positioned on the fretboard."""
    string: int          # String index (0 = lowest)
    fret: int            # Fret number (0 = open)
    start_time: float    # Start time in seconds
    end_time: float      # End time in seconds
    technique: str       # "pick", "slide", "hammer", "pull"
    pitch: int           # Original MIDI pitch


class TabAgent:
    """
    Convert MIDI notes to playable guitar/bass tablature.
    
    Uses Viterbi-style dynamic programming to find optimal fingering path.
    Detects techniques: slides, hammer-ons, pull-offs.
    """
    
    # String names for display
    GUITAR_STRINGS = ["E", "A", "D", "G", "B", "e"]
    BASS_4_STRINGS = ["E", "A", "D", "G"]
    BASS_5_STRINGS = ["B", "E", "A", "D", "G"]
    
    def __init__(
        self,
        tuning: List[int] = None,
        num_frets: int = 24,
        instrument: str = "guitar"
    ):
        """
        Initialize TabAgent.
        
        Args:
            tuning: MIDI note numbers for open strings (low to high)
            num_frets: Maximum fret number
            instrument: "guitar" or "bass"
        """
        self.instrument = instrument.lower()
        self.num_frets = num_frets
        
        if tuning is None:
            if self.instrument == "bass":
                self.tuning = [23, 28, 33, 38, 43]  # 5-string bass
            else:
                self.tuning = [40, 45, 50, 55, 59, 64]  # Standard guitar
        else:
            self.tuning = tuning
            
        self.num_strings = len(self.tuning)
        
        # Cost weights for Viterbi algorithm
        self.fret_distance_weight = 1.5
        self.string_change_weight = 2.0
        self.legato_bonus = -5.0  # Negative = reward
        self.string_skip_penalty = 5.0
        
        print(f"🎸 TabAgent initialized ({self.instrument}, {self.num_strings} strings)")
    
    def generate_tab(self, notes: List[Note]) -> List[TabNote]:
        """
        Generate tablature from MIDI notes using Viterbi algorithm.
        
        Args:
            notes: List of Note objects from EarAgent
            
        Returns:
            List of TabNote objects with optimal fingering
        """
        if not notes:
            return []
            
        print(f"📝 Generating tablature for {len(notes)} notes...")
        
        # Sort notes by start time
        notes = sorted(notes, key=lambda n: n.start_time)
        
        # Find all possible positions for each note
        note_positions = []
        for note in notes:
            positions = self._find_positions(note.pitch)
            if positions:
                note_positions.append((note, positions))
            else:
                print(f"   ⚠️  Note {note.pitch} unplayable, skipping")
        
        if not note_positions:
            return []
        
        # Viterbi dynamic programming
        tab_notes = self._viterbi_path(note_positions)
        
        # Detect techniques
        tab_notes = self._detect_techniques(tab_notes)
        
        print(f"   ✅ Generated {len(tab_notes)} tab notes")
        return tab_notes
    
    def _find_positions(self, pitch: int) -> List[Tuple[int, int]]:
        """
        Find all possible (string, fret) positions for a pitch.
        
        Args:
            pitch: MIDI pitch number
            
        Returns:
            List of (string_index, fret_number) tuples
        """
        positions = []
        
        for string_idx, open_pitch in enumerate(self.tuning):
            fret = pitch - open_pitch
            if 0 <= fret <= self.num_frets:
                positions.append((string_idx, fret))
        
        return positions
    
    def _viterbi_path(
        self,
        note_positions: List[Tuple[Note, List[Tuple[int, int]]]]
    ) -> List[TabNote]:
        """
        Find optimal fingering path using Viterbi algorithm.
        
        Args:
            note_positions: List of (note, possible_positions) tuples
            
        Returns:
            List of TabNote objects with optimal positions
        """
        n = len(note_positions)
        if n == 0:
            return []
        
        # Initialize DP tables
        # costs[i][j] = minimum cost to reach note i at position j
        costs = [{} for _ in range(n)]
        backptr = [{} for _ in range(n)]
        
        # Initialize first note
        note0, positions0 = note_positions[0]
        for pos in positions0:
            costs[0][pos] = self._position_cost(pos)
            backptr[0][pos] = None
        
        # Forward pass
        for i in range(1, n):
            note_curr, positions_curr = note_positions[i]
            note_prev, positions_prev = note_positions[i-1]
            
            time_gap = note_curr.start_time - note_prev.end_time
            
            for pos_curr in positions_curr:
                min_cost = float('inf')
                best_prev = None
                
                for pos_prev in positions_prev:
                    # Calculate transition cost
                    trans_cost = self._transition_cost(
                        pos_prev, pos_curr, time_gap
                    )
                    total = costs[i-1].get(pos_prev, float('inf')) + trans_cost
                    
                    if total < min_cost:
                        min_cost = total
                        best_prev = pos_prev
                
                # Add position cost
                costs[i][pos_curr] = min_cost + self._position_cost(pos_curr)
                backptr[i][pos_curr] = best_prev
        
        # Backtrack to find optimal path
        # Find best final position
        note_last, positions_last = note_positions[-1]
        best_pos = min(positions_last, key=lambda p: costs[-1].get(p, float('inf')))
        
        # Trace back
        path = [best_pos]
        for i in range(n-1, 0, -1):
            path.append(backptr[i][path[-1]])
        path.reverse()
        
        # Convert to TabNote objects
        tab_notes = []
        for i, ((note, _), (string_idx, fret)) in enumerate(zip(note_positions, path)):
            tab_notes.append(TabNote(
                string=string_idx,
                fret=fret,
                start_time=note.start_time,
                end_time=note.end_time,
                technique="pick",  # Will be updated by technique detection
                pitch=note.pitch
            ))
        
        return tab_notes
    
    def _position_cost(self, pos: Tuple[int, int]) -> float:
        """Calculate cost for a fret position."""
        string_idx, fret = pos
        
        cost = 0.0
        
        # Prefer lower frets (easier to play)
        if fret > 12:
            cost += (fret - 12) * 0.3
        
        # For bass, penalize very low frets on low strings
        if self.instrument == "bass" and string_idx < 2 and fret < 5:
            cost += 2.0
        
        return cost
    
    def _transition_cost(
        self,
        pos_prev: Tuple[int, int],
        pos_curr: Tuple[int, int],
        time_gap: float
    ) -> float:
        """Calculate cost for transitioning between positions."""
        string_prev, fret_prev = pos_prev
        string_curr, fret_curr = pos_curr
        
        cost = 0.0
        
        # Fret distance cost
        fret_dist = abs(fret_curr - fret_prev)
        cost += fret_dist * self.fret_distance_weight
        
        # String change cost
        string_dist = abs(string_curr - string_prev)
        cost += string_dist * self.string_change_weight
        
        # Legato bonus (same string, small time gap)
        if time_gap < 0.2 and string_curr == string_prev and 1 <= fret_dist <= 2:
            cost += self.legato_bonus
        
        # String skip penalty for fast passages
        if time_gap < 0.2 and string_dist > 1:
            cost += self.string_skip_penalty
        
        return cost
    
    def _detect_techniques(self, tab_notes: List[TabNote]) -> List[TabNote]:
        """Detect slides, hammer-ons, and pull-offs."""
        if len(tab_notes) < 2:
            return tab_notes
        
        for i in range(1, len(tab_notes)):
            prev = tab_notes[i-1]
            curr = tab_notes[i]
            
            # Same string, small time gap, small fret distance = slide/hammer/pull
            time_gap = curr.start_time - prev.end_time
            
            if curr.string == prev.string and time_gap < 0.15:
                fret_diff = curr.fret - prev.fret
                
                if 1 <= abs(fret_diff) <= 3:
                    if fret_diff > 0:
                        curr.technique = "slide" if fret_diff > 1 else "hammer"
                    else:
                        curr.technique = "pull"
        
        return tab_notes
    
    def export_ascii(
        self,
        tab_notes: List[TabNote],
        title: str = "Tablature",
        time_resolution: float = 0.25
    ) -> str:
        """
        Export tablature as ASCII text.
        
        Args:
            tab_notes: List of TabNote objects
            title: Title for the tablature
            time_resolution: Time per column in seconds
            
        Returns:
            ASCII tablature string
        """
        if not tab_notes:
            return f"=== {title} ===\n\n(No notes)\n"
        
        # Get string labels
        if self.instrument == "bass":
            if self.num_strings == 5:
                labels = self.BASS_5_STRINGS
            else:
                labels = self.BASS_4_STRINGS
        else:
            labels = self.GUITAR_STRINGS
        
        # Calculate grid size
        max_time = max(n.end_time for n in tab_notes)
        num_cols = int(max_time / time_resolution) + 1
        
        # Initialize grid
        grid = [['---' for _ in range(num_cols)] for _ in range(self.num_strings)]
        
        # Place notes
        for note in tab_notes:
            col = int(note.start_time / time_resolution)
            if col < num_cols:
                fret_str = str(note.fret)
                
                # Add technique marker
                if note.technique == "slide":
                    fret_str += "s"
                elif note.technique == "hammer":
                    fret_str += "h"
                elif note.technique == "pull":
                    fret_str += "p"
                
                # Pad to 3 characters
                fret_str = fret_str.ljust(3, '-')
                grid[note.string][col] = fret_str
        
        # Build output
        lines = [
            f"=== {title} ===",
            "",
            f"Generated by Tab Agent Pro",
            f"Timestamp: {datetime.now().isoformat()}",
            ""
        ]
        
        # Render in chunks of 60 columns
        chunk_size = 60
        for start_col in range(0, num_cols, chunk_size):
            end_col = min(start_col + chunk_size, num_cols)
            
            # Strings displayed high to low
            for string_idx in range(self.num_strings - 1, -1, -1):
                label = labels[string_idx] if string_idx < len(labels) else str(string_idx)
                line = f"{label}|"
                for col in range(start_col, end_col):
                    line += grid[string_idx][col]
                lines.append(line)
            
            lines.append("")  # Blank line between chunks
        
        lines.append("Legend: s=slide, h=hammer-on, p=pull-off")
        
        return "\n".join(lines)
    
    def export_json(self, tab_notes: List[TabNote], title: str = "Tablature") -> str:
        """Export tablature as JSON."""
        data = {
            "title": title,
            "instrument": self.instrument,
            "tuning": self.tuning,
            "num_frets": self.num_frets,
            "timestamp": datetime.now().isoformat(),
            "notes": [
                {
                    "string": n.string,
                    "fret": n.fret,
                    "start_time": n.start_time,
                    "end_time": n.end_time,
                    "technique": n.technique,
                    "pitch": n.pitch
                }
                for n in tab_notes
            ]
        }
        return json.dumps(data, indent=2)
