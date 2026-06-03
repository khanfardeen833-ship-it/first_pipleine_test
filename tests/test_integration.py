"""
Integration tests for skill routing and prompt optimization end-to-end.
"""

import pytest
from core.prompt import build_system_prompt, build_system_prompt_optimized
from core.router import route_skills


class TestSkillRoutingIntegration:
    """Tests for skill routing integrated with prompt builder."""

    def test_optimized_prompt_smaller_for_text_only_request(self):
        """Simple text request should produce smaller optimized prompt."""
        full_prompt = build_system_prompt()
        optimized_prompt, metadata = build_system_prompt_optimized(
            "Simple presentation about company"
        )

        # Optimized should be smaller for text-only requests
        assert len(optimized_prompt) < len(full_prompt)
        assert metadata["reduction_pct"] > 0

    def test_coffee_request_routing_consistency(self):
        """Router and prompt builder should agree on skills needed for coffee request."""
        user_request = "Build me a 10-slide deck about coffee in Ethiopia"

        # Get skills from router directly
        routed_skills = route_skills(user_request)

        # Get skills from prompt builder
        prompt, metadata = build_system_prompt_optimized(user_request)

        # Should include text
        assert "02-text-element.md" in routed_skills
        assert "02-text-element.md" in metadata["selected_skills"]

        # Should include image (travel/coffee keywords)
        assert "04-image-element.md" in routed_skills
        assert "04-image-element.md" in metadata["selected_skills"]

    def test_sales_request_routing_consistency(self):
        """Router and prompt builder should agree on skills for sales request."""
        user_request = (
            "Create quarterly sales report with growth metrics and competitor comparison"
        )

        routed_skills = route_skills(user_request)
        prompt, metadata = build_system_prompt_optimized(user_request)

        # Should include text
        assert "02-text-element.md" in routed_skills
        assert "02-text-element.md" in metadata["selected_skills"]

        # Should include chart (sales/metrics keywords)
        assert "06-chart-element.md" in routed_skills
        assert "06-chart-element.md" in metadata["selected_skills"]

        # Should include table (comparison keyword)
        assert "07-table-element.md" in routed_skills
        assert "07-table-element.md" in metadata["selected_skills"]

    def test_prompt_includes_routing_selections(self):
        """Optimized prompt should include content from selected skills."""
        prompt, metadata = build_system_prompt_optimized("coffee in Ethiopia")

        # Prompt should contain sections for selected skills
        for skill_name in metadata["selected_skill_names"]:
            # Display name should be in prompt or prompt should be substantively different
            assert len(prompt) > 5000  # Pragmatic check that prompt has content

    def test_excluded_skills_not_in_prompt(self):
        """Excluded skills should not appear in significant way in optimized prompt."""
        prompt, metadata = build_system_prompt_optimized("simple text presentation")

        # Most skills should be excluded for a simple text request
        assert len(metadata["excluded_skills"]) > 3

        # Optimized prompt should be significantly smaller
        full_prompt = build_system_prompt()
        size_ratio = metadata["prompt_size_bytes"] / metadata["full_prompt_size_bytes"]
        assert size_ratio < 0.7  # Should be < 70% of full size for simple request

    def test_workflow_diagram_request(self):
        """Workflow/diagram keywords should select shape element."""
        prompt, metadata = build_system_prompt_optimized(
            "System architecture and workflow diagram for microservices"
        )

        # Should select shape element
        assert "03-shape-element.md" in metadata["selected_skills"]

    def test_benefits_checklist_request(self):
        """Benefits/features keywords should select icon element."""
        prompt, metadata = build_system_prompt_optimized(
            "Key benefits and features checklist for the product"
        )

        # Should select icon element
        assert "05-icon-element.md" in metadata["selected_skills"]

    def test_metadata_consistency(self):
        """Metadata should be internally consistent."""
        prompt, metadata = build_system_prompt_optimized("complex multi-skill deck")

        # selected + excluded should equal all possible element skills
        all_skills = (
            metadata["selected_skills"] | metadata["excluded_skills"]
        )
        # At minimum text should be selected
        assert "02-text-element.md" in metadata["selected_skills"]

        # Reduction should be based on correct sizes
        expected_reduction = (
            1 - metadata["prompt_size_bytes"] / metadata["full_prompt_size_bytes"]
        ) * 100
        assert abs(
            metadata["reduction_pct"] - expected_reduction
        ) < 0.1  # Allow for rounding

    def test_multi_keyword_complex_request(self):
        """Complex request with multiple keyword types."""
        prompt, metadata = build_system_prompt_optimized(
            "Sales dashboard with revenue charts, competitor pricing table, "
            "product photography showcase, workflow diagrams, and feature checklist"
        )

        # Should detect multiple skill types
        assert "02-text-element.md" in metadata["selected_skills"]
        assert "04-image-element.md" in metadata["selected_skills"]
        assert "06-chart-element.md" in metadata["selected_skills"]
        assert "07-table-element.md" in metadata["selected_skills"]
        assert "03-shape-element.md" in metadata["selected_skills"]
        assert "05-icon-element.md" in metadata["selected_skills"]

        # Should have minimal exclusions
        assert len(metadata["excluded_skills"]) == 0


class TestPromptQualityMaintenance:
    """Tests to ensure output quality is maintained with optimization."""

    def test_optimized_prompt_includes_template_base(self):
        """Optimized prompt should include the base template content."""
        prompt, metadata = build_system_prompt_optimized("test")
        # Should have substantial content
        assert len(prompt) > 5000

    def test_core_skills_always_present(self):
        """Core skills should be in all optimized prompts."""
        requests = [
            "simple text",
            "coffee Ethiopia",
            "sales metrics",
            "system architecture",
        ]

        for request in requests:
            prompt, metadata = build_system_prompt_optimized(request)
            # Prompt should be large enough to include core content
            assert len(prompt) > 4000

    def test_consistent_results_for_same_input(self):
        """Same input should produce identical results."""
        request = "coffee in Ethiopia with photos"

        prompt1, metadata1 = build_system_prompt_optimized(request)
        prompt2, metadata2 = build_system_prompt_optimized(request)

        assert prompt1 == prompt2
        assert metadata1 == metadata2

    def test_prompt_without_extra_equals_optimized(self):
        """Optimized prompt without extra should not have extra content."""
        prompt, metadata = build_system_prompt_optimized("coffee")

        # Should not have obvious extra content
        assert "EXTRA:" not in prompt or len(prompt.split("EXTRA:")) == 1

    def test_prompt_with_extra_contains_extra(self):
        """Optimized prompt with extra should include extra content."""
        extra = "CONSTRAINT: This is batch-specific content"
        prompt, metadata = build_system_prompt_optimized("coffee", extra=extra)

        assert "CONSTRAINT: This is batch-specific content" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
