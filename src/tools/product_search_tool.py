import os
import pandas as pd
from crewai.tools import BaseTool
from difflib import get_close_matches
import json

class ProductDataTool(BaseTool):
    name: str = "Westside Product Data Tool"
    description: str = "Useful for retrieving specific product details from the Westside Products CSV. The input to this tool should be a list of one or more Product Names."

    def _run(self, product_identifiers: list[str]) -> str:
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Westside_Inventory.csv')

        try:
            df = pd.read_csv(file_path, parse_dates=['Manufacturing Date', 'Last Sold Date'])
            df['Product Name'] = df['Product Name'].str.strip()
        except FileNotFoundError:
            return f"Error: The data file was not found at the expected path."
        except Exception as e:
            return f"Error: An unexpected error occurred while reading the data file: {e}"

        if not isinstance(product_identifiers, list):
            return "Error: Input must be a list of strings (product names)."

        try:
            # --- FIX STARTS HERE ---
            # Sanitize all incoming identifiers for a clean, case-insensitive match
            sanitized_identifiers = [name.strip().lower() for name in product_identifiers]
            
            # Perform an exact, case-insensitive match using .isin() for accuracy
            results = df[df['Product Name'].str.strip().str.lower().isin(sanitized_identifiers)]
            # --- FIX ENDS HERE ---
        except Exception as e:
            return f"Error during product search: {e}"

        if results.empty:
            # --- FIX STARTS HERE ---
            # Provide a more informative message about which products were not found and suggest alternatives.
            all_product_names = df['Product Name'].str.strip().tolist()
            not_found_products = [
                name for name in product_identifiers
                if name.strip().lower() not in results['Product Name'].str.strip().str.lower().tolist()
            ]
            
            error_message = f"No exact matches found for: {', '.join(not_found_products)}. "
            
            suggestions = []
            for name in not_found_products:
                close_matches = get_close_matches(name, all_product_names, n=3, cutoff=0.6)
                if close_matches:
                    suggestions.append(f"For '{name}', did you mean: {', '.join(close_matches)}?")
            
            if suggestions:
                error_message += " ".join(suggestions)

            return error_message
            # --- FIX ENDS HERE ---
        
        results = results.copy()
        
        results.columns = results.columns.str.replace(r'[. ()]', '_', regex=True).str.replace(r'__', '_', regex=True)
        
        relevant_columns = [
            'Product_Name', 'Factor_1', 'Factor_2', 'Factor_3', 'Category', 'Sub-category', 'Size',
            'Color', 'Min_Selling_Price_Rs_', 'Max_Selling_Price_MRP__Rs_', 'Quantity_in_Stock',
            'Stock_Status', 'Reorder_Level', 'Manufacturing_Date', 'Last_Sold_Date',
            'SmartBuy', 'ClicKart', 'ShopiSky', 'Neesho'
        ]
        
        existing_relevant_columns = [col for col in relevant_columns if col in results.columns]

        for col in ['Manufacturing_Date', 'Last_Sold_Date']:
            if col in results.columns:
                results[col] = results[col].dt.strftime('%Y-%m-%d')

        column_rename_map = {
            'Min_Selling_Price_Rs_': 'Min_Selling_Price_Rs',
            'Max_Selling_Price_MRP__Rs_': 'Max_Selling_Price_MRP_Rs'
        }
        
        results = results.rename(columns=column_rename_map)
        
        existing_relevant_columns = [column_rename_map.get(col, col) for col in existing_relevant_columns]
                
        json_output = results[existing_relevant_columns].to_json(orient='records')
        return json_output

class SmartProductMatcher:
    def __init__(self, inventory_path='src/data/Westside_Inventory.csv'):
        """Initialize with inventory data."""
        self.df = pd.read_csv(inventory_path)
        # Clean product names for better matching
        self.df['Product_Name'] = self.df['Product_Name'].fillna('').str.strip()
        
    def find_product_matches(self, query, size=None, color=None, brand=None):
        """
        Find exact and close matches for a product query, considering attributes.
        Returns both exact matches and similar alternatives.
        """
        query = query.lower().strip()
        
        # 1. Try exact match first
        exact_matches = self.df[
            self.df['Product_Name'].str.lower() == query
        ]
        
        # 2. If no exact match, try fuzzy matching
        if len(exact_matches) == 0:
            # Get all unique product names
            all_products = self.df['Product_Name'].unique()
            # Find close matches
            close_matches = get_close_matches(query, all_products, n=5, cutoff=0.6)
            exact_matches = self.df[self.df['Product_Name'].isin(close_matches)]
        
        # 3. Filter by attributes if provided
        filtered_matches = exact_matches.copy()
        if size:
            size_matches = exact_matches[exact_matches['Size'].str.lower() == size.lower()]
            if not size_matches.empty:
                filtered_matches = size_matches
            
        if color:
            color_matches = filtered_matches[filtered_matches['Color'].str.lower() == color.lower()]
            if not color_matches.empty:
                filtered_matches = color_matches
                
        if brand:
            brand_matches = filtered_matches[filtered_matches['Brand'].str.lower() == brand.lower()]
            if not brand_matches.empty:
                filtered_matches = brand_matches
        
        # 4. Prepare results
        exact_variants = []
        alternative_suggestions = []
        
        # Add exact matches with requested attributes
        for _, row in filtered_matches.iterrows():
            exact_variants.append({
                'product_name': row['Product_Name'],
                'brand': row['Brand'],
                'size': row['Size'],
                'color': row['Color'],
                'stock': row['Quantity_in_Stock'],
                'status': row['Stock_Status']
            })
        
        # Add alternative suggestions (different size/color combinations)
        if len(exact_variants) == 0:
            for _, row in exact_matches.iterrows():
                alternative_suggestions.append({
                    'product_name': row['Product_Name'],
                    'brand': row['Brand'],
                    'size': row['Size'],
                    'color': row['Color'],
                    'stock': row['Quantity_in_Stock'],
                    'status': row['Stock_Status']
                })
        
        return {
            'query': query,
            'requested_attributes': {
                'size': size,
                'color': color,
                'brand': brand
            },
            'exact_matches': exact_variants,
            'alternative_suggestions': alternative_suggestions,
            'found_exact_match': len(exact_variants) > 0,
            'has_alternatives': len(alternative_suggestions) > 0
        }

    def format_response(self, match_results):
        """Format the match results into a user-friendly message."""
        response = []
        query = match_results['query']
        attrs = match_results['requested_attributes']
        
        # Format requested specifications
        specs = []
        if attrs['size']: specs.append(f"Size: {attrs['size']}")
        if attrs['color']: specs.append(f"Color: {attrs['color']}")
        if attrs['brand']: specs.append(f"Brand: {attrs['brand']}")
        specs_str = f" ({', '.join(specs)})" if specs else ""
        
        response.append(f"🔍 Searching for: {query}{specs_str}")
        
        # Exact matches
        if match_results['found_exact_match']:
            response.append("\n✅ Found exact matches:")
            for variant in match_results['exact_matches']:
                response.append(
                    f"- {variant['product_name']} ({variant['size']}, {variant['color']}) - "
                    f"{variant['stock']} units available"
                )
        
        # Alternative suggestions
        if match_results['has_alternatives']:
            response.append("\n💡 Alternative options available:")
            for alt in match_results['alternative_suggestions']:
                response.append(
                    f"- {alt['product_name']} ({alt['size']}, {alt['color']}) - "
                    f"{alt['stock']} units available"
                )
        
        # No matches
        if not match_results['found_exact_match'] and not match_results['has_alternatives']:
            response.append("\n❌ No matches or alternatives found.")
            
        return "\n".join(response)

def extract_product_details(product_line):
    """
    Extract product name, quantity, size, color, and brand from a product line.
    Handles various orderings and missing fields.
    """
    # Remove bullet points or numbers at start
    line = re.sub(r'^\s*[-*•\d.]+\s*', '', product_line).strip()

    # Patterns for attributes
    quantity_pattern = r'(\d+)\s*(?:units?|pcs|pieces|qty)?'
    size_pattern = r'(XS|S|M|L|XL|XXL|One Size|Small|Medium|Large)'
    color_pattern = r'(Black|White|Blue|Red|Green|Yellow|Grey|Pink|Charcoal|Silver|Gold|Brown|Orange|Purple)'
    brand_pattern = r'(HP|Apple|Sony|LG|Google|Samsung|Dell|Lenovo|Asus|Acer|Microsoft|Bose|JBL|Panasonic|Philips|OnePlus|Realme|Oppo|Vivo|Mi|Redmi|Nokia|Motorola|Amazon|Nest)'

    # Try to extract quantity
    quantity = None
    qty_match = re.search(quantity_pattern, line, re.IGNORECASE)
    if qty_match:
        quantity = int(qty_match.group(1))

    # Try to extract brand
    brand = None
    brand_match = re.search(brand_pattern, line, re.IGNORECASE)
    if brand_match:
        brand = brand_match.group(1)

    # Try to extract size
    size = None
    size_match = re.search(size_pattern, line, re.IGNORECASE)
    if size_match:
        size = size_match.group(1)

    # Try to extract color
    color = None
    color_match = re.search(color_pattern, line, re.IGNORECASE)
    if color_match:
        color = color_match.group(1)

    # Remove extracted attributes from line to get product name
    temp_line = line
    for pat in [quantity_pattern, size_pattern, color_pattern, brand_pattern]:
        temp_line = re.sub(pat, '', temp_line, flags=re.IGNORECASE)
    # Remove extra commas, "and", "of", etc.
    temp_line = re.sub(r'[,;]|and|of', '', temp_line, flags=re.IGNORECASE)
    product_name = temp_line.strip()

    # If brand is not None and not in product_name, prepend it
    if brand and not product_name.lower().startswith(brand.lower()):
        product_name = f"{brand} {product_name}".strip()

    return {
        'name': product_name,
        'quantity': quantity,
        'size': size,
        'color': color,
        'brand': brand
    }

def process_product_request(product_line):
    """Process a single product request line and return matching results."""
    # Extract product details
    details = extract_product_details(product_line)
    
    # Initialize matcher
    matcher = SmartProductMatcher()
    
    # Find matches
    matches = matcher.find_product_matches(
        details['name'],
        size=details['size'],
        color=details['color']
    )
    
    # Add extracted quantity to results
    matches['requested_quantity'] = details['quantity']
    
    return matches