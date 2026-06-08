"""Flexible Bildory JSON builder used by presentation-generation agents."""

from __future__ import annotations

import json
import time
from pathlib import Path


TEXT_DEFAULTS = {
    "title": (60, 700, 1.05),
    "subtitle": (40, 600, 1.35),
    "heading": (32, 600, 1.30),
    "subheading": (26, 600, 1.30),
    "paragraph": (22, 700, 1.50),
    "caption": (18, 600, 1.30),
}

CONTENT_ARRAYS = (
    "imageElements",
    "shapeElements",
    "chartElements",
    "tableElements",
    "iconElements",
    "embedElements",
    "smartDiagramElements",
    "groupElements",
)


def _merge(base: dict, overrides: dict | None) -> dict:
    if overrides:
        base.update(overrides)
    return base


class Deck:
    """Build a valid Bildory deck while leaving all visual choices to the caller."""

    def __init__(
        self,
        title: str,
        *,
        description: str = "",
        id_offset: int = 0,
        deck_id: str | None = None,
        timestamp: int | None = None,
    ):
        self.title = title
        self.description = description
        self.now = timestamp or int(time.time() * 1000)
        self.deck_id = deck_id or f"deck-{self.now}"
        self._counter = id_offset
        self._slides: list[Slide] = []
        self._content_arrays = {key: [] for key in CONTENT_ARRAYS}
        self._changelog_slides: dict[str, dict] = {}

    def _next_element(self, prefix: str) -> tuple[str, int]:
        self._counter += 1
        return f"{prefix}-{self._counter}", self._counter

    def add_slide(
        self,
        *,
        slide_id: str | None = None,
        background: str = "#ffffff",
        layout_id: str = "blank-canvas",
    ) -> "Slide":
        slide_id = slide_id or f"slide-{len(self._slides) + 1}"
        if slide_id in self._changelog_slides:
            raise ValueError(f"Duplicate slide ID: {slide_id}")
        slide = Slide(self, slide_id, len(self._slides), background, layout_id)
        self._slides.append(slide)
        self._changelog_slides[slide_id] = {"elements": {}}
        return slide

    def _register(
        self,
        slide: "Slide",
        element_id: str,
        content_record: dict,
        changelog_record: dict,
        content_array: str | None,
    ) -> str:
        if content_array is None:
            slide._text_elements.append(content_record)
        else:
            self._content_arrays[content_array].append(content_record)
        self._changelog_slides[slide.id]["elements"][element_id] = changelog_record
        return element_id

    def to_dict(self) -> dict:
        content = {
            "slides": [slide._content_record() for slide in self._slides],
            **self._content_arrays,
        }
        element_count = sum(len(slide._text_elements) for slide in self._slides)
        element_count += sum(len(content[key]) for key in CONTENT_ARRAYS)

        return {
            "exportedAt": self.now,
            "presentation": {
                "_id": self.deck_id,
                "title": self.title,
                "description": self.description,
                "thumbnailUrl": None,
                "isPublic": False,
                "slideCount": len(self._slides),
                "elementCount": element_count,
                "createdAt": "2026-01-01T00:00:00.000Z",
                "updatedAt": "2026-01-01T00:00:00.000Z",
                "s3Key": None,
                "s3Url": None,
            },
            "files": {
                "content": content,
                "baseLayout": {
                    "version": "v1",
                    "slides": [slide._base_layout_record() for slide in self._slides],
                    "imageElements": [],
                    "shapeElements": [],
                    "chartElements": [],
                    "iconElements": [],
                    "embedElements": [],
                },
                "changelog": {"version": "2.0", "slides": self._changelog_slides},
            },
        }

    def save(self, path: str | Path = "deck.json") -> Path:
        output = Path(path)
        output.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output


class Slide:
    def __init__(self, deck: Deck, slide_id: str, order: int, background: str, layout_id: str):
        self.deck = deck
        self.id = slide_id
        self.order = order
        self.background = background
        self.layout_id = layout_id
        self._text_elements: list[dict] = []

    def _content_record(self) -> dict:
        return {
            "id": self.id,
            "order": self.order,
            "layoutId": self.layout_id,
            "backgroundColor": self.background,
            "textElements": self._text_elements,
        }

    def _base_layout_record(self) -> dict:
        return {
            "id": self.id,
            "layoutId": self.layout_id,
            "imageElements": [],
            "shapeElements": [],
            "chartElements": [],
            "iconElements": [],
            "embedElements": [],
        }

    def add_text(
        self,
        text: str,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        type: str = "paragraph",
        color: str = "#1c1917",
        font_size: int | None = None,
        font_weight: int | None = None,
        line_height: float | None = None,
        font_family: str = "Space Grotesk",
        text_align: str = "left",
        rotation: int = 0,
        style: dict | None = None,
        animation: dict | None = None,
        changelog: dict | None = None,
    ) -> str:
        if type not in TEXT_DEFAULTS:
            raise ValueError(f"Unsupported text type: {type}")
        default_size, default_weight, default_line_height = TEXT_DEFAULTS[type]
        element_id, z_index = self.deck._next_element("text")

        text_style = {
            "fontSize": font_size or default_size,
            "fontFamily": font_family,
            "color": color,
            "textAlign": text_align,
            "lineHeight": line_height or default_line_height,
            "letterSpacing": 0,
            "fontWeight": font_weight or default_weight,
            "fontStyle": "normal",
            "textDecoration": "none",
            "textTransform": "none",
            "isCode": False,
            "listStyle": "none",
            "link": "",
            "backgroundColor": "transparent",
            "background": "none",
            "WebkitBackgroundClip": "unset",
            "WebkitTextFillColor": "unset",
            "backgroundClip": "unset",
            "listLevel": 1,
            "paragraphSpacingBefore": 0,
            "paragraphSpacingAfter": 0,
            "textOutlineColor": "#000000",
            "textOutlineWidth": 0,
            "textTransformEffect": "none",
            "textTransformRadius": 220,
            "textVerticalAlign": "baseline",
            "curveEnabled": False,
            "curveValue": 26,
            "shadowType": "none",
            "shadowOffset": 22,
            "shadowDirection": -45,
            "shadowBlur": 0,
            "shadowTransparency": 40,
            "shadowColor": "#000000",
        }
        _merge(text_style, style)
        animation_block = {
            "enter": "none",
            "exit": "fade",
            "duration": 550,
            "delay": 0,
            "trigger": "both",
            "typewriterMode": "character",
        }
        _merge(animation_block, animation)
        content = {
            "id": element_id,
            "content": text,
            "type": type,
            "originalType": type,
            "groupId": None,
            "formattedContent": text,
        }
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "width": width,
            "height": height,
            "rotation": rotation,
            "zIndex": z_index,
            "style": text_style,
            "formattedContent": text,
            "animation": animation_block,
            "enterAnimation": animation_block["enter"],
            "exitAnimation": animation_block["exit"],
            "animationEffect": animation_block["enter"],
            "animationDurationMs": animation_block["duration"],
            "animationDelayMs": animation_block["delay"],
            "animationTrigger": animation_block["trigger"],
            "animationTypewriterMode": animation_block["typewriterMode"],
            "updatedAt": self.deck.now,
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content, change, None)

    def add_title(self, text: str, **kwargs) -> str:
        return self.add_text(text, type="title", **kwargs)

    def add_subtitle(self, text: str, **kwargs) -> str:
        return self.add_text(text, type="subtitle", **kwargs)

    def add_shape(
        self,
        shape_type: str,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        fill: str = "#c67c3a",
        stroke: str | None = None,
        stroke_width: int = 0,
        opacity: float = 1,
        rotation: int = 0,
        changelog: dict | None = None,
    ) -> str:
        element_id, z_index = self.deck._next_element("shape")
        content = {"id": element_id, "slideId": self.id, "groupId": None}
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "width": width,
            "height": height,
            "rotation": rotation,
            "zIndex": z_index,
            "opacity": opacity,
            "shapeType": shape_type,
            "fill": fill,
            "stroke": stroke or fill,
            "strokeWidth": stroke_width,
            "updatedAt": self.deck.now,
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content, change, "shapeElements")

    def add_icon(
        self,
        icon_name: str,
        *,
        x: int,
        y: int,
        size: int = 64,
        color: str = "#c67c3a",
        opacity: float = 1,
        rotation: int = 0,
        changelog: dict | None = None,
    ) -> str:
        element_id, z_index = self.deck._next_element("icon")
        content = {
            "id": element_id,
            "slideId": self.id,
            "groupId": None,
            "iconName": icon_name,
            "iconSource": "lucide",
        }
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "width": size,
            "height": size,
            "rotation": rotation,
            "zIndex": z_index,
            "color": color,
            "opacity": opacity,
            "updatedAt": self.deck.now,
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content, change, "iconElements")

    def add_image(
        self,
        src: str,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        is_background: bool = False,
        border_radius: int = 0,
        opacity: float = 1,
        rotation: int = 0,
        shadow: dict | None = None,
        border: dict | None = None,
        crop_ratio: str = "free",
        crop_rect: dict | None = None,
        focus_point: dict | None = None,
        changelog: dict | None = None,
    ) -> str:
        element_id, z_index = self.deck._next_element("image")
        content = {
            "id": element_id,
            "slideId": self.id,
            "groupId": None,
            "src": src,
            "s3Key": None,
            "isBackground": is_background,
            "_smartDiagram": False,
        }
        shadow_block = {
            "enabled": False,
            "angle": 135,
            "color": "#000000",
            "opacity": 40,
            "distance": 8,
            "blur": 12,
            "size": 0,
            "spread": 0,
        }
        border_block = {"type": "none", "width": 4, "color": "#000000", "specialStyle": None}
        _merge(shadow_block, shadow)
        _merge(border_block, border)
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "width": width,
            "height": height,
            "rotation": rotation,
            "zIndex": z_index,
            "opacity": opacity,
            "borderRadius": border_radius,
            "shadow": shadow_block,
            "border": border_block,
            "cropRatio": crop_ratio,
            "cropRect": crop_rect or {"left": 0, "top": 0, "right": 0, "bottom": 0},
            "focusPoint": focus_point or {"x": 50, "y": 50},
            "updatedAt": self.deck.now,
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content, change, "imageElements")

    def add_chart(
        self,
        chart_type: str,
        chart_config: dict,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        rotation: int = 0,
        changelog: dict | None = None,
    ) -> str:
        element_id, z_index = self.deck._next_element("chart")
        content = {
            "id": element_id,
            "slideId": self.id,
            "groupId": None,
            "svgDataUrl": "",
            "chartType": chart_type,
            "chartConfig": chart_config,
        }
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "width": width,
            "height": height,
            "rotation": rotation,
            "zIndex": z_index,
            "updatedAt": self.deck.now,
            "chartType": chart_type,
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content, change, "chartElements")

    def add_table(
        self,
        cells: dict,
        *,
        x: int,
        y: int,
        col_widths: list[int],
        row_heights: list[int],
        font_size: int = 20,
        table_color: str = "#1c1917",
        table_bg: str = "#ffffff",
        table_bold: bool = False,
        table_italic: bool = False,
        table_align: str = "left",
        content: dict | None = None,
        changelog: dict | None = None,
    ) -> str:
        element_id, z_index = self.deck._next_element("table")
        content_record = {
            "id": element_id,
            "slideId": self.id,
            "groupId": None,
            "type": "table",
            "position": {"x": x, "y": y},
            "zIndex": z_index,
            "cells": cells,
            "colWidths": col_widths,
            "rowHeights": row_heights,
            "tableFontSize": font_size,
            "tableBold": table_bold,
            "tableItalic": table_italic,
            "tableAlign": table_align,
            "tableColor": table_color,
            "tableBg": table_bg,
        }
        _merge(content_record, content)
        change = {
            "slideId": self.id,
            "position": {"x": x, "y": y},
            "zIndex": z_index,
            "updatedAt": self.deck.now,
            "style": {"colWidths": col_widths, "rowHeights": row_heights},
        }
        _merge(change, changelog)
        return self.deck._register(self, element_id, content_record, change, "tableElements")
