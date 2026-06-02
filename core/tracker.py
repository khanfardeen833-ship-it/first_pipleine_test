"""
Token usage and cost tracking across agent turns.
"""

import time
from core.pricing import get_pricing, calculate_cost


class Tracker:
    def __init__(self, model: str):
        self.start = time.time()
        self.model = model
        self.rates, self.pricing_known = get_pricing(model)

        self.turns = 0
        self.tool_calls = []
        self.files_written = []
        self.bash_commands = []
        self.thinking_total_chars = 0

        self.input_tokens = 0
        self.output_tokens = 0
        self.cache_creation = 0
        self.cache_read = 0
        self.ephemeral_5m = 0
        self.ephemeral_1h = 0

        self.per_turn_costs = []
        self.sdk_reported_cost = 0.0
        self.last_error = None
        self.permission_denials = []

        self._last_usage_snapshot = None

    def record_usage(self, usage: dict):
        snapshot = (
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0),
            usage.get("cache_creation_input_tokens", 0),
            usage.get("cache_read_input_tokens", 0),
        )
        if snapshot == self._last_usage_snapshot:
            return None
        self._last_usage_snapshot = snapshot

        input_tok  = usage.get("input_tokens", 0) or 0
        output_tok = usage.get("output_tokens", 0) or 0
        cc_tok     = usage.get("cache_creation_input_tokens", 0) or 0
        cr_tok     = usage.get("cache_read_input_tokens", 0) or 0

        cc_obj = usage.get("cache_creation", {}) or {}
        tok_5m = cc_obj.get("ephemeral_5m_input_tokens", 0) or 0
        tok_1h = cc_obj.get("ephemeral_1h_input_tokens", 0) or 0

        self.input_tokens   += input_tok
        self.output_tokens  += output_tok
        self.cache_creation += cc_tok
        self.cache_read     += cr_tok
        self.ephemeral_5m   += tok_5m
        self.ephemeral_1h   += tok_1h

        breakdown = calculate_cost(self.rates, {
            "input_tokens":                input_tok,
            "output_tokens":               output_tok,
            "cache_creation_input_tokens": cc_tok,
            "cache_read_input_tokens":     cr_tok,
            "ephemeral_5m_input_tokens":   tok_5m,
            "ephemeral_1h_input_tokens":   tok_1h,
        })
        if breakdown["total"] is not None:
            self.per_turn_costs.append(breakdown["total"])
        return breakdown

    def get_total_breakdown(self) -> dict:
        return calculate_cost(self.rates, {
            "input_tokens":                self.input_tokens,
            "output_tokens":               self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation,
            "cache_read_input_tokens":     self.cache_read,
            "ephemeral_5m_input_tokens":   self.ephemeral_5m,
            "ephemeral_1h_input_tokens":   self.ephemeral_1h,
        })
