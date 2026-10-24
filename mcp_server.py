"""MCP server for LLM Token Cost Budget Tracker and Model Router."""
import sys
import json
from client import ModelCostRouter

_router = ModelCostRouter()


def handle_request(req):
    method = req.get("method")
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "calculate_cost",
                    "description": "Calculates inference dollar cost based on model and token counts",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "model": {"type": "string"},
                            "prompt_tokens": {"type": "integer"},
                            "completion_tokens": {"type": "integer"},
                        },
                        "required": ["model", "prompt_tokens", "completion_tokens"],
                    },
                },
                {
                    "name": "record_usage",
                    "description": "Records token usage for a tenant, tracking spend against maximum budget limits",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "tenant_id": {"type": "string"},
                            "model": {"type": "string"},
                            "prompt_tokens": {"type": "integer"},
                            "completion_tokens": {"type": "integer"},
                            "budget_limit_usd": {"type": "number", "default": 50.0},
                        },
                        "required": ["tenant_id", "model", "prompt_tokens", "completion_tokens"],
                    },
                },
                {
                    "name": "route_by_complexity",
                    "description": "Determines optimal model tier (frontier vs fast) by analyzing prompt complexity",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "force_frontier": {"type": "boolean", "default": False},
                        },
                        "required": ["prompt"],
                    },
                },
            ]
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "calculate_cost":
            cost = ModelCostRouter.calculate_cost(
                model=args.get("model", ""),
                prompt_tokens=int(args.get("prompt_tokens", 0)),
                completion_tokens=int(args.get("completion_tokens", 0)),
            )
            return {"content": [{"type": "text", "text": json.dumps({"cost_usd": cost})}]}
        elif tool_name == "record_usage":
            res = _router.record_usage(
                tenant_id=args.get("tenant_id"),
                model=args.get("model"),
                prompt_tokens=int(args.get("prompt_tokens", 0)),
                completion_tokens=int(args.get("completion_tokens", 0)),
                budget_limit_usd=float(args.get("budget_limit_usd", 50.0)),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
        elif tool_name == "route_by_complexity":
            res = ModelCostRouter.route_by_complexity(
                prompt=args.get("prompt", ""),
                force_frontier=args.get("force_frontier", False),
            )
            return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
    return {"error": "Method not found"}


if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(json.dumps(handle_request(json.loads(line))))
            sys.stdout.flush()
