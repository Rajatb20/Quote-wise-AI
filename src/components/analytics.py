"""
Analytics dashboard components for QuoteWise AI.
Provides charts, KPIs, and business intelligence features.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path

from ..utils.logger import get_logger
from ..utils.config import config

logger = get_logger("analytics")


class AnalyticsDashboard:
    """Main analytics dashboard class."""
    
    def __init__(self):
        self.data_dir = Path("src/data")
        self.outputs_dir = Path("src/outputs")
        self.final_quotes_dir = Path("final_quotes")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        for directory in [self.data_dir, self.outputs_dir, self.final_quotes_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_quotation_history(self) -> List[Dict[str, Any]]:
        """Get quotation history from output files."""
        quotations = []
        
        try:
            # Read from outputs directory
            for file_path in self.outputs_dir.glob("report_agent_*.md"):
                if file_path.name == "report_agent_5.md":  # Final quotation
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        quotations.append({
                            'file': file_path.name,
                            'content': content,
                            'created_at': file_path.stat().st_mtime,
                            'type': 'quotation'
                        })
        except Exception as e:
            logger.error(f"Error reading quotation history: {e}")
        
        return quotations
    
    def get_inventory_analytics(self) -> Dict[str, Any]:
        """Get inventory analytics from CSV data."""
        try:
            csv_path = config.get_database_path()
            df = pd.read_csv(csv_path)
            
            # Basic inventory metrics
            total_products = len(df)
            in_stock = len(df[df['Stock Status'] == 'In Stock'])
            out_of_stock = len(df[df['Stock Status'] == 'Out of Stock'])
            
            # Category distribution
            category_dist = df['Category'].value_counts().to_dict()
            
            # Stock value analysis
            df['Stock Value'] = df['Quantity in Stock'] * df['Min. Selling Price (Rs)']
            total_stock_value = df['Stock Value'].sum()
            
            # Low stock items (below reorder level)
            low_stock = df[df['Quantity in Stock'] <= df['Reorder Level']]
            
            return {
                'total_products': total_products,
                'in_stock': in_stock,
                'out_of_stock': out_of_stock,
                'stock_availability_rate': (in_stock / total_products) * 100,
                'category_distribution': category_dist,
                'total_stock_value': total_stock_value,
                'low_stock_items': len(low_stock),
                'low_stock_list': low_stock[['Product Name', 'Quantity in Stock', 'Reorder Level']].to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error getting inventory analytics: {e}")
            return {}
    
    def render_kpi_cards(self):
        """Render KPI cards for the dashboard."""
        analytics = self.get_inventory_analytics()
        
        if not analytics:
            st.error("Unable to load analytics data")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Products",
                value=analytics.get('total_products', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="In Stock",
                value=analytics.get('in_stock', 0),
                delta=f"{analytics.get('stock_availability_rate', 0):.1f}%"
            )
        
        with col3:
            st.metric(
                label="Stock Value",
                value=f"₹{analytics.get('total_stock_value', 0):,.0f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Low Stock Items",
                value=analytics.get('low_stock_items', 0),
                delta="Need Reorder" if analytics.get('low_stock_items', 0) > 0 else None
            )
    
    def render_category_chart(self):
        """Render category distribution chart."""
        analytics = self.get_inventory_analytics()
        category_dist = analytics.get('category_distribution', {})
        
        if not category_dist:
            st.warning("No category data available")
            return
        
        # Create pie chart
        fig = px.pie(
            values=list(category_dist.values()),
            names=list(category_dist.keys()),
            title="Product Distribution by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_stock_status_chart(self):
        """Render stock status distribution chart."""
        analytics = self.get_inventory_analytics()
        
        if not analytics:
            return
        
        # Create stock status chart
        status_data = {
            'In Stock': analytics.get('in_stock', 0),
            'Out of Stock': analytics.get('out_of_stock', 0)
        }
        
        fig = px.bar(
            x=list(status_data.keys()),
            y=list(status_data.values()),
            title="Stock Status Distribution",
            color=list(status_data.keys()),
            color_discrete_map={'In Stock': '#2E8B57', 'Out of Stock': '#DC143C'}
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Stock Status",
            yaxis_title="Number of Products"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_low_stock_table(self):
        """Render low stock items table."""
        analytics = self.get_inventory_analytics()
        low_stock_list = analytics.get('low_stock_list', [])
        
        if not low_stock_list:
            st.success("No low stock items found!")
            return
        
        st.subheader("🚨 Low Stock Items")
        
        df = pd.DataFrame(low_stock_list)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    
    def render_quotation_analytics(self):
        """Render quotation analytics."""
        quotations = self.get_quotation_history()
        
        if not quotations:
            st.info("No quotations generated yet")
            return
        
        st.subheader("📊 Quotation Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Total Quotations",
                value=len(quotations),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Latest Quotation",
                value=datetime.fromtimestamp(quotations[0]['created_at']).strftime('%Y-%m-%d %H:%M') if quotations else "N/A",
                delta=None
            )
    
    def render_dashboard(self):
        """Render the complete analytics dashboard."""
        st.title("📊 QuoteWise AI Analytics Dashboard")
        st.markdown("---")
        
        # KPI Cards
        st.subheader("📈 Key Performance Indicators")
        self.render_kpi_cards()
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_category_chart()
        
        with col2:
            self.render_stock_status_chart()
        
        st.markdown("---")
        
        # Low Stock Items
        self.render_low_stock_table()
        
        st.markdown("---")
        
        # Quotation Analytics
        self.render_quotation_analytics()
    
    def export_analytics_report(self) -> str:
        """Export analytics data as JSON report."""
        analytics = self.get_inventory_analytics()
        quotations = self.get_quotation_history()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'inventory_analytics': analytics,
            'quotation_count': len(quotations),
            'report_generated_by': 'QuoteWise AI Analytics'
        }
        
        return json.dumps(report, indent=2, default=str)

