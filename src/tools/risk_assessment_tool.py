import json
from crewai.tools import BaseTool

class RiskAssessmentTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = (
        "Analyzes the pricing strategy JSON of a SINGLE line item to identify business risks like high discounts. "
        "The input must be the JSON object for one priced item."
    )

    def _run(self, item_pricing_json: str) -> str:
        try:
            strategy_data = json.loads(item_pricing_json)
        except (json.JSONDecodeError, TypeError) as e:
            return f"Error: Invalid JSON from input. Details: {e}."

        # --- FIX STARTS HERE ---
        # First, check if the item is even approved for a quote.
        # If not, it poses no pricing risk and we can exit early.
        if not strategy_data.get('approved_for_quote', False):
            reason = strategy_data.get('status', 'Item not available for quoting.')
            return json.dumps({
                "risk_level": "Low", 
                "summary": f"Item '{strategy_data.get('product_name', 'Unknown')}' poses no pricing risk as it is not being quoted. Reason: {reason}"
            })
        # --- FIX ENDS HERE ---

        high_risk_flags = []
        max_allowed_discount = 25.0

        # This check will now only run on approved items with valid pricing data.
        adjustment = strategy_data.get('net_price_adjustment_percentage', 0)
        
        # Add a check to ensure adjustment is not None before comparison
        if adjustment is not None and adjustment < -max_allowed_discount:
            high_risk_flags.append(f"Risk: Net discount for '{strategy_data.get('product_name')}' is {abs(adjustment)}%, which exceeds the maximum of {max_allowed_discount}%.")
        
        reasons = strategy_data.get('reasoning_breakdown', [])
        for reason in reasons:
            if "Capped" in reason:
                high_risk_flags.append(f"Heads-up: A discount for '{strategy_data.get('product_name')}' was automatically capped.")

        if not high_risk_flags:
            return json.dumps({"risk_level": "Low", "summary": f"Item '{strategy_data.get('product_name')}' passed all checks."})
        else:
            return json.dumps({"risk_level": "High", "summary": "High risk detected.", "reasons": high_risk_flags})