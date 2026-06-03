"""
Unit tests for the Haiku planning phase.
Tests validate plan structure, slide count, skill routing, and metadata.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

from core.planner import plan_presentation


async def async_gen_factory(message):
    """Factory function to create async generator that yields a single message."""
    yield message


@pytest.mark.asyncio
async def test_plan_structure_valid_json():
    """Test that plan_presentation returns valid JSON with required structure."""
    # Mock the query function to return a valid plan
    valid_plan = {
        "skill_routing": {
            "selected_skills": ["text", "image"],
            "excluded_skills": ["chart", "table", "shape", "icon"]
        },
        "slides": [
            {
                "slide_number": 1,
                "title": "Coffee: A Global Perspective",
                "content_outline": "Introduction to coffee cultivation",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": "Coffee plantation landscape"
            },
            {
                "slide_number": 2,
                "title": "Origins and History",
                "content_outline": "Historical context",
                "layout_hint": "Two column",
                "data_elements": [],
                "image_prompt": "Historical coffee trade routes"
            }
        ],
        "deck_metadata": {
            "title": "The Complete Guide to Coffee",
            "theme": "Professional",
            "style_notes": "Photography-focused"
        }
    }

    # Create mock message objects
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(valid_plan))]

    with patch('core.planner.query') as mock_query:
        # Make query return async generator
        mock_query.side_effect = lambda *args, **kwargs: async_gen_factory(mock_message)

        with patch('core.planner.render_message'):
            from core.tracker import Tracker
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Build me a 2-slide coffee presentation", 2, tracker=tracker)

            # Verify tracker recorded planning phase
            assert tracker.phase is None  # Phase ended
            assert "planning" in tracker.phases
            assert tracker.phases["planning"]["duration_seconds"] > 0
            assert tracker.phases["planning"]["model"] == "claude-haiku-4-5"

    # Assert structure
    assert "skill_routing" in plan
    assert "slides" in plan
    assert "deck_metadata" in plan

    # Assert skill routing
    assert "selected_skills" in plan["skill_routing"]
    assert "excluded_skills" in plan["skill_routing"]

    # Assert deck metadata
    assert "title" in plan["deck_metadata"]
    assert "theme" in plan["deck_metadata"]


@pytest.mark.asyncio
async def test_plan_includes_all_slides():
    """Test that plan includes the correct number of slides."""
    total_slides = 5
    slides = [
        {
            "slide_number": i,
            "title": f"Slide {i}",
            "content_outline": f"Content for slide {i}",
            "layout_hint": "Default",
            "data_elements": [],
            "image_prompt": f"Image for slide {i}"
        }
        for i in range(1, total_slides + 1)
    ]

    valid_plan = {
        "skill_routing": {
            "selected_skills": ["text"],
            "excluded_skills": ["chart", "table", "shape", "icon", "image"]
        },
        "slides": slides,
        "deck_metadata": {
            "title": "Test Presentation",
            "theme": "Minimal",
            "style_notes": "Text-focused"
        }
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(valid_plan))]

    with patch('core.planner.query') as mock_query:
        mock_query.side_effect = lambda *args, **kwargs: async_gen_factory(mock_message)

        with patch('core.planner.render_message'):
            from core.tracker import Tracker
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Build me a test presentation", total_slides, tracker=tracker)

            # Verify tracker recorded phase
            assert "planning" in tracker.phases
            assert tracker.phases["planning"]["duration_seconds"] > 0

    # Assert correct number of slides
    assert len(plan["slides"]) == total_slides

    # Assert all slide numbers are present
    slide_numbers = {s["slide_number"] for s in plan["slides"]}
    assert slide_numbers == set(range(1, total_slides + 1))


@pytest.mark.asyncio
async def test_skill_routing_in_plan():
    """Test that skill routing is correctly included in the plan."""
    valid_plan = {
        "skill_routing": {
            "selected_skills": ["text", "chart", "table"],
            "excluded_skills": ["image", "icon", "shape"]
        },
        "slides": [
            {
                "slide_number": 1,
                "title": "Sales Report",
                "content_outline": "Q1 sales metrics",
                "layout_hint": "Title + chart",
                "data_elements": ["chart"],
                "image_prompt": ""
            }
        ],
        "deck_metadata": {
            "title": "Sales Analysis",
            "theme": "Professional",
            "style_notes": "Data visualization"
        }
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(valid_plan))]

    with patch('core.planner.query') as mock_query:
        mock_query.side_effect = lambda *args, **kwargs: async_gen_factory(mock_message)

        with patch('core.planner.render_message'):
            from core.tracker import Tracker
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Build me a sales presentation", 1, tracker=tracker)

            # Verify tracker recorded phase
            assert "planning" in tracker.phases

    # Assert skill routing is present
    assert "chart" in plan["skill_routing"]["selected_skills"]
    assert "table" in plan["skill_routing"]["selected_skills"]
    assert "image" in plan["skill_routing"]["excluded_skills"]


@pytest.mark.asyncio
async def test_plan_metadata_complete():
    """Test that deck metadata includes all required fields."""
    valid_plan = {
        "skill_routing": {
            "selected_skills": ["text"],
            "excluded_skills": []
        },
        "slides": [
            {
                "slide_number": 1,
                "title": "Title",
                "content_outline": "Content",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": ""
            }
        ],
        "deck_metadata": {
            "title": "My Presentation",
            "theme": "Modern",
            "style_notes": "Clean and minimal design"
        }
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(valid_plan))]

    with patch('core.planner.query') as mock_query:
        mock_query.side_effect = lambda *args, **kwargs: async_gen_factory(mock_message)

        with patch('core.planner.render_message'):
            from core.tracker import Tracker
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Build me a presentation", 1, tracker=tracker)

            # Verify tracker recorded phase
            assert "planning" in tracker.phases
            assert tracker.phases["planning"]["model"] == "claude-haiku-4-5"

    # Assert metadata fields
    metadata = plan["deck_metadata"]
    assert "title" in metadata
    assert "theme" in metadata
    assert "style_notes" in metadata
    assert len(metadata["title"]) > 0
    assert len(metadata["theme"]) > 0


@pytest.mark.asyncio
async def test_plan_slide_fields_required():
    """Test that each slide has all required fields."""
    valid_plan = {
        "skill_routing": {
            "selected_skills": ["text"],
            "excluded_skills": []
        },
        "slides": [
            {
                "slide_number": 1,
                "title": "Slide Title",
                "content_outline": "Slide content",
                "layout_hint": "Title + content",
                "data_elements": [],
                "image_prompt": "Image description"
            }
        ],
        "deck_metadata": {
            "title": "Presentation",
            "theme": "Theme",
            "style_notes": "Notes"
        }
    }

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps(valid_plan))]

    with patch('core.planner.query') as mock_query:
        mock_query.side_effect = lambda *args, **kwargs: async_gen_factory(mock_message)

        with patch('core.planner.render_message'):
            from core.tracker import Tracker
            tracker = Tracker("claude-haiku-4-5")
            plan = await plan_presentation("Build presentation", 1, tracker=tracker)

            # Verify tracker recorded phase with proper cleanup
            assert tracker.phase is None
            assert "planning" in tracker.phases

    # Assert each slide has required fields
    required_fields = {"slide_number", "title", "content_outline", "layout_hint", "data_elements", "image_prompt"}
    for slide in plan["slides"]:
        assert all(field in slide for field in required_fields), \
            f"Slide missing required fields: {required_fields - set(slide.keys())}"
