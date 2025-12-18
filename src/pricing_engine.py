import json
from datetime import datetime

# --- CONFIGURATIONS ---
# This section makes it easy to change business logic without digging into the code.
# You can expand this list with any category you consider seasonal for summer.
SEASONAL_SUMMER_CATEGORIES = ['Toys & Games', 'Sports & Outdoors', 'Fashion & Apparel']


class PricingRulesEngine:
    """
    Calculates the final price for a product based on a set of business rules.
    It considers inventory levels, order quantity, and dynamic factors like seasonality.
    """
    def __init__(self, product: dict, quantity: int):
        """
        Initializes the engine with product data and the requested quantity.

        Args:
            product (dict): A dictionary containing the product's details from the inventory.
            quantity (int): The number of units being requested by the customer.
        """
        self.product = product
        self.quantity = quantity
        self.base_price = float(product.get('Min_Selling_Price_Rs', 0))
        self.adjustments = []
        self.final_price = self.base_price

    def _apply_factor_based_rules(self):
        """
        Reads the product's factors ('Factor_1', 'Factor_2', 'Factor_3') and applies
        relevant pricing strategies in a dynamic and scalable way.
        """
        factors = [
            str(self.product.get('Factor_1', '')).strip(),
            str(self.product.get('Factor_2', '')).strip(),
            str(self.product.get('Factor_3', '')).strip()
        ]

        # --- DYNAMIC SEASONAL PRICING RULE ---
        # Checks if 'Weather & Seasons' is a factor and if the current date is in summer.
        if 'Weather & Seasons' in factors:
            product_category = self.product.get('Category', '')
            today = datetime.now()
            # Assuming summer months are May through August
            is_summer_season = today.month in [5, 6, 7, 8]

            if is_summer_season and product_category in SEASONAL_SUMMER_CATEGORIES:
                self.adjustments.append({
                    "type": "markup",
                    "value": 10.0,
                    "reason": f"In-Season Demand Markup: '{product_category}' is a popular summer category."
                })

        # --- DEMOGRAPHIC PRICING RULE ---
        if 'Age' in factors or 'Gender' in factors:
             self.adjustments.append({
                    "type": "markup",
                    "value": 3.0,
                    "reason": "Targeted Product Premium: Price adjusted for specific demographic appeal."
                })

        # --- VALUE-BASED PRICING OVERRIDE ---
        # If 'Purchasing Power' is a key factor, it may override inventory-based discounts.
        if 'Purchasing Power' in factors:
            for adj in self.adjustments:
                if "High Inventory Discount" in adj.get('reason', ''):
                    # Neutralize the discount by setting its value to 0
                    adj['value'] = 0
                    adj['reason'] = "Price Strategy Override: Item's price is driven by perceived value, not inventory levels."

    def _apply_inventory_rules(self):
        """Applies discounts based on high stock levels relative to the reorder level."""
        stock = self.product.get('Quantity_in_Stock', 0)
        reorder_level = self.product.get('Reorder_Level', 1)

        # Ensure reorder_level is not zero to avoid division errors
        if reorder_level and stock > 2 * reorder_level:
            # Calculate a discount that scales with how high the inventory is, capped at 20%
            discount_factor = (stock / (2 * reorder_level)) * 0.05
            discount_percentage = min(discount_factor, 0.20) * 100
            self.adjustments.append({
                "type": "discount",
                "value": discount_percentage,
                "reason": f"High Inventory Discount: Stock level ({stock}) is high compared to reorder point."
            })

    def _apply_order_value_rules(self):
        """Applies discounts for bulk orders."""
        if self.quantity >= 25:
            self.adjustments.append({
                "type": "discount",
                "value": 7.5,
                "reason": f"Bulk Order Discount: For ordering {self.quantity} units (25+)."
            })

    def calculate_price(self) -> dict:
        """
        Executes the pricing calculation pipeline.

        This is the main public method that performs pre-flight checks, applies all pricing
        rules, calculates the final price, and returns a structured result.

        Returns:
            dict: A dictionary containing the full pricing breakdown and status.
        """
        # --- 1. Pre-flight Checks for Data Integrity and Stock ---
        required_keys = ['Product_Name', 'Quantity_in_Stock', 'Stock_Status', 'Min_Selling_Price_Rs']
        missing_keys = [key for key in required_keys if key not in self.product or self.product.get(key) is None]
        if missing_keys:
            return {
                "product_name": self.product.get('Product_Name', 'Unknown'),
                "approved_for_quote": False,
                "status": f"Product data incomplete. Missing required fields: {', '.join(missing_keys)}"
            }

        stock_status = self.product.get('Stock_Status')
        stock_quantity = self.product.get('Quantity_in_Stock')

        # Check for stock availability before proceeding
        if stock_status == 'Out of Stock' or self.quantity > stock_quantity:
            status_msg = "Product is out of stock." if stock_status == 'Out of Stock' else f"Insufficient stock. Requested: {self.quantity}, Available: {stock_quantity}."
            return {
                "product_name": self.product.get('Product_Name'),
                "quantity_requested": self.quantity,
                "approved_for_quote": False,
                "status": status_msg
            }

        # --- 2. Apply Pricing Rules ---
        self._apply_inventory_rules()
        self._apply_order_value_rules()
        self._apply_factor_based_rules()

        # --- 3. Calculate Final Price ---
        total_adjustment_percentage = 0
        for adj in self.adjustments:
            if adj['type'] == 'discount':
                total_adjustment_percentage -= adj.get('value', 0)
            elif adj['type'] == 'markup':
                total_adjustment_percentage += adj.get('value', 0)

        final_single_unit_price = self.base_price * (1 + (total_adjustment_percentage / 100))
        total_price = final_single_unit_price * self.quantity

        # --- 4. Return Structured Output ---
        return {
            "product_name": self.product.get('Product_Name'),
            "quantity_requested": self.quantity,
            "approved_for_quote": True,
            "base_single_unit_price": round(self.base_price, 2),
            "final_single_unit_price": round(final_single_unit_price, 2),
            "total_price": round(total_price, 2),
            "net_price_adjustment_percentage": round(total_adjustment_percentage, 2),
            "reasoning_breakdown": [adj['reason'] for adj in self.adjustments if adj.get('value') != 0],
            "competitors": {
                "SmartBuy": self.product.get('SmartBuy'),
                "ClicKart": self.product.get('ClicKart'),
                "ShopiSky": self.product.get('ShopiSky'),
                "Neesho": self.product.get('Neesho')
            },
            "status": "Available"
        }