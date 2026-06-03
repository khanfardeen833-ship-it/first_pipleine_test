"""
Schema compression configuration and feature flags.

Controls which optimization phases are enabled:
- "legacy": No compression (baseline, for A/B testing)
- "phase1": Metadata precomputation (5-10% savings, low risk)
- "phase2": Style compression (15-25% savings, medium risk)
- "phase3": Layout templates (20-30% savings, medium-high risk)

Environment variable: SCHEMA_COMPRESSION_MODE
Default: "phase1"
"""

import os
from enum import Enum


class CompressionMode(Enum):
    """Schema compression phase selection."""
    LEGACY = "legacy"        # No compression
    PHASE1 = "phase1"        # Metadata precomputation only
    PHASE2 = "phase2"        # Phase1 + Style compression
    PHASE3 = "phase3"        # Phase1 + Phase2 + Layout templates


class SchemaCompressionConfig:
    """
    Feature flags for schema compression phases.

    Configuration is driven by environment variables to enable A/B testing
    without code changes.
    """

    # Default mode (can override with environment variable)
    DEFAULT_MODE = CompressionMode.PHASE1

    @staticmethod
    def get_mode() -> CompressionMode:
        """Get current compression mode from environment or default."""
        mode_str = os.getenv("SCHEMA_COMPRESSION_MODE", SchemaCompressionConfig.DEFAULT_MODE.value)
        try:
            return CompressionMode(mode_str)
        except ValueError:
            # Invalid mode, use default
            print(f"Warning: Invalid SCHEMA_COMPRESSION_MODE={mode_str}, using {SchemaCompressionConfig.DEFAULT_MODE.value}")
            return SchemaCompressionConfig.DEFAULT_MODE

    @staticmethod
    def is_enabled(phase: int) -> bool:
        """
        Check if a compression phase is enabled.

        Args:
            phase: Phase number (1, 2, or 3)

        Returns:
            True if the current mode includes this phase
        """
        mode = SchemaCompressionConfig.get_mode()

        if mode == CompressionMode.LEGACY:
            return False
        elif mode == CompressionMode.PHASE1:
            return phase == 1
        elif mode == CompressionMode.PHASE2:
            return phase in (1, 2)
        elif mode == CompressionMode.PHASE3:
            return phase in (1, 2, 3)

        return False

    @staticmethod
    def get_compression_mode_string() -> str:
        """Get compression mode as string."""
        return SchemaCompressionConfig.get_mode().value

    # Phase-specific flags (derived from mode)
    @staticmethod
    def precompute_metadata() -> bool:
        """Phase 1: Generate UUID, IDs, timestamps client-side."""
        return SchemaCompressionConfig.is_enabled(1)

    @staticmethod
    def compress_styles() -> bool:
        """Phase 2: Use styleRef instead of inline styles."""
        return SchemaCompressionConfig.is_enabled(2)

    @staticmethod
    def use_layout_templates() -> bool:
        """Phase 3: Use layout templates with slot references."""
        return SchemaCompressionConfig.is_enabled(3)

    @staticmethod
    def skip_id_generation() -> bool:
        """Legacy mode: Skip ID generation (Opus generates them)."""
        return SchemaCompressionConfig.get_mode() == CompressionMode.LEGACY


# Quick access helper
def get_compression_mode() -> str:
    """Get compression mode for convenience."""
    return SchemaCompressionConfig.get_compression_mode_string()


# Example usage:
#
# from core.schema_config import SchemaCompressionConfig, get_compression_mode
#
# # In runner.py:
# if SchemaCompressionConfig.precompute_metadata():
#     batch_json = apply_schema_compression(batch_json, compression_mode="phase1")
#
# # In system prompt builder:
# if SchemaCompressionConfig.precompute_metadata():
#     system_prompt += "\n[SCHEMA_COMPRESSION_INSTRUCTIONS]\n..."
#
# # Environment override:
# export SCHEMA_COMPRESSION_MODE=legacy    # Run baseline
# export SCHEMA_COMPRESSION_MODE=phase1    # Run with metadata precomputation
# export SCHEMA_COMPRESSION_MODE=phase2    # Run with style compression
