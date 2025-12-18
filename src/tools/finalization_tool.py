import os
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from crewai.tools import BaseTool
import re

class QuotePDF(FPDF):
    """
    A custom FPDF class to generate a professional quotation PDF.
    The design is clean, minimalistic, and avoids tables in favor of 
    listing product details in separate, easy-to-read blocks.
    """
    def header(self):

        self.set_font('Arial', 'B', 24)
        self.set_text_color(33, 47, 60)
        self.cell(0, 10, 'Your Company Name', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font('Arial', '', 10)
        self.cell(0, 6, 'Company Logo Placeholder', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

        # Quotation Number and Date
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.set_font('Arial', '', 11)
        self.cell(0, 6, f'Quotation Number: QT-{timestamp}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, f'Date: {datetime.now().strftime("%d-%m-%Y")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        # Footer line
        self.set_draw_color(200, 200, 200) # Light grey line
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        
        # Footer text
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, 'Thank you for your business! | Email: info@yourcompany.com | Phone: +91-XXXXXXXXXX', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.cell(0, 5, f'Page {self.page_no()}', align='C')

    def add_client_details(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, 'Client Details:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font('Arial', '', 11)
        self.cell(0, 6, 'Client Name: ___________________________', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, 'Client Address: _________________________', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, 'Contact: _______________________________', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(12)

    def add_quotation_details(self, products, notes, discount_summary):
        """
        This is the new method to display products in a block format,
        not a table. This solves the main issue.
        """
        # --- Quotation for Available Items Section ---
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, 'Quotation for Available Items', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

        for product in products:
            self.set_font('Arial', 'B', 11)
            self.cell(0, 6, f"Product: {product['name']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            self.set_font('Arial', '', 10)
            self.cell(0, 5, f"Quantity: {product['quantity']} units", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.cell(0, 5, f"MRP (Per Unit): INR {product['mrp']:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            if product.get('discount') and product['discount'] > 0:
                self.cell(0, 5, f"Discount Applied: {product['discount']:.2f}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                 self.cell(0, 5, "Discount: None", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            self.set_font('Arial', 'B', 10)
            self.cell(0, 5, f"Total Price: INR {product['total']:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(6) # Add space between product entries
        
        # --- Discount & Pricing Summary Section ---
        if discount_summary:
            self.set_font('Arial', 'B', 14)
            self.cell(0, 8, 'Discount & Pricing Summary', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(4)
            self.set_font('Arial', '', 10)
            for item in discount_summary:
                self.multi_cell(0, 5, item)
                self.ln(2)
            self.ln(6)

        # --- Notes on Your Request Section ---
        if notes:
            self.set_font('Arial', 'B', 14)
            self.cell(0, 8, 'Notes on Your Request', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(4)
            self.set_font('Arial', '', 10)
            for note in notes:
                self.multi_cell(0, 5, note)
                self.ln(2)
            self.ln(6)


    def add_grand_total(self, total_amount):
        self.ln(5)
        self.set_font('Arial', 'B', 16)
        # Use a green color for the total to make it stand out
        self.set_text_color(34, 139, 34) # Forest Green
        self.cell(0, 10, f'GRAND TOTAL: INR {total_amount:,.2f}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.set_text_color(0, 0, 0) # Reset text color
        self.ln(12)

    def add_terms_conditions(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, 'Terms and Conditions:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)
        
        terms = [
            "- Prices are inclusive of applicable taxes.",
            "- Quotation is valid for 30 days from the date of issue.",
            "- Delivery timeline is subject to inventory availability.",
            "- Payment terms: 50% advance, 50% on delivery."
        ]
        
        self.set_font('Arial', '', 10)
        for term in terms:
            self.cell(0, 6, term, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)

    def add_signature_section(self):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, 'Authorized Signature:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(15)
        
        self.set_font('Arial', '', 10)
        self.cell(0, 6, '_________________________', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 6, 'Name & Designation', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

class PDFCreationTool(BaseTool):
    name: str = "PDF Quote Creator"
    description: str = (
        "Creates a professional PDF file from a given quote text. "
        "The input to this tool should be the complete and final text content of the quote in markdown format."
    )

    def _parse_markdown_quote(self, quote_text: str) -> dict:
        """Parse the markdown quotation to extract structured data."""
        data = {
            'products': [],
            'discount_summary': [],
            'notes': [],
            'grand_total': 0.0
        }
        
        lines = quote_text.strip().split('\n')
        current_section = None
        
        # --- FIX STARTS HERE ---
        # Regex patterns for resilient parsing
        product_row_pattern = re.compile(r"\|\s*(.*?)\s*\|\s*(\d+)\s*\|\s*₹\s*([\d,]+\.?\d*)\s*\|\s*([\d.]+)%\s*\|\s*₹\s*([\d,]+\.?\d*)\s*\|")
        grand_total_pattern = re.compile(r"₹([\d,]+\.?\d*)")
        note_pattern = re.compile(r"-\s*\*\*(.*?)\*\*:\s*(.*)")
        # --- FIX ENDS HERE ---

        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('---'):
                continue
            
            # Section detection (made case-insensitive for robustness)
            if re.search(r'quotation for available items', line, re.IGNORECASE):
                current_section = 'products'
                continue
            elif re.search(r'discount & pricing summary', line, re.IGNORECASE):
                current_section = 'summary'
                continue
            elif re.search(r'notes on your request', line, re.IGNORECASE):
                current_section = 'notes'
                continue
            elif re.search(r'grand total', line, re.IGNORECASE):
                current_section = 'grand_total'
                continue

            # Parsing logic based on current section
            if current_section == 'products':
                # --- FIX STARTS HERE ---
                match = product_row_pattern.match(line)
                if match:
                    try:
                        product = {
                            'name': match.group(1).strip(),
                            'quantity': int(match.group(2).strip()),
                            'mrp': float(match.group(3).strip().replace(',', '')),
                            'discount': float(match.group(4).strip()),
                            'total': float(match.group(5).strip().replace(',', ''))
                        }
                        data['products'].append(product)
                    except (ValueError, IndexError):
                        continue # Safely skip malformed rows
                # --- FIX ENDS HERE ---
            
            elif current_section == 'summary' and line.startswith(('-', '*')):
                data['discount_summary'].append(line.lstrip('*- ').strip())

            elif current_section == 'notes' and line.startswith(('-', '*')):
                data['notes'].append(line.lstrip('*- ').strip())

            elif current_section == 'grand_total':
                # --- FIX STARTS HERE ---
                total_match = grand_total_pattern.search(line)
                # --- FIX ENDS HERE ---
                if total_match:
                    data['grand_total'] = float(total_match.group(1).replace(',', ''))
        
        return data

    def _run(self, quote_text: str) -> str:
        # --- FIX STARTS HERE ---
        # Calculate the project's root directory from this file's location
        # (__file__ is .../src/tools/finalization_tool.py, so we go up 3 levels)
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Define the output directory relative to the project root
        output_dir_name = "final_quotes"
        
        # Create the full, absolute path for the output directory
        output_dir_path = os.path.join(PROJECT_ROOT, output_dir_name)
        # --- FIX ENDS HERE ---

        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"Professional_Quotation_{timestamp}.pdf"
        
        # Create the full, absolute path for the file
        file_path = os.path.join(output_dir_path, file_name)

        try:
            # (Your parsing logic remains the same)
            data = self._parse_markdown_quote(quote_text)
            
            if not data['products'] and not data['grand_total']:
                return "Error: Failed to parse any products or grand total from the input text."

            pdf = QuotePDF()
            pdf.add_page()
            pdf.add_client_details()
            pdf.add_quotation_details(data['products'], data['notes'], data['discount_summary'])
            if data['grand_total'] > 0:
                pdf.add_grand_total(data['grand_total'])
            pdf.add_terms_conditions()
            pdf.add_signature_section()
            
            pdf.output(file_path)
            
            # Return the full, absolute path. This is crucial.
            return f"✅ Successfully created PDF quote at: {file_path}"
        except Exception as e:
            import traceback
            tb_str = traceback.format_exc()
            return f"Error: Failed to create PDF. Details: {e}\nTraceback:\n{tb_str}"