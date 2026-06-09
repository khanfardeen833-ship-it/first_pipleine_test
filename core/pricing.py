"""
Pricing data and cost calculation for AWS Bedrock models.
"""

# AWS Bedrock pricing for supported models
# Source: https://aws.amazon.com/bedrock/pricing/
KNOWN_PRICING = {
    "claude-opus-4-8": {
        "input":           5.00,
        "output":         25.00,
        "cache_write_5m":  6.25,
        "cache_write_1h": 10.00,
        "cache_read":      0.50,
    },
    "claude-opus-4-7": {
        "input":           5.00,
        "output":         25.00,
        "cache_write_5m":  6.25,
        "cache_write_1h": 10.00,
        "cache_read":      0.50,
    },
    "claude-sonnet-4-6": {
        "input":           3.00,
        "output":         15.00,
        "cache_write_5m":  3.75,
        "cache_write_1h":  6.00,
        "cache_read":      0.30,
    },
    "claude-haiku-4-5": {
        "input":           1.00,
        "output":          5.00,
        "cache_write_5m":  1.25,
        "cache_write_1h":  2.00,
        "cache_read":      0.10,
    },
}


def get_pricing(model_id: str):
    for key, rates in KNOWN_PRICING.items():
        if key in model_id.lower():
            return rates, True
    return None, False


def calculate_cost(rates, usage: dict) -> dict:
    input_tok    = usage.get("input_tokens", 0) or 0
    output_tok   = usage.get("output_tokens", 0) or 0
    cache_5m     = usage.get("ephemeral_5m_input_tokens", 0) or 0
    cache_1h     = usage.get("ephemeral_1h_input_tokens", 0) or 0
    cache_create = usage.get("cache_creation_input_tokens", 0) or 0
    cache_read   = usage.get("cache_read_input_tokens", 0) or 0
    cache_write_tok = cache_5m + cache_1h + (0 if (cache_5m or cache_1h) else cache_create)

    if rates is None:
        return {
            "input_tok": input_tok, "output_tok": output_tok,
            "cache_write_tok": cache_write_tok, "cache_read_tok": cache_read,
            "cost_input": None, "cost_output": None,
            "cost_cache_write": None, "cost_cache_read": None, "total": None,
        }

    cost_cache_write = (
        (cache_5m * rates["cache_write_5m"] + cache_1h * rates["cache_write_1h"]) / 1_000_000
        if (cache_5m or cache_1h)
        else cache_create * rates["cache_write_1h"] / 1_000_000
    )
    cost_input      = input_tok  * rates["input"]      / 1_000_000
    cost_output     = output_tok * rates["output"]     / 1_000_000
    cost_cache_read = cache_read * rates["cache_read"] / 1_000_000

    return {
        "input_tok": input_tok, "output_tok": output_tok,
        "cache_write_tok": cache_write_tok, "cache_read_tok": cache_read,
        "cost_input": cost_input, "cost_output": cost_output,
        "cost_cache_write": cost_cache_write, "cost_cache_read": cost_cache_read,
        "total": cost_input + cost_output + cost_cache_write + cost_cache_read,
    }


def fmt_money(amount) -> str:
    if amount is None:
        return "n/a"
    if amount < 0.01:
        return f"${amount:.4f}"
    if amount < 1:
        return f"${amount:.3f}"
    return f"${amount:.2f}"
