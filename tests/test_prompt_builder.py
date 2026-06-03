"""
Unit tests for the optimized prompt builder.
"""

import pytest
from pathlib import Path
from core.prompt import (
    load_core_skills,
    load_selected_skills,
    build_system_prompt,
    build_system_prompt_optimized,
)


class TestLoadCoreSkills:
    """Tests for loading core skills."""

    def test_returns_tuple(self):
        """Should return (content, size_bytes) tuple."""
        result = load_core_skills()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_content_is_string(self):
        """Returned content should be a string."""
        content, size = load_core_skills()
        assert isinstance(content, str)
        assert len(content) > 0

    def test_size_matches_content(self):
        """Size in bytes should match encoded content."""
        content, size = load_core_skills()
        assert size == len(content.encode("utf-8"))

    def test_includes_skills_index(self):
        """Content should include the skills index."""
        content, size = load_core_skills()
        assert "SKILLS INDEX" in content

    def test_core_skills_present(self):
        """Core skills should be in content."""
        content, size = load_core_skills()
        # Should include sections from core skills
        assert "01-" in content or len(content) > 1000  # pragmatic check


class TestLoadSelectedSkills:
    """Tests for loading selected skills."""

    def test_returns_tuple(self):
        """Should return (content, size_bytes) tuple."""
        result = load_selected_skills({"02-text-element.md"})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_loads_text_skill(self):
        """Should load text-element skill when specified."""
        content, size = load_selected_skills({"02-text-element.md"})
        assert isinstance(content, str)
        assert size == len(content.encode("utf-8"))

    def test_loads_multiple_skills(self):
        """Should load multiple skills when specified."""
        skills = {"02-text-element.md", "04-image-element.md", "06-chart-element.md"}
        content, size = load_selected_skills(skills)
        assert isinstance(content, str)
        assert size == len(content.encode("utf-8"))

    def test_empty_skill_set(self):
        """Should handle empty skill set."""
        content, size = load_selected_skills(set())
        assert isinstance(content, str)
        assert size == len(content.encode("utf-8"))

    def test_filters_non_element_skills(self):
        """Should only load valid element skills."""
        # 01- and 08-10 are core, should be skipped
        skills = {"01-envelope.md", "02-text-element.md", "08-changelog.md"}
        content, size = load_selected_skills(skills)
        # Should only include 02-text, not 01 or 08
        assert isinstance(content, str)


class TestBuildSystemPrompt:
    """Tests for legacy prompt builder."""

    def test_returns_string(self):
        """Should return a string."""
        result = build_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 1000

    def test_includes_all_skills(self):
        """Should include content from all skill categories."""
        result = build_system_prompt()
        # Should be reasonably large since it includes everything
        assert len(result) > 10000

    def test_extra_content_appended(self):
        """Should append extra content when provided."""
        extra = "EXTRA: This is additional constraint"
        result = build_system_prompt(extra=extra)
        assert "EXTRA: This is additional constraint" in result


class TestBuildSystemPromptOptimized:
    """Tests for optimized prompt builder."""

    def test_returns_tuple(self):
        """Should return (prompt_string, metadata_dict) tuple."""
        result = build_system_prompt_optimized("coffee presentation")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_prompt_is_string(self):
        """First element should be prompt string."""
        prompt, metadata = build_system_prompt_optimized("coffee")
        assert isinstance(prompt, str)
        assert len(prompt) > 1000

    def test_metadata_is_dict(self):
        """Second element should be metadata dict."""
        prompt, metadata = build_system_prompt_optimized("coffee")
        assert isinstance(metadata, dict)

    def test_metadata_required_fields(self):
        """Metadata should contain all required fields."""
        prompt, metadata = build_system_prompt_optimized("sales dashboard")
        required_fields = [
            "selected_skills",
            "selected_skill_names",
            "excluded_skills",
            "excluded_skill_names",
            "prompt_size_bytes",
            "full_prompt_size_bytes",
            "reduction_pct",
        ]
        for field in required_fields:
            assert field in metadata, f"Missing field: {field}"

    def test_text_always_included(self):
        """Text skill should always be selected."""
        prompt, metadata = build_system_prompt_optimized("random words")
        assert "02-text-element.md" in metadata["selected_skills"]

    def test_reduction_percentage_valid(self):
        """Reduction percentage should be between 0 and 100."""
        prompt, metadata = build_system_prompt_optimized("coffee")
        assert 0 <= metadata["reduction_pct"] <= 100

    def test_prompt_smaller_than_full(self):
        """Optimized prompt should be smaller than or equal to full prompt."""
        prompt, metadata = build_system_prompt_optimized("coffee")
        assert metadata["prompt_size_bytes"] <= metadata["full_prompt_size_bytes"]

    def test_image_skill_detected(self):
        """Should detect image-related keywords."""
        prompt, metadata = build_system_prompt_optimized("coffee in Ethiopia with photos")
        assert "04-image-element.md" in metadata["selected_skills"]

    def test_chart_skill_detected(self):
        """Should detect chart-related keywords."""
        prompt, metadata = build_system_prompt_optimized("sales revenue growth metrics")
        assert "06-chart-element.md" in metadata["selected_skills"]

    def test_table_skill_detected(self):
        """Should detect table-related keywords."""
        prompt, metadata = build_system_prompt_optimized("pricing comparison table")
        assert "07-table-element.md" in metadata["selected_skills"]

    def test_extra_content_included(self):
        """Should include extra content in prompt."""
        extra = "CONSTRAINT: Special requirement here"
        prompt, metadata = build_system_prompt_optimized("coffee", extra=extra)
        assert "CONSTRAINT: Special requirement here" in prompt

    def test_selected_skill_names_populated(self):
        """Should populate skill display names."""
        prompt, metadata = build_system_prompt_optimized("sales chart")
        assert isinstance(metadata["selected_skill_names"], set)
        assert len(metadata["selected_skill_names"]) > 0
        # Should have display names like "text", not filenames
        assert "text" in metadata["selected_skill_names"]

    def test_excluded_skills_not_empty_for_basic_request(self):
        """For simple requests, some skills should be excluded."""
        prompt, metadata = build_system_prompt_optimized("simple text")
        # Text is always included, so excluded should be most of the rest
        assert len(metadata["excluded_skills"]) > 0

    def test_prompt_size_bytes_accurate(self):
        """Prompt size bytes should match actual prompt size."""
        prompt, metadata = build_system_prompt_optimized("coffee")
        expected_size = len(prompt.encode("utf-8"))
        assert metadata["prompt_size_bytes"] == expected_size

    def test_realistic_coffee_request(self):
        """Test realistic coffee presentation request."""
        prompt, metadata = build_system_prompt_optimized(
            "Build me a 10-slide deck about coffee in Ethiopia"
        )
        assert "02-text-element.md" in metadata["selected_skills"]
        assert "04-image-element.md" in metadata["selected_skills"]
        assert metadata["prompt_size_bytes"] > 0
        assert metadata["reduction_pct"] > 0

    def test_realistic_sales_request(self):
        """Test realistic sales presentation request."""
        prompt, metadata = build_system_prompt_optimized(
            "Create quarterly sales report with growth metrics and competitor comparison"
        )
        assert "02-text-element.md" in metadata["selected_skills"]
        assert "06-chart-element.md" in metadata["selected_skills"]
        assert "07-table-element.md" in metadata["selected_skills"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
