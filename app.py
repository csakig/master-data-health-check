import streamlit as st
import pandas as pd
import io
import re

# ---------------------------------------------------------
# 1. CONFIGURATION & STYLE
# ---------------------------------------------------------
st.set_page_config(page_title="Data Health Check Tool", page_icon="🔍", layout="wide")

# Custom CSS for better metric visibility in both Dark/Light modes
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# APP TITLE
st.title("🔍 Master Data Health Check Tool")
st.markdown("Automated data quality validation system (PoC) for enterprise migration projects.")

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------

def validate_email(email):
    """Validates email format using Regex."""
    if pd.isna(email) or email == "":
        return False
    # Standard email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None

def to_excel(df):
    """Converts dataframe to Excel in memory for download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Validation_Errors')
    processed_data = output.getvalue()
    return processed_data

# ---------------------------------------------------------
# 3. SIDEBAR & INPUT
# ---------------------------------------------------------
st.sidebar.header("🎛️ Control Panel")
uploaded_file = st.sidebar.file_uploader("Upload Raw Data (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file)
        
        # --- INTERACTIVE FILTER ---
        all_countries = df['Country'].unique().tolist()
        selected_countries = st.sidebar.multiselect(
            "Filter by Country:",
            options=all_countries,
            default=all_countries
        )
        
        # Apply Filter
        filtered_df = df[df['Country'].isin(selected_countries)]
        
        st.success(f"Dataset loaded: {len(df)} rows (Active Filter: {len(filtered_df)} rows)")

        # ---------------------------------------------------------
        # 4. VALIDATION ENGINE
        # ---------------------------------------------------------
        st.divider()
        st.subheader("📊 Real-time Analysis")

        # Check 1: Invalid or Missing Email
        filtered_df['Email_Valid'] = filtered_df['Email'].apply(validate_email)
        bad_emails = filtered_df[~filtered_df['Email_Valid']]
        
        # Check 2: Duplicated ID
        duplicate_ids = filtered_df[filtered_df.duplicated(subset=['Partner_ID'], keep=False)]
        
        # Check 3: Invalid VAT Number (length check)
        bad_vat = filtered_df[filtered_df['VAT_Number'].astype(str).str.len() < 5]

        # Consolidate Error Rows
        error_indices = set(bad_emails.index) | set(duplicate_ids.index) | set(bad_vat.index)
        all_bad_rows = filtered_df.loc[list(error_indices)]

        # KPI Panel
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows Scanned", len(filtered_df))
        c2.metric("Invalid Emails", len(bad_emails), delta_color="inverse", delta=f"-{len(bad_emails)}" if len(bad_emails)>0 else "OK")
        c3.metric("Duplicate IDs", len(duplicate_ids), delta_color="inverse", delta=f"-{len(duplicate_ids)}" if len(duplicate_ids)>0 else "OK")
        c4.metric("Critical Errors", len(all_bad_rows), delta_color="inverse", delta=f"-{len(all_bad_rows)}" if len(all_bad_rows)>0 else "Perfect")

        # ---------------------------------------------------------
        # 5. VISUALIZATION & TABLE
        # ---------------------------------------------------------
        if len(all_bad_rows) > 0:
            st.divider()
            
            # --- CHART ---
            st.subheader("1. Error Distribution")
            error_stats = pd.DataFrame({
                'Error Type': ['Invalid Email', 'Duplicate ID', 'Suspicious VAT'],
                'Count': [len(bad_emails), len(duplicate_ids), len(bad_vat)]
            })
            st.bar_chart(error_stats.set_index('Error Type'), height=300)

            st.divider()

            # --- DETAILED TABLE ---
            st.subheader(f"2. Detailed Error List ({len(all_bad_rows)} rows)")
            st.info("💡 Cells highlighted in red require attention.")

            # SMART HIGHLIGHT FUNCTION
            def highlight_cells(row):
                styles = [''] * len(row)
                
                # Email Logic
                if not validate_email(row['Email']):
                    email_idx = row.index.get_loc('Email')
                    styles[email_idx] = 'background-color: #ff4b4b; color: white'
                
                # ID Logic
                if row['Partner_ID'] in duplicate_ids['Partner_ID'].values:
                     id_idx = row.index.get_loc('Partner_ID')
                     styles[id_idx] = 'background-color: #ff4b4b; color: white'

                # VAT Logic
                vat_val = str(row['VAT_Number'])
                if len(vat_val) < 5 or vat_val == 'nan':
                     vat_idx = row.index.get_loc('VAT_Number')
                     styles[vat_idx] = 'background-color: #ff4b4b; color: white'
                
                return styles

            # Display Table
            st.dataframe(
                all_bad_rows.head(100).style.apply(highlight_cells, axis=1), 
                use_container_width=True,
                height=500 
            )

            # ---------------------------------------------------------
            # 6. EXPORT BUTTON
            # ---------------------------------------------------------
            st.warning(f"⚠️ You can export {len(all_bad_rows)} rows for correction.")
            
            excel_data = to_excel(all_bad_rows)
            st.download_button(
                label="📥 Download Error Report (.xlsx)",
                data=excel_data,
                file_name="Data_Quality_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.success("🎉 Congratulations! Data is clean and ready for migration.")
            st.balloons()

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

else:
    st.info("👈 Please upload your raw data (.xlsx) using the sidebar to start.")