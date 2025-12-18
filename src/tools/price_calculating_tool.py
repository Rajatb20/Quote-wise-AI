import json
from crewai.tools import BaseTool
from pricing_engine import PricingRulesEngine

class PricingCalculatorTool(BaseTool):
    name: str = "Advanced Pricing Calculator Tool"
    description: str = (
        "Calculates final prices for a list of products. "
        "The input must be a JSON string representing a list of objects. "
        "Each object must have two keys: 'product_json' (containing the product's data) and 'quantity' (the integer quantity for that product)."
    )

    def _run(self, line_items_json: str) -> str:
        try:
            line_items = json.loads(line_items_json)
            if not isinstance(line_items, list):
                return json.dumps({"error": "Input must be a JSON array of line items."})
        except (json.JSONDecodeError, TypeError) as e:
            return f"Error: Invalid JSON data provided. Details: {e}"

        all_results = []
        for item in line_items:
            product_data = item.get('product_json')
            quantity = item.get('quantity')

            if not product_data or quantity is None:
                all_results.append({"error": "Skipping item due to missing 'product_json' or 'quantity'."})
                continue
            
            try:
                engine = PricingRulesEngine(product=product_data, quantity=int(quantity))
                pricing_result = engine.calculate_price()
                all_results.append(pricing_result)
            except Exception as e:
                 all_results.append({"error": f"Failed to process item {product_data.get('Product_Name', 'Unknown')}. Details: {e}"})

        return json.dumps(all_results)