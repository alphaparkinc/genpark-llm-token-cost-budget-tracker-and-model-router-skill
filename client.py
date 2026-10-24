"""LLM Token Cost Budget Tracker and Model Router.
100% Python Standard Library.
"""

import time
import re
from typing import Dict, Any, Optional


class ModelCostRouter:
    """Tracks cumulative LLM token expenditure per tenant, enforces budget ceilings,
    and intelligently routes prompts to cost-effective models based on task complexity."""

    # Cost per 1,000,000 tokens in USD (Input, Output)
    PRICING_TABLE = {
        "gpt-4o": {"input": 2.50, "output": 10.00, "tier": "frontier"},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60, "tier": "fast"},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "tier": "frontier"},
        "claude-3-5-haiku": {"input": 0.80, "output": 4.00, "tier": "fast"},
        "gemini-1-5-pro": {"input": 1.25, "output": 5.00, "tier": "frontier"},
        "gemini-1-5-flash": {"input": 0.075, "output": 0.30, "tier": "fast"},
    }

    def __init__(self):
        # Maps tenant_id -> {"total_spent": float, "total_tokens": int, "call_count": int}
        self.tenant_ledgers: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def calculate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculates exact dollar cost for an inference call based on token counts."""
        pricing = cls.PRICING_TABLE.get(model.lower(), {"input": 2.00, "output": 8.00})
        input_cost = (prompt_tokens / 1_000_000.0) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000.0) * pricing["output"]
        return round(input_cost + output_cost, 6)

    def record_usage(
        self,
        tenant_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        budget_limit_usd: float = 50.0,
    ) -> Dict[str, Any]:
        """Records token usage, updates cumulative expenditure, and evaluates budget ceiling."""
        if tenant_id not in self.tenant_ledgers:
            self.tenant_ledgers[tenant_id] = {
                "total_spent_usd": 0.0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_calls": 0,
            }

        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        ledger = self.tenant_ledgers[tenant_id]

        ledger["total_spent_usd"] = round(ledger["total_spent_usd"] + cost, 6)
        ledger["total_prompt_tokens"] += prompt_tokens
        ledger["total_completion_tokens"] += completion_tokens
        ledger["total_calls"] += 1

        spent = ledger["total_spent_usd"]
        remaining = round(max(0.0, budget_limit_usd - spent), 4)
        pct_used = round((spent / budget_limit_usd) * 100.0, 2) if budget_limit_usd > 0 else 100.0
        exceeded = spent >= budget_limit_usd

        return {
            "tenant_id": tenant_id,
            "call_cost_usd": cost,
            "cumulative_spent_usd": spent,
            "budget_limit_usd": budget_limit_usd,
            "budget_remaining_usd": remaining,
            "budget_used_percent": pct_used,
            "budget_exceeded": exceeded,
            "status": "BUDGET_EXCEEDED" if exceeded else ("BUDGET_WARNING" if pct_used >= 80 else "BUDGET_HEALTHY"),
        }

    @classmethod
    def route_by_complexity(
        cls,
        prompt: str,
        force_frontier: bool = False,
    ) -> Dict[str, Any]:
        """Analyzes prompt length, code blocks, and complex reasoning keywords to choose
        between high-capability frontier models and low-cost fast models."""
        if force_frontier:
            return {
                "selected_model": "gpt-4o",
                "tier": "frontier",
                "reason": "Explicitly requested frontier reasoning tier.",
            }

        # Complexity heuristics
        has_code = "```" in prompt or any(kw in prompt for kw in ["def ", "class ", "function(", "SELECT ", "import "])
        is_long = len(prompt.split()) > 400
        has_deep_reasoning = any(kw in prompt.lower() for kw in ["prove", "analyze blast radius", "step-by-step mathematical", "architect", "audit"])

        is_complex = has_code or is_long or has_deep_reasoning

        if is_complex:
            return {
                "selected_model": "gpt-4o",
                "tier": "frontier",
                "reason": "Complex task detected: involves code, deep reasoning, or extensive prompt length.",
                "complexity_signals": {
                    "has_code": has_code,
                    "is_long_prompt": is_long,
                    "has_deep_reasoning": has_deep_reasoning,
                },
            }
        else:
            return {
                "selected_model": "gpt-4o-mini",
                "tier": "fast",
                "reason": "Standard task: routed to cost-efficient fast tier to minimize token expenditure.",
                "complexity_signals": {
                    "has_code": False,
                    "is_long_prompt": False,
                    "has_deep_reasoning": False,
                },
            }
