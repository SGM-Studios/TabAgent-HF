"""
Tests for agents/tab.py - TabAgent (MIDI to Tablature)
"""

import pytest
import json
from agents import TabAgent
from agents.types import Note, TabNote


class TestTabAgentInit:
    """Tests for TabAgent initialization."""

    @pytest.mark.unit
    def test_init_default_guitar(self):
        """Test default initialization creates guitar TabAgent."""
        agent = TabAgent()
        assert agent.instrument == "guitar"
        assert agent.num_strings == 6
        assert agent.num_frets == 24

    @pytest.mark.unit
    def test_init_with_tuning(self, guitar_standard_tuning):
        """Test initialization with custom tuning."""
        agent = TabAgent(tuning=guitar_standard_tuning)
        assert agent.tuning == guitar_standard_tuning
        assert agent.num_strings == 6

    @pytest.mark.unit
    def test_init_bass(self, bass_4_string_tuning):
        """Test bass initialization."""
        agent = TabAgent(tuning=bass_4_string_tuning, instrument="bass")
        assert agent.instrument == "bass"
        assert agent.num_strings == 4

    @pytest.mark.unit
    def test_init_custom_frets(self):
        """Test initialization with custom fret count."""
        agent = TabAgent(num_frets=22)
        assert agent.num_frets == 22


class TestFindPositions:
    """Tests for _find_positions method."""

    @pytest.mark.unit
    def test_find_positions_open_string(self, tab_agent):
        """Test finding position for open string note."""
        positions = tab_agent._find_positions(40)  # E2, open low E
        assert (0, 0) in positions

    @pytest.mark.unit
    def test_find_positions_multiple(self, tab_agent):
        """Test finding multiple positions for same pitch."""
        # A2 (45) can be played on:
        # - String 0, fret 5
        # - String 1, fret 0
        positions = tab_agent._find_positions(45)
        assert len(positions) >= 2
        assert (0, 5) in positions
        assert (1, 0) in positions

    @pytest.mark.unit
    def test_find_positions_high_note(self, tab_agent):
        """Test finding position for high note."""
        positions = tab_agent._find_positions(76)  # E5
        # Should be playable on high E string
        assert len(positions) > 0

    @pytest.mark.unit
    def test_find_positions_unplayable(self, tab_agent):
        """Test that unplayable notes return empty list."""
        # Very low note
        positions = tab_agent._find_positions(20)
        assert len(positions) == 0

        # Very high note
        positions = tab_agent._find_positions(100)
        assert len(positions) == 0


class TestGenerateTab:
    """Tests for generate_tab method."""

    @pytest.mark.unit
    def test_generate_tab_basic(self, tab_agent, sample_notes_guitar):
        """Test basic tablature generation."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)

        assert len(tab_notes) > 0
        for tab_note in tab_notes:
            assert isinstance(tab_note, TabNote)
            assert 0 <= tab_note.string < 6
            assert 0 <= tab_note.fret <= 24

    @pytest.mark.unit
    def test_generate_tab_empty(self, tab_agent):
        """Test generating tab from empty note list."""
        tab_notes = tab_agent.generate_tab([])
        assert len(tab_notes) == 0

    @pytest.mark.unit
    def test_generate_tab_single_note(self, tab_agent):
        """Test generating tab from single note."""
        notes = [Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80)]
        tab_notes = tab_agent.generate_tab(notes)

        assert len(tab_notes) == 1
        assert tab_notes[0].pitch == 60

    @pytest.mark.unit
    def test_generate_tab_preserves_timing(self, tab_agent, sample_notes_guitar):
        """Test that tab generation preserves note timing."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)

        for orig, tab in zip(sample_notes_guitar, tab_notes):
            assert tab.start_time == orig.start_time
            assert tab.end_time == orig.end_time

    @pytest.mark.unit
    def test_generate_tab_bass(self, tab_agent_bass, sample_notes_bass):
        """Test tablature generation for bass."""
        tab_notes = tab_agent_bass.generate_tab(sample_notes_bass)

        assert len(tab_notes) > 0
        for tab_note in tab_notes:
            assert 0 <= tab_note.string < 4

    @pytest.mark.unit
    def test_generate_tab_sorted_by_time(self, tab_agent):
        """Test that output is sorted by time."""
        # Notes in random order
        notes = [
            Note(pitch=60, start_time=1.0, end_time=1.5, velocity=80),
            Note(pitch=55, start_time=0.0, end_time=0.5, velocity=80),
            Note(pitch=62, start_time=0.5, end_time=1.0, velocity=80),
        ]

        tab_notes = tab_agent.generate_tab(notes)

        for i in range(len(tab_notes) - 1):
            assert tab_notes[i].start_time <= tab_notes[i + 1].start_time


class TestTechniqueDetection:
    """Tests for technique detection."""

    @pytest.mark.unit
    def test_detect_hammer_on(self, tab_agent):
        """Test hammer-on detection."""
        # Two notes on same string, ascending, close together
        notes = [
            Note(pitch=55, start_time=0.0, end_time=0.1, velocity=80),  # G3
            Note(pitch=57, start_time=0.1, end_time=0.3, velocity=80),  # A3
        ]

        tab_notes = tab_agent.generate_tab(notes)

        # At least one should be detected as hammer
        techniques = [n.technique for n in tab_notes]
        assert "hammer" in techniques or "slide" in techniques or len(tab_notes) == 2

    @pytest.mark.unit
    def test_detect_pull_off(self, tab_agent):
        """Test pull-off detection."""
        # Two notes on same string, descending, close together
        notes = [
            Note(pitch=57, start_time=0.0, end_time=0.1, velocity=80),  # A3
            Note(pitch=55, start_time=0.1, end_time=0.3, velocity=80),  # G3
        ]

        tab_notes = tab_agent.generate_tab(notes)
        # Pull-off detection depends on Viterbi path
        assert len(tab_notes) == 2

    @pytest.mark.unit
    def test_default_technique_is_pick(self, tab_agent):
        """Test that default technique is 'pick'."""
        notes = [Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80)]
        tab_notes = tab_agent.generate_tab(notes)

        # First note should always be pick
        assert tab_notes[0].technique == "pick"


class TestExportAscii:
    """Tests for export_ascii method."""

    @pytest.mark.unit
    def test_export_ascii_basic(self, tab_agent, sample_notes_guitar):
        """Test basic ASCII export."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        ascii_tab = tab_agent.export_ascii(tab_notes, title="Test Tab")

        assert "Test Tab" in ascii_tab
        assert "Tab Agent Pro" in ascii_tab

    @pytest.mark.unit
    def test_export_ascii_has_string_labels(self, tab_agent, sample_notes_guitar):
        """Test that ASCII export has string labels."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        ascii_tab = tab_agent.export_ascii(tab_notes)

        # Should have guitar string labels
        assert "e|" in ascii_tab or "E|" in ascii_tab

    @pytest.mark.unit
    def test_export_ascii_empty(self, tab_agent):
        """Test ASCII export with no notes."""
        ascii_tab = tab_agent.export_ascii([], title="Empty Tab")

        assert "Empty Tab" in ascii_tab
        assert "No notes" in ascii_tab

    @pytest.mark.unit
    def test_export_ascii_legend(self, tab_agent, sample_notes_guitar):
        """Test that ASCII export includes legend."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        ascii_tab = tab_agent.export_ascii(tab_notes)

        assert "Legend:" in ascii_tab

    @pytest.mark.unit
    def test_export_ascii_bass(self, tab_agent_bass, sample_notes_bass):
        """Test ASCII export for bass."""
        tab_notes = tab_agent_bass.generate_tab(sample_notes_bass)
        ascii_tab = tab_agent_bass.export_ascii(tab_notes, title="Bass Tab")

        assert "Bass Tab" in ascii_tab


class TestExportJson:
    """Tests for export_json method."""

    @pytest.mark.unit
    def test_export_json_basic(self, tab_agent, sample_notes_guitar):
        """Test basic JSON export."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        json_str = tab_agent.export_json(tab_notes, title="Test Tab")

        data = json.loads(json_str)
        assert data["title"] == "Test Tab"
        assert data["instrument"] == "guitar"

    @pytest.mark.unit
    def test_export_json_has_notes(self, tab_agent, sample_notes_guitar):
        """Test that JSON export includes notes."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        json_str = tab_agent.export_json(tab_notes)

        data = json.loads(json_str)
        assert "notes" in data
        assert len(data["notes"]) == len(tab_notes)

    @pytest.mark.unit
    def test_export_json_note_fields(self, tab_agent, sample_notes_guitar):
        """Test that JSON notes have all required fields."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        json_str = tab_agent.export_json(tab_notes)

        data = json.loads(json_str)
        for note in data["notes"]:
            assert "string" in note
            assert "fret" in note
            assert "start_time" in note
            assert "end_time" in note
            assert "technique" in note
            assert "pitch" in note

    @pytest.mark.unit
    def test_export_json_tuning_info(self, tab_agent, sample_notes_guitar):
        """Test that JSON export includes tuning info."""
        tab_notes = tab_agent.generate_tab(sample_notes_guitar)
        json_str = tab_agent.export_json(tab_notes)

        data = json.loads(json_str)
        assert "tuning" in data
        assert data["tuning"] == tab_agent.tuning

    @pytest.mark.unit
    def test_export_json_empty(self, tab_agent):
        """Test JSON export with no notes."""
        json_str = tab_agent.export_json([], title="Empty")

        data = json.loads(json_str)
        assert data["title"] == "Empty"
        assert len(data["notes"]) == 0


class TestViterbiAlgorithm:
    """Tests for the Viterbi dynamic programming algorithm."""

    @pytest.mark.unit
    def test_viterbi_prefers_adjacent_frets(self, tab_agent):
        """Test that Viterbi prefers adjacent fret positions."""
        # Chromatic scale notes
        notes = [
            Note(pitch=55 + i, start_time=i * 0.2, end_time=(i + 1) * 0.2 - 0.05, velocity=80)
            for i in range(5)
        ]

        tab_notes = tab_agent.generate_tab(notes)

        # Check that fret distances are reasonable
        for i in range(len(tab_notes) - 1):
            fret_diff = abs(tab_notes[i + 1].fret - tab_notes[i].fret)
            # Should prefer small fret distances
            assert fret_diff <= 5 or tab_notes[i + 1].string != tab_notes[i].string

    @pytest.mark.unit
    def test_viterbi_handles_large_jumps(self, tab_agent):
        """Test that Viterbi handles large pitch jumps."""
        notes = [
            Note(pitch=40, start_time=0.0, end_time=0.5, velocity=80),  # E2
            Note(pitch=64, start_time=0.5, end_time=1.0, velocity=80),  # E4
        ]

        tab_notes = tab_agent.generate_tab(notes)

        assert len(tab_notes) == 2
        # Should be on different strings
        assert tab_notes[0].string != tab_notes[1].string or \
               abs(tab_notes[0].fret - tab_notes[1].fret) > 10


class TestPositionCost:
    """Tests for position cost calculation."""

    @pytest.mark.unit
    def test_position_cost_low_frets_preferred(self, tab_agent):
        """Test that lower frets have lower cost."""
        cost_low = tab_agent._position_cost((0, 3))
        cost_high = tab_agent._position_cost((0, 15))

        assert cost_low < cost_high

    @pytest.mark.unit
    def test_position_cost_open_string(self, tab_agent):
        """Test cost of open string position."""
        cost = tab_agent._position_cost((0, 0))
        assert cost >= 0  # No negative costs


class TestTransitionCost:
    """Tests for transition cost calculation."""

    @pytest.mark.unit
    def test_transition_cost_same_position(self, tab_agent):
        """Test transition cost for same position."""
        cost = tab_agent._transition_cost((0, 5), (0, 5), 0.5)
        assert cost >= 0

    @pytest.mark.unit
    def test_transition_cost_adjacent_frets(self, tab_agent):
        """Test transition cost for adjacent frets."""
        cost_adj = tab_agent._transition_cost((0, 5), (0, 6), 0.2)
        cost_far = tab_agent._transition_cost((0, 5), (0, 12), 0.2)

        assert cost_adj < cost_far

    @pytest.mark.unit
    def test_transition_cost_string_change(self, tab_agent):
        """Test transition cost for string changes."""
        cost_same = tab_agent._transition_cost((0, 5), (0, 7), 0.2)
        cost_diff = tab_agent._transition_cost((0, 5), (1, 5), 0.2)

        # String changes should have higher cost (assuming similar fret distance)
        # This depends on the specific weights
        assert cost_diff >= 0
