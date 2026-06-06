"""
Token usage and cost tracking across agent turns.
"""

import time
import json
from datetime import datetime
from core.pricing import get_pricing, calculate_cost


class PerformanceInstrument:
    """Detailed runtime performance tracking."""

    def __init__(self):
        self.stages = {}  # {stage_name: {start, end, duration_ms, metadata}}
        self.batches = []  # [{name, start, end, duration_s, tokens_in, tokens_out, prompt_size}]
        self.api_calls = []  # [{request_time, first_token_time, final_time, duration_s, first_token_latency_s, tokens_in, tokens_out}]
        self.turns = []  # [{turn_num, duration_ms, tokens_in, tokens_out, tool_calls}]
        self.retries = []  # [{reason, timestamp, turn}]
        self.validations = []  # [{attempt_num, passed, duration_s, problems_count}]

    def record_stage(self, stage_name: str, duration_seconds: float, metadata: dict = None):
        """Record timing for a pipeline stage."""
        self.stages[stage_name] = {
            "duration_seconds": duration_seconds,
            "duration_ms": duration_seconds * 1000,
            "metadata": metadata or {}
        }

    def record_batch(self, batch_name: str, duration_seconds: float, tokens_in: int, tokens_out: int, prompt_size: int = 0):
        """Record batch execution timing."""
        self.batches.append({
            "name": batch_name,
            "duration_seconds": round(duration_seconds, 2),
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "prompt_size_bytes": prompt_size,
        })

    def record_api_call(self, request_time: float, first_token_time: float, final_time: float, tokens_in: int, tokens_out: int):
        """Record Claude API call metrics."""
        duration = final_time - request_time
        first_token_latency = first_token_time - request_time if first_token_time else 0
        stream_duration = final_time - first_token_time if first_token_time else 0

        self.api_calls.append({
            "request_duration_seconds": round(duration, 2),
            "first_token_latency_seconds": round(first_token_latency, 2),
            "stream_duration_seconds": round(stream_duration, 2),
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
        })

    def record_turn(self, turn_num: int, duration_ms: float, tokens_in: int, tokens_out: int, tool_calls: int = 0):
        """Record per-turn timing and token usage."""
        self.turns.append({
            "turn": turn_num,
            "duration_ms": round(duration_ms, 1),
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "tool_calls": tool_calls,
        })

    def record_retry(self, reason: str):
        """Record a retry event."""
        self.retries.append({
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        })

    def record_validation(self, attempt_num: int, passed: bool, duration_seconds: float, problems_count: int):
        """Record validation attempt."""
        self.validations.append({
            "attempt": attempt_num,
            "passed": passed,
            "duration_seconds": round(duration_seconds, 2),
            "problems_count": problems_count,
        })

    def to_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            "stages": self.stages,
            "batches": self.batches,
            "api_calls": self.api_calls,
            "turns": self.turns,
            "retries": self.retries,
            "validations": self.validations,
        }


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

        # Skill routing metadata
        self.skill_routing = None

        # Phase tracking for hybrid pipeline
        self.phase = None  # "planning", "design", or None
        self.phase_start = None  # Start time of current phase
        self.phase_duration_seconds = None  # Duration of current phase
        self.phases = {}  # Dict of phase_name -> {duration, tokens_input, tokens_output, model, cost}

        self._last_usage_snapshot = None

        # Performance instrumentation
        self.perf = PerformanceInstrument()
        self.batch_name = None
        self.batch_start_time = None

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

    def start_phase(self, phase_name: str):
        """Begin tracking a new phase."""
        self.phase = phase_name
        self.phase_start = time.time()

    def end_phase(self):
        """End current phase and record duration."""
        if self.phase is not None and self.phase_start is not None:
            duration = time.time() - self.phase_start
            self.phase_duration_seconds = duration

            # Record phase metadata
            phase_name = self.phase  # Store before clearing
            self.phases[phase_name] = {
                "duration_seconds": duration,
                "tokens_input": self.input_tokens,
                "tokens_output": self.output_tokens,
                "model": self.model,
            }

            # Calculate cost for this phase
            breakdown = self.get_total_breakdown()
            if breakdown.get("total") is not None:
                self.phases[phase_name]["cost"] = breakdown.get("total", 0.0)

            self.phase = None
            self.phase_start = None
