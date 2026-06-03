"""
Unit tests for the skill router.
"""

import pytest
from core.router import (
    route_skills,
    _normalize_text,
    _extract_keywords,
    get_skill_display_names,
    get_excluded_skills,
)


class TestNormalizeText:
    """Tests for text normalization."""

    def test_converts_to_lowercase(self):
        assert _normalize_text("HELLO World") == "hello world"

    def test_removes_extra_whitespace(self):
        assert _normalize_text("hello    world") == "hello world"

    def test_handles_empty_string(self):
        assert _normalize_text("") == ""

    def test_handles_only_whitespace(self):
        assert _normalize_text("   \t\n  ") == ""


class TestExtractKeywords:
    """Tests for keyword extraction."""

    def test_extracts_basic_keywords(self):
        keywords = _extract_keywords("coffee and tea")
        assert "coffee" in keywords
        assert "tea" in keywords
        assert "and" not in keywords  # stop word

    def test_removes_stop_words(self):
        keywords = _extract_keywords("the quick brown fox jumps over the lazy dog")
        assert "the" not in keywords
        assert "quick" in keywords
        assert "brown" in keywords
        assert "fox" in keywords

    def test_removes_single_characters(self):
        keywords = _extract_keywords("a b c dog")
        assert "a" not in keywords
        assert "b" not in keywords
        assert "c" not in keywords
        assert "dog" in keywords

    def test_handles_numbers(self):
        keywords = _extract_keywords("10 slides about data")
        assert "10" not in keywords  # single digit, in stop words
        assert "data" in keywords

    def test_empty_input(self):
        keywords = _extract_keywords("")
        assert len(keywords) == 0


class TestRouteSkills:
    """Tests for skill routing logic."""

    def test_always_includes_text(self):
        """Text element should always be included."""
        result = route_skills("random words")
        assert "02-text-element.md" in result

    def test_detects_chart_keywords(self):
        """Should include chart skill when chart keywords detected."""
        result = route_skills("Build a deck showing sales growth and revenue trends")
        assert "02-text-element.md" in result
        assert "06-chart-element.md" in result

    def test_detects_table_keywords(self):
        """Should include table skill when table keywords detected."""
        result = route_skills("Create a pricing comparison table")
        assert "02-text-element.md" in result
        assert "07-table-element.md" in result

    def test_detects_image_keywords(self):
        """Should include image skill when image keywords detected."""
        result = route_skills("Travel guide about coffee in Ethiopia")
        assert "02-text-element.md" in result
        assert "04-image-element.md" in result

    def test_detects_icon_keywords(self):
        """Should include icon skill when icon keywords detected."""
        result = route_skills("Key benefits and features checklist")
        assert "02-text-element.md" in result
        assert "05-icon-element.md" in result

    def test_detects_shape_keywords(self):
        """Should include shape skill when workflow/architecture keywords detected."""
        result = route_skills("System architecture and workflow diagram")
        assert "02-text-element.md" in result
        assert "03-shape-element.md" in result

    def test_multiple_keywords_detected(self):
        """Should include multiple skills when multiple keyword types detected."""
        result = route_skills(
            "Sales dashboard with charts, pricing comparison table, and product photos"
        )
        assert "02-text-element.md" in result
        assert "06-chart-element.md" in result
        assert "07-table-element.md" in result
        assert "04-image-element.md" in result

    def test_no_optional_skills(self):
        """Should only include text when no matching keywords found."""
        result = route_skills("Generic presentation about company")
        assert "02-text-element.md" in result
        assert len(result) == 1  # Only text element

    def test_case_insensitive(self):
        """Should work with different cases."""
        result_lower = route_skills("sales metrics")
        result_upper = route_skills("SALES METRICS")
        result_mixed = route_skills("Sales Metrics")
        assert result_lower == result_upper == result_mixed

    def test_real_world_coffee_request(self):
        """Test realistic coffee presentation request."""
        result = route_skills("Build me a 10-slide deck about coffee in Ethiopia")
        assert "02-text-element.md" in result
        assert "04-image-element.md" in result  # travel/coffee keywords

    def test_real_world_sales_request(self):
        """Test realistic sales presentation request."""
        result = route_skills("Create quarterly sales report with growth metrics and competitor comparison")
        assert "02-text-element.md" in result
        assert "06-chart-element.md" in result  # sales, metrics, quarterly
        assert "07-table-element.md" in result  # comparison


class TestGetSkillDisplayNames:
    """Tests for converting filenames to display names."""

    def test_single_skill(self):
        result = get_skill_display_names({"02-text-element.md"})
        assert result == {"text"}

    def test_multiple_skills(self):
        result = get_skill_display_names({
            "02-text-element.md",
            "04-image-element.md",
            "05-icon-element.md"
        })
        assert result == {"text", "image", "icon"}

    def test_ignores_unknown_skills(self):
        result = get_skill_display_names({
            "02-text-element.md",
            "unknown-skill.md"
        })
        assert result == {"text"}


class TestGetExcludedSkills:
    """Tests for determining excluded skills."""

    def test_all_skills_selected(self):
        all_skills = {
            "02-text-element.md",
            "03-shape-element.md",
            "04-image-element.md",
            "05-icon-element.md",
            "06-chart-element.md",
            "07-table-element.md",
        }
        result = get_excluded_skills(all_skills)
        assert len(result) == 0

    def test_some_skills_excluded(self):
        selected = {"02-text-element.md", "04-image-element.md"}
        result = get_excluded_skills(selected)
        assert "03-shape-element.md" in result
        assert "05-icon-element.md" in result
        assert "06-chart-element.md" in result
        assert "07-table-element.md" in result

    def test_only_text_selected(self):
        selected = {"02-text-element.md"}
        result = get_excluded_skills(selected)
        assert len(result) == 5  # 6 total - 1 text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
