import streamlit as st
import pandas as pd

# Import our modular backend files
from database import DatabaseManager
from schema import get_live_schema
from classifier import classify_question
from llm import generate_sql, fix_sql, explain_sql, generate_narrative_insight, general_chat
from executor import execute_query
from chart_generator import generate_chart
from export import export_to_csv, export_to_excel, export_to_pdf
from history import init_history, add_history_entry, clear_history, get_history

# Page Configuration
st.set_page_config(
    page_title="AI SQL Analytics Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state history
init_history()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/database.png", width=64)
    st.title("SQL Analytics Hub")
    st.markdown("---")
    
    # 1. Database Connection Status Check
    db = DatabaseManager()
    connected, msg = db.test_connection()
    if connected:
        st.success("🟢 Database Connected")
    else:
        st.error(f"🔴 Connection Failed: {msg}")
        
    st.markdown("---")
    st.subheader("Query History")
    
    # Clear History Button
    if st.button("🗑️ Clear History", use_container_width=True):
        clear_history()
        st.rerun()
        
    # Render History List
    history_list = get_history()
    if not history_list:
        st.info("No queries recorded yet.")
    else:
        for idx, item in enumerate(history_list):
            case_badge = "⚡ Case A (SQL)" if item["case"] == "CASE_A" else "💬 Case B (Chat)"
            with st.expander(f"{case_badge}: {item['question'][:30]}..."):
                st.write(f"**Time:** {item['timestamp']}")
                st.write(f"**Question:** {item['question']}")
                if item["sql"]:
                    st.code(item["sql"], language="sql")
                    st.write(f"**Rows:** {item['row_count']} | **Exec Time:** {item['execution_time']}s")

# --- MAIN APP INTERFACE ---
st.title("📊 AI SQL Analytics Assistant")
st.markdown("Ask questions about your E-Commerce database or chat general questions. The assistant handles routing, schema grounding, dynamic SQL generation, and visualization automatically.")

# Suggested prompt examples for quick testing
st.markdown("💡 **Try asking things like:** *'Display products priced above 500'*, *'Calculate total revenue by category'*, or *'What is the capital of France?'*")

# User Input Form
with st.form("query_form"):
    user_query = st.text_input("Enter your question or query here:", placeholder="e.g., Show me all customers from Hyderabad")
    submitted = st.form_submit_button("Analyze & Run", type="primary")

if submitted and user_query.strip():
    with st.spinner("Analyzing question..."):
        # 1. Classify Question (Case A vs Case B)
        route, confidence = classify_question(user_query)
        
    # ==========================================
    # CASE B: Unrelated to Database (General Chat)
    # ==========================================
    if route == "CASE_B":
        st.info("ℹ️ **Case B Route:** Handled as a general assistant question (No database accessed).")
        with st.spinner("Generating response..."):
            answer = general_chat(user_query)
            
        st.markdown("### Assistant Response")
        st.write(answer)
        
        # Log to history
        add_history_entry(question=user_query, case="CASE_B")

    # ==========================================
    # CASE A: Database-related Question
    # ==========================================
    else:
        st.info(f"⚡ **Case A Route:** Database query identified (Confidence: {confidence:.2f}). Fetching live schema and generating SQL...")
        
        # Fetch live schema dynamically
        live_schema = get_live_schema()
        
        # Step 1: Generate SQL
        with st.spinner("Generating SQL query..."):
            sql = generate_sql(user_query, live_schema)
            
        st.markdown("### Generated SQL")
        st.code(sql, language="sql")
        
        # Step 2: Execute SQL with Self-Correction Retry Loop (up to 2 retries)
        df = None
        row_count = 0
        execution_time = 0.0
        error_msg = None
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            with st.spinner(f"Executing SQL query (Attempt {attempt + 1}/{max_retries + 1})..."):
                df, row_count, execution_time, error_msg = execute_query(sql)
                
            if error_msg is None:
                break # Success!
            else:
                if attempt < max_retries:
                    with st.spinner(f"Query failed with error. Attempting self-correction retry ({attempt + 1}/{max_retries})..."):
                        sql = fix_sql(user_query, live_schema, sql, error_msg)
                        st.warning(f"⚠️ Retry {attempt + 1}: Fixed SQL generated based on error: `{error_msg}`")
                else:
                    st.error(f"❌ Query execution failed after {max_retries} retry attempts.")
                    st.error(f"Final Error: {error_msg}")

        # If execution succeeded successfully
        if error_msg is None and df is not None:
            st.success(f"Query executed successfully in {execution_time} seconds! Returned {row_count} rows.")
            
            # Display Results Table
            st.markdown("### Result Data")
            st.dataframe(df, use_container_width=True)
            
            # Sidebar / Toggle Options for Explanation & Insight
            col_opt1, col_opt2 = st.columns(2)
            show_explanation = col_opt1.checkbox("Show Plain-English Explanation", value=True)
            show_insight = col_opt2.checkbox("Show Narrative Business Insight", value=True)
            
            if show_explanation:
                with st.spinner("Generating explanation..."):
                    explanation = explain_sql(sql)
                    st.info(f"📝 **Explanation:** {explanation}")
                    
            if show_insight and not df.empty:
                with st.spinner("Generating business insight..."):
                    sample_str = df.head(5).to_string(index=False)
                    insight = generate_narrative_insight(user_query, sample_str)
                    st.success(f"💡 **Business Insight:** {insight}")

            # Auto-Generated Charts
            with st.spinner("Generating visualizations..."):
                fig = generate_chart(df)
                if fig is not None:
                    st.markdown("### Visual Analytics")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = None # Explicitly set to None for PDF export if unchartable

            # Download Options
            st.markdown("### Export Results")
            dl_col1, dl_col2, dl_col3 = st.columns(3)
            
            csv_bytes = export_to_csv(df)
            excel_bytes = export_to_excel(df)
            pdf_bytes = export_to_pdf(user_query, sql, df, fig)
            
            dl_col1.download_button("📥 Download CSV", data=csv_bytes, file_name="query_results.csv", mime="text/csv", use_container_width=True)
            dl_col2.download_button("📊 Download Excel", data=excel_bytes, file_name="query_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            dl_col3.download_button("📑 Download PDF Report", data=pdf_bytes, file_name="analytics_report.pdf", mime="application/pdf", use_container_width=True)

            # Log successful query to history
            add_history_entry(question=user_query, case="CASE_A", sql=sql, row_count=row_count, execution_time=execution_time)
        else:
            # Log failed query to history
            add_history_entry(question=user_query, case="CASE_A", sql=sql, row_count=0, execution_time=execution_time)