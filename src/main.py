"""
Enhanced main application for QuoteWise AI.
Features improved error handling, logging, caching, and modern UI components.
"""

import warnings
import os
import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv(override=True)

# Import enhanced components
from utils.logger import get_logger, logger
from utils.config import config
from utils.exceptions import QuoteWiseException, AgentExecutionError, PDFGenerationError
from utils.cache import cache, cached
from components.analytics import AnalyticsDashboard
from components.ui_components import ModernUIComponents
from components.styles import get_enhanced_css, get_analytics_css

# Import existing components
from crew import QuotationGeneratorAzure1
from tools.finalization_tool import PDFCreationTool

# Initialize logger
logger = get_logger("main_enhanced")

# Initialize components
analytics_dashboard = AnalyticsDashboard()
ui_components = ModernUIComponents()
pdf_tool = PDFCreationTool()

# Enhanced CSS
enhanced_css = get_enhanced_css()
analytics_css = get_analytics_css()

# Page configuration
st.set_page_config(
    page_title=config.ui.page_title,
    page_icon=config.ui.page_icon,
    layout=config.ui.layout,
    initial_sidebar_state=config.ui.sidebar_state
)

# Inject enhanced CSS
st.markdown(enhanced_css, unsafe_allow_html=True)

# Session state initialization
def initialize_session_state():
    """Initialize session state with enhanced structure."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "request_items" not in st.session_state:
        st.session_state.request_items = []
    
    if "is_waiting_for_approval" not in st.session_state:
        st.session_state.is_waiting_for_approval = False
    
    if "last_quote" not in st.session_state:
        st.session_state.last_quote = ""
    
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = ""
    
    if "quotation_history" not in st.session_state:
        st.session_state.quotation_history = []
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

# Enhanced date helper
@cached(ttl=3600)  # Cache for 1 hour
def get_dates():
    """Provides consistent dates for the crew kickoff with caching."""
    today = datetime(2025, 8, 1)
    end_date = today + timedelta(days=14)
    today_str = today.strftime("%B %d, %Y")
    end_date_str = end_date.strftime("%B %d, %Y")
    return today_str, end_date_str

# Enhanced crew execution with error handling
def run_crew_and_get_quote(request: str, placeholder) -> str:
    """
    Enhanced crew execution with comprehensive error handling and logging.
    """
    try:
        logger.info("Starting quotation generation process", request_length=len(request))
        
        # Enhanced loading messages with better UX
        loading_messages = [
            ("🔍 **Data Fetcher Agent:** Identifying products in your request...", 2, "🔍"),
            ("💰 **Pricing Strategy Agent:** Calculating initial prices...", 3, "💰"),
            ("📅 **Event Scout Agent:** Searching for relevant upcoming events...", 2, "📅"),
            ("📈 **Price Impact Analyst:** Analyzing event impact on pricing...", 2, "📈"),
            ("🛡️ **Approval Logic Agent:** Performing risk assessment on the quote...", 2, "🛡️"),
            ("✨ **Discount Strategist Agent:** Applying final strategic discounts...", 3, "✨"),
            ("📄 **Quotation Formatter Agent:** Generating the final document...", 2, "📄")
        ]
        
        for msg, delay, icon in loading_messages:
            ui_components.render_loading_animation(msg, icon)
            time.sleep(delay)
        
        ui_components.render_loading_animation("🤖 Finalizing... this may take a moment.", "🤖")
        
        # Execute crew with enhanced error handling
        start_time = time.time()
        today_str, end_date_str = get_dates()
        
        inputs = {
            'customer_requirements': request,
            'start_date': today_str,
            'end_date': end_date_str
        }
        
        logger.log_agent_activity("QuotationGenerator", "Starting crew execution")
        QuotationGeneratorAzure1().crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        logger.log_performance("Crew execution", execution_time)
        
        # Read and return the result
        output_file_path = os.path.join(config.get_output_directory(), 'report_agent_5.md')
        
        if not os.path.exists(output_file_path):
            raise FileNotFoundError(f"Output file not found: {output_file_path}")
        
        with open(output_file_path, 'r', encoding='utf-8') as f:
            quote_text = f.read()
        
        logger.info("Quotation generation completed successfully", 
                   execution_time=execution_time, 
                   output_length=len(quote_text))
        
        return quote_text
        
    except Exception as e:
        logger.error("Crew execution failed", exception=e, request=request)
        raise AgentExecutionError(
            f"Quotation generation failed: {str(e)}",
            error_code="CREW_EXECUTION_FAILED",
            context={"request": request, "error": str(e)}
        )

# Enhanced PDF generation with error handling
def finalize_approved_quote(quote_text: str) -> str:
    """Enhanced PDF generation with comprehensive error handling."""
    try:
        logger.info("Starting PDF generation", quote_length=len(quote_text))
        
        with st.spinner("🎨 Finalizing your approved quote and generating the PDF..."):
            result = pdf_tool.run(quote_text=quote_text)
            
            if "Successfully created PDF quote at: " in result:
                full_path = result.replace("✅ Successfully created PDF quote at: ", "").strip()
                st.session_state.pdf_path = full_path
                logger.info("PDF generation completed successfully", pdf_path=full_path)
            else:
                logger.warning("PDF generation may have issues", result=result)
            
            return f"**✅ PDF Generation Specialist:**\n\n{result}"
            
    except Exception as e:
        logger.error("PDF generation failed", exception=e, quote_text=quote_text[:100])
        raise PDFGenerationError(
            f"PDF generation failed: {str(e)}",
            error_code="PDF_GENERATION_FAILED",
            context={"quote_text": quote_text[:100], "error": str(e)}
        )

# Enhanced main application
def render_dashboard():
    """Render the main dashboard with analytics."""
    ui_components.render_enhanced_header()
    analytics_dashboard.render_dashboard()

def render_quotation_interface():
    """Render the quotation interface."""
    ui_components.render_enhanced_header()
    
    # Display features if no messages
    if len(st.session_state.messages) <= 1:
        ui_components.render_feature_showcase()
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
                st.markdown(message["content"])
                
                # Show PDF download button for approved quotes
                if message["role"] == "assistant" and "pdf_path" in message and message["pdf_path"]:
                    try:
                        with open(message["pdf_path"], "rb") as pdf_file:
                            st.download_button(
                                label="📥 Download Quote PDF",
                                data=pdf_file,
                                file_name=os.path.basename(message["pdf_path"]),
                                mime="application/pdf",
                                key=f"download_{i}"
                            )
                    except FileNotFoundError:
                        st.error("PDF file not found.")
    
    # Input section
    st.markdown("<br>", unsafe_allow_html=True)
    
    if prompt := st.chat_input("💬 What can I get for you today?"):
        try:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Create placeholder for loading
            status_placeholder = st.empty()
            
            if st.session_state.is_waiting_for_approval:
                if prompt.strip().lower() == "approve":
                    # Handle approval
                    st.session_state.is_waiting_for_approval = False
                    finalization_result = finalize_approved_quote(st.session_state.last_quote)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": finalization_result, 
                        "pdf_path": st.session_state.pdf_path
                    })
                    
                    # Add to quotation history
                    st.session_state.quotation_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "quote": st.session_state.last_quote,
                        "pdf_path": st.session_state.pdf_path
                    })
                    
                    # Reset for next request
                    st.session_state.request_items = []
                    st.session_state.last_quote = ""
                    
                else:
                    # Handle modification
                    st.session_state.is_waiting_for_approval = False
                    st.session_state.request_items.append(prompt)
                    
                    consolidated_request = "\n".join(st.session_state.request_items)
                    new_quote = run_crew_and_get_quote(consolidated_request, status_placeholder)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"**🤖 Quotation Bot:**\n\n{new_quote}\n\n✅ Here is the revised quote including all items. Please review and type **APPROVE** to finalize, or provide further modifications."
                    })
                    st.session_state.is_waiting_for_approval = True
                    
            else:
                # Handle new request
                st.session_state.request_items = [prompt]
                consolidated_request = "\n".join(st.session_state.request_items)
                
                quote = run_crew_and_get_quote(consolidated_request, status_placeholder)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"**🤖 Quotation Bot:**\n\n{quote}\n\n📋 Please review the quote above. Type **APPROVE** to finalize, or provide any modifications."
                })
                st.session_state.is_waiting_for_approval = True
                
        except QuoteWiseException as e:
            logger.error("Application error", exception=e, context=e.context)
            st.error(f"❌ {e.message}")
            if e.context:
                with st.expander("Error Details"):
                    st.json(e.context)
        except Exception as e:
            logger.error("Unexpected error", exception=e)
            st.error(f"❌ An unexpected error occurred: {str(e)}")
        finally:
            status_placeholder.empty()
            st.rerun()

# Main application logic
def main():
    """Main application entry point."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Render sidebar
        ui_components.render_enhanced_sidebar()
        
        # Page routing
        if st.session_state.current_page == "dashboard":
            render_dashboard()
        elif st.session_state.current_page == "quotation":
            render_quotation_interface()
        else:
            render_quotation_interface()
        
        # Initialize with welcome message
        if not st.session_state.messages:
            st.session_state.messages.append(
                {"role": "assistant", "content": "🎉 Welcome to the enhanced QuoteWise AI! I'm ready to help you create professional quotations with advanced analytics and improved user experience."}
            )
        
    except Exception as e:
        logger.critical("Application startup failed", exception=e)
        st.error("❌ Application failed to start. Please check the logs for details.")

if __name__ == "__main__":
    main()






