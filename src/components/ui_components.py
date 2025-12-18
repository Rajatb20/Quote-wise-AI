"""
Enhanced UI components for QuoteWise AI.
Provides modern, responsive UI components with better UX.
"""

import streamlit as st
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json

from ..utils.logger import get_logger
from ..utils.config import config

logger = get_logger("ui_components")


class ModernUIComponents:
    """Modern UI components for enhanced user experience."""
    
    def __init__(self):
        self.session_state = st.session_state
    
    def render_enhanced_header(self):
        """Render enhanced header with animations."""
        st.markdown("""
        <div class="enhanced-header">
            <div class="header-content">
                <h1 class="main-title">
                    <span class="title-icon">🚀</span>
                    QuoteWise AI
                </h1>
                <p class="subtitle">Intelligent Quotation Generation Platform</p>
                <div class="status-indicator">
                    <span class="status-dot"></span>
                    <span class="status-text">System Online</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_feature_showcase(self):
        """Render feature showcase cards."""
        features = [
            {
                "icon": "🎯",
                "title": "Smart Pricing",
                "description": "AI-powered pricing with market intelligence",
                "color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            },
            {
                "icon": "📊",
                "description": "Real-time Analytics",
                "description": "Comprehensive business intelligence",
                "color": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            },
            {
                "icon": "📄",
                "description": "Instant PDF",
                "description": "Professional document generation",
                "color": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            },
            {
                "icon": "🛡️",
                "description": "Risk Assessment",
                "description": "Automated risk evaluation",
                "color": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            }
        ]
        
        cols = st.columns(2)
        for i, feature in enumerate(features):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="feature-card" style="background: {feature['color']};">
                    <div class="feature-icon">{feature['icon']}</div>
                    <h3 class="feature-title">{feature['title']}</h3>
                    <p class="feature-description">{feature['description']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def render_quotation_wizard(self):
        """Render step-by-step quotation wizard."""
        if 'wizard_step' not in self.session_state:
            self.session_state.wizard_step = 1
        
        steps = [
            {"number": 1, "title": "Product Selection", "icon": "🛍️"},
            {"number": 2, "title": "Quantity & Specs", "icon": "📝"},
            {"number": 3, "title": "Pricing Review", "icon": "💰"},
            {"number": 4, "title": "Final Approval", "icon": "✅"}
        ]
        
        # Progress bar
        progress = self.session_state.wizard_step / len(steps)
        st.progress(progress)
        
        # Step indicators
        cols = st.columns(len(steps))
        for i, step in enumerate(steps):
            with cols[i]:
                is_active = i + 1 == self.session_state.wizard_step
                is_completed = i + 1 < self.session_state.wizard_step
                
                status_class = "active" if is_active else ("completed" if is_completed else "pending")
                
                st.markdown(f"""
                <div class="wizard-step {status_class}">
                    <div class="step-number">{step['number']}</div>
                    <div class="step-icon">{step['icon']}</div>
                    <div class="step-title">{step['title']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_enhanced_input(self, label: str, placeholder: str = "", help_text: str = ""):
        """Render enhanced input with better styling."""
        return st.text_area(
            label=label,
            placeholder=placeholder,
            help=help_text,
            height=100,
            key=f"enhanced_input_{label}"
        )
    
    def render_quotation_preview(self, quotation_data: Dict[str, Any]):
        """Render quotation preview with enhanced styling."""
        st.subheader("📋 Quotation Preview")
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Items",
                value=quotation_data.get('total_items', 0)
            )
        
        with col2:
            st.metric(
                label="Total Value",
                value=f"₹{quotation_data.get('total_value', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                label="Discount Applied",
                value=f"{quotation_data.get('discount_percentage', 0):.1f}%"
            )
        
        # Quotation details
        if 'items' in quotation_data:
            st.subheader("📦 Quotation Items")
            
            for item in quotation_data['items']:
                with st.expander(f"📦 {item.get('name', 'Unknown Product')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Quantity:** {item.get('quantity', 0)}")
                        st.write(f"**Unit Price:** ₹{item.get('unit_price', 0):.2f}")
                    
                    with col2:
                        st.write(f"**Discount:** {item.get('discount', 0):.1f}%")
                        st.write(f"**Total:** ₹{item.get('total', 0):.2f}")
                    
                    with col3:
                        if item.get('status') == 'Available':
                            st.success("✅ Available")
                        else:
                            st.error(f"❌ {item.get('status', 'Unavailable')}")
    
    def render_loading_animation(self, message: str, icon: str = "⏳"):
        """Render enhanced loading animation."""
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown(f"""
            <div class="loading-container">
                <div class="loading-spinner">
                    <div class="spinner"></div>
                </div>
                <div class="loading-text">
                    <span class="loading-icon">{icon}</span>
                    <span class="loading-message">{message}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return placeholder
    
    def render_success_message(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Render success message with details."""
        st.success(f"✅ {message}")
        
        if details:
            with st.expander("📋 Details"):
                for key, value in details.items():
                    st.write(f"**{key}:** {value}")
    
    def render_error_message(self, error: str, suggestions: Optional[List[str]] = None):
        """Render error message with suggestions."""
        st.error(f"❌ {error}")
        
        if suggestions:
            st.info("💡 Suggestions:")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")
    
    def render_quotation_history(self):
        """Render quotation history with enhanced UI."""
        st.subheader("📚 Quotation History")
        
        # Mock data for demonstration
        history_data = [
            {
                "id": "QT-001",
                "date": "2024-01-15",
                "customer": "ABC Corp",
                "total": 125000,
                "status": "Approved"
            },
            {
                "id": "QT-002", 
                "date": "2024-01-14",
                "customer": "XYZ Ltd",
                "total": 89000,
                "status": "Pending"
            }
        ]
        
        for quote in history_data:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{quote['id']}**")
                
                with col2:
                    st.write(quote['date'])
                
                with col3:
                    st.write(quote['customer'])
                
                with col4:
                    st.write(f"₹{quote['total']:,.2f}")
                
                with col5:
                    if quote['status'] == 'Approved':
                        st.success("✅")
                    else:
                        st.warning("⏳")
    
    def render_export_options(self, quotation_data: Dict[str, Any]):
        """Render export options for quotations."""
        st.subheader("📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export PDF", key="export_pdf"):
                st.success("PDF export initiated!")
        
        with col2:
            if st.button("📊 Export Excel", key="export_excel"):
                st.success("Excel export initiated!")
        
        with col3:
            if st.button("📧 Email Quote", key="email_quote"):
                st.success("Email sent!")
    
    def render_enhanced_sidebar(self):
        """Render enhanced sidebar with navigation."""
        with st.sidebar:
            st.markdown("### 🎯 Navigation")
            
            pages = [
                {"name": "🏠 Dashboard", "icon": "🏠"},
                {"name": "📝 New Quotation", "icon": "📝"},
                {"name": "📊 Analytics", "icon": "📊"},
                {"name": "📚 History", "icon": "📚"},
                {"name": "⚙️ Settings", "icon": "⚙️"}
            ]
            
            for page in pages:
                st.markdown(f"""
                <div class="sidebar-item">
                    <span class="sidebar-icon">{page['icon']}</span>
                    <span class="sidebar-text">{page['name']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 📈 Quick Stats")
            st.metric("Quotations Today", "12", "3")
            st.metric("Total Value", "₹2.5M", "15%")
            
            st.markdown("---")
            
            st.markdown("### 🔧 System Status")
            st.success("🟢 All Systems Operational")
            st.info("📊 Analytics Updated")
            st.warning("⚠️ 3 Items Low Stock")

