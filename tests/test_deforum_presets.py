"""
Tests for deforum/presets.py - Style Presets
"""

import pytest
from deforum.presets import (
    STYLE_PRESETS,
    get_preset,
    list_presets,
    get_preset_description,
)


class TestStylePresets:
    """Tests for STYLE_PRESETS dictionary."""

    @pytest.mark.unit
    def test_presets_exist(self):
        """Test that presets dictionary is not empty."""
        assert len(STYLE_PRESETS) > 0

    @pytest.mark.unit
    def test_required_presets(self):
        """Test that required presets exist."""
        required = ["guitar_hero", "concert", "abstract", "acoustic"]
        for preset_name in required:
            assert preset_name in STYLE_PRESETS

    @pytest.mark.unit
    def test_preset_structure(self):
        """Test that each preset has required fields."""
        required_fields = ["name", "description", "prompt_base"]

        for preset_name, preset in STYLE_PRESETS.items():
            for field in required_fields:
                assert field in preset, f"Preset '{preset_name}' missing '{field}'"

    @pytest.mark.unit
    def test_preset_optional_fields(self):
        """Test that optional fields have correct types when present."""
        for preset_name, preset in STYLE_PRESETS.items():
            if "guidance_scale" in preset:
                assert isinstance(preset["guidance_scale"], (int, float))
            if "motion_scale" in preset:
                assert isinstance(preset["motion_scale"], (int, float))
            if "strength_base" in preset:
                assert 0 <= preset["strength_base"] <= 1


class TestGetPreset:
    """Tests for get_preset function."""

    @pytest.mark.unit
    def test_get_preset_exact_match(self):
        """Test getting preset by exact name."""
        preset = get_preset("guitar_hero")
        assert preset is not None
        assert preset["name"] == "Guitar Hero"

    @pytest.mark.unit
    def test_get_preset_case_insensitive(self):
        """Test case-insensitive lookup."""
        preset1 = get_preset("guitar_hero")
        preset2 = get_preset("GUITAR_HERO")
        preset3 = get_preset("Guitar_Hero")

        assert preset1 == preset2 == preset3

    @pytest.mark.unit
    def test_get_preset_with_spaces(self):
        """Test lookup with spaces instead of underscores."""
        preset = get_preset("guitar hero")
        assert preset is not None
        assert preset["name"] == "Guitar Hero"

    @pytest.mark.unit
    def test_get_preset_unknown(self):
        """Test that unknown preset returns guitar_hero default."""
        preset = get_preset("nonexistent_preset")
        guitar_hero = get_preset("guitar_hero")

        assert preset == guitar_hero

    @pytest.mark.unit
    def test_get_preset_all_presets(self):
        """Test getting all presets."""
        for preset_name in STYLE_PRESETS.keys():
            preset = get_preset(preset_name)
            assert preset is not None


class TestListPresets:
    """Tests for list_presets function."""

    @pytest.mark.unit
    def test_list_presets_returns_list(self):
        """Test that list_presets returns a list."""
        presets = list_presets()
        assert isinstance(presets, list)

    @pytest.mark.unit
    def test_list_presets_not_empty(self):
        """Test that preset list is not empty."""
        presets = list_presets()
        assert len(presets) > 0

    @pytest.mark.unit
    def test_list_presets_contains_all(self):
        """Test that list contains all presets."""
        presets = list_presets()
        for key in STYLE_PRESETS.keys():
            assert key in presets

    @pytest.mark.unit
    def test_list_presets_strings(self):
        """Test that all items are strings."""
        presets = list_presets()
        assert all(isinstance(p, str) for p in presets)


class TestGetPresetDescription:
    """Tests for get_preset_description function."""

    @pytest.mark.unit
    def test_get_description_existing(self):
        """Test getting description for existing preset."""
        desc = get_preset_description("guitar_hero")
        assert isinstance(desc, str)
        assert len(desc) > 0

    @pytest.mark.unit
    def test_get_description_unknown(self):
        """Test getting description for unknown preset."""
        # Should return guitar_hero's description
        desc = get_preset_description("nonexistent")
        guitar_hero_desc = get_preset_description("guitar_hero")

        assert desc == guitar_hero_desc

    @pytest.mark.unit
    def test_all_presets_have_descriptions(self):
        """Test that all presets have descriptions."""
        for preset_name in list_presets():
            desc = get_preset_description(preset_name)
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestPresetContent:
    """Tests for specific preset content."""

    @pytest.mark.unit
    def test_guitar_hero_content(self):
        """Test guitar_hero preset content."""
        preset = get_preset("guitar_hero")

        assert "neon" in preset["prompt_base"].lower() or "guitar" in preset["prompt_base"].lower()
        assert preset["motion_scale"] > 1.0  # High energy

    @pytest.mark.unit
    def test_acoustic_content(self):
        """Test acoustic preset content."""
        preset = get_preset("acoustic")

        assert "acoustic" in preset["prompt_base"].lower() or "warm" in preset["prompt_base"].lower()
        assert preset["motion_scale"] < 1.0  # Calm motion

    @pytest.mark.unit
    def test_abstract_content(self):
        """Test abstract preset content."""
        preset = get_preset("abstract")

        assert "abstract" in preset["prompt_base"].lower() or "pattern" in preset["prompt_base"].lower()

    @pytest.mark.unit
    def test_concert_content(self):
        """Test concert preset content."""
        preset = get_preset("concert")

        assert "concert" in preset["prompt_base"].lower() or "stage" in preset["prompt_base"].lower()


class TestPresetNegativePrompts:
    """Tests for negative prompts."""

    @pytest.mark.unit
    def test_negative_prompts_exist(self):
        """Test that negative prompts are defined."""
        for preset_name, preset in STYLE_PRESETS.items():
            if "negative_prompt" in preset:
                assert isinstance(preset["negative_prompt"], str)

    @pytest.mark.unit
    def test_negative_prompts_not_empty(self):
        """Test that negative prompts are not empty strings."""
        for preset_name, preset in STYLE_PRESETS.items():
            if "negative_prompt" in preset:
                assert len(preset["negative_prompt"]) > 0


class TestPresetGuidanceScales:
    """Tests for guidance scale values."""

    @pytest.mark.unit
    def test_guidance_scales_reasonable(self):
        """Test that guidance scales are in reasonable range."""
        for preset_name, preset in STYLE_PRESETS.items():
            if "guidance_scale" in preset:
                gs = preset["guidance_scale"]
                assert 1.0 <= gs <= 20.0, f"Preset '{preset_name}' has unreasonable guidance_scale: {gs}"


class TestPresetStrengthValues:
    """Tests for strength base values."""

    @pytest.mark.unit
    def test_strength_base_values(self):
        """Test that strength values are valid."""
        for preset_name, preset in STYLE_PRESETS.items():
            if "strength_base" in preset:
                strength = preset["strength_base"]
                assert 0.0 <= strength <= 1.0, f"Preset '{preset_name}' has invalid strength: {strength}"

    @pytest.mark.unit
    def test_acoustic_lower_strength(self):
        """Test that acoustic has lower strength (more coherent)."""
        acoustic = get_preset("acoustic")
        abstract = get_preset("abstract")

        if "strength_base" in acoustic and "strength_base" in abstract:
            assert acoustic["strength_base"] <= abstract["strength_base"]
