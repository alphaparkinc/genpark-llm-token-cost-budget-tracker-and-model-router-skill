"""Example usage for LLM Token Cost Budget Tracker and Model Router."""
from client import ModelCostRouter


def main():
    router = ModelCostRouter()
    tenant = "org_fintech_labs"

    print("=== 1. Calculating Call Costs ===")
    cost_gpt4o = ModelCostRouter.calculate_cost("gpt-4o", prompt_tokens=10_000, completion_tokens=2_000)
    cost_mini = ModelCostRouter.calculate_cost("gpt-4o-mini", prompt_tokens=10_000, completion_tokens=2_000)
    print(f"GPT-4o (12k tokens): ${cost_gpt4o}")
    print(f"GPT-4o-mini (12k tokens): ${cost_mini} (Savings: {round((1 - cost_mini/cost_gpt4o)*100, 1)}%)")

    print("\n=== 2. Recording Usage & Enforcing Budget Ceiling ===")
    budget = 0.10  # Low budget for demonstration
    u1 = router.record_usage(tenant, "gpt-4o", 10_000, 2_000, budget_limit_usd=budget)
    print(f"Usage 1: Spent ${u1['cumulative_spent_usd']} / ${u1['budget_limit_usd']} (Status: {u1['status']})")

    u2 = router.record_usage(tenant, "gpt-4o", 20_000, 4_000, budget_limit_usd=budget)
    print(f"Usage 2: Spent ${u2['cumulative_spent_usd']} / ${u2['budget_limit_usd']} (Status: {u2['status']})")

    print("\n=== 3. Complexity-Based Smart Model Routing ===")
    simple_prompt = "What is the capital of Spain?"
    complex_prompt = "Write a Python class with def execute(self) to parse recursive AST trees and prove safety."

    r_simple = ModelCostRouter.route_by_complexity(simple_prompt)
    print(f"Simple Prompt -> Model: {r_simple['selected_model']} ({r_simple['tier']}) - Reason: {r_simple['reason']}")

    r_complex = ModelCostRouter.route_by_complexity(complex_prompt)
    print(f"Complex Prompt -> Model: {r_complex['selected_model']} ({r_complex['tier']}) - Reason: {r_complex['reason']}")


if __name__ == "__main__":
    main()
