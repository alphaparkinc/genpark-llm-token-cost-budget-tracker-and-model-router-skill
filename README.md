# genpark-llm-token-cost-budget-tracker-and-model-router-skill

Real-time LLM token spend tracker, tenant budget ceiling guard, and complexity-based model down-router.

100% Python Standard Library implementation with zero external dependencies.

## Key Capabilities

- **Unified Multi-Provider Pricing Matrix**: Accurate per-million token pricing across frontier and fast models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro/Flash).
- **Tenant-Level Spend & Budget Ceilings**: Tracks cumulative expenditures, remaining balances, and automatically triggers alerts when reaching budget limits.
- **Smart Complexity-Based Model Routing**: Cascades simple tasks to fast models (slashing costs by >90%) while reserving frontier models for code and deep reasoning.
- **Zero-Latency In-Memory Accounting**: Thread-safe in-memory accounting with zero external database dependencies.

## Architecture

```
[Inbound User Prompt / Inference Token Metrics]
                        │
                        ▼
┌────────────────────────────────────────────────────────┐
│                   ModelCostRouter                      │
│  - Multi-Model Pricing Matrix Evaluator                │
│  - Prompt Complexity Heuristic Classifier              │
│  - Tenant Budget Ceiling & Cumulative Spend Ledger     │
│  - Cost Optimization Model Tier Arbiter                │
└────────────────────────────────────────────────────────┘
          │                                  │
  (Complex Prompt)                    (Routine Task)
          ▼                                  ▼
[Route to Frontier Tier]             [Route to Fast Tier: 90%+ Savings]
```

## MCP Server Integration

Run standard MCP stdio server:
```bash
python mcp_server.py
```

Exposed Tools:
- `calculate_cost`: Calculates inference dollar cost based on model and token counts.
- `record_usage`: Records token usage for a tenant, tracking spend against maximum budget limits.
- `route_by_complexity`: Determines optimal model tier (frontier vs fast) by analyzing prompt complexity.

## Quickstart (Python API)

```python
from client import ModelCostRouter

cost = ModelCostRouter.calculate_cost("gpt-4o", prompt_tokens=5000, completion_tokens=1000)
print(f"Call Cost: ${cost}")
```

---

## GenPark Ecosystem

- **Official Website**: [https://www.genpark.ai](https://www.genpark.ai)
- **LinkedIn Page**: [https://www.linkedin.com/company/92955550](https://www.linkedin.com/company/92955550)
