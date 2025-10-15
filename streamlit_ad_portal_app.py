"""
Streamlit Active Directory (Excel-backed) - app.py

Features:
- Uses an Excel workbook with two sheets: 'Employees' and 'Departments'
- CRUD for Employees and Departments (Add / Update / Delete)
- Search & filters for every column
- Toggle user Active/Inactive
- Export filtered results to CSV / Excel
- Basic dashboard metrics
- Local, offline, single-file Streamlit app

How to run:
1. Create a virtualenv and install requirements:
   pip install -r requirements.txt
   (requirements.txt should include: streamlit, pandas, openpyxl, python-multipart)

2. Run the app locally:
   streamlit run streamlit_ad_portal_app.py

Notes:
- The app will create `employees.xlsx` in the working directory if it doesn't exist.
- Excel writes are atomic: it writes to a temp file then replaces the original.
- This is intended as a lightweight admin tool — not a replacement for a secure AD.
"""

import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime
from io import BytesIO
import time

# --------------------------- Configuration ---------------------------
EXCEL_PATH = "employees.xlsx"
EMP_SHEET = "Employees"
DEPT_SHEET = "Departments"

# Default columns for employees sheet
EMP_COLUMNS = [
    "Row ID",      # Auto-generated internal ID
    "Employee ID",  # User-provided, required
    "Name",
    "Extension",   # 4-digit
    "Department",
    "Cell Number",
    "Location",
    "Status",      # Active / Inactive
    "Notes",
    "Last Updated"
]

DEPT_COLUMNS = ["Dept ID", "Department Name", "Description"]

# --------------------------- Utility Functions ---------------------------

def ensure_workbook(path: str):
    """Ensure base Excel workbook exists with required sheets."""
    if not os.path.exists(path):
        st.warning(f"Excel file not found — creating new workbook at {path}")
        df_emp = pd.DataFrame(columns=EMP_COLUMNS)
        df_dept = pd.DataFrame(columns=DEPT_COLUMNS)
        write_workbook(path, df_emp, df_dept)


def read_workbook(path: str):
    """Read Employees and Departments into DataFrames."""
    try:
        xls = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    except FileNotFoundError:
        ensure_workbook(path)
        xls = pd.read_excel(path, sheet_name=None, engine="openpyxl")

    df_emp = xls.get(EMP_SHEET, pd.DataFrame(columns=EMP_COLUMNS))
    df_dept = xls.get(DEPT_SHEET, pd.DataFrame(columns=DEPT_COLUMNS))

    # Normalize columns if missing and ensure string types
    for c in EMP_COLUMNS:
        if c not in df_emp.columns:
            df_emp[c] = ""
    for c in DEPT_COLUMNS:
        if c not in df_dept.columns:
            df_dept[c] = ""
    
    # Ensure department columns are string type to prevent dtype warnings
    if not df_dept.empty:
        df_dept["Department Name"] = df_dept["Department Name"].astype(str)
        df_dept["Description"] = df_dept["Description"].astype(str).replace('nan', '')
    
    # Ensure all employees have Row IDs
    if not df_emp.empty:
        # Fill missing Row IDs
        missing_ids = df_emp["Row ID"].isna() | (df_emp["Row ID"] == "") | (df_emp["Row ID"] == "nan")
        if missing_ids.any():
            max_id = 0
            existing_ids = df_emp.loc[~missing_ids, "Row ID"]
            if not existing_ids.empty:
                try:
                    max_id = int(existing_ids.max())
                except:
                    max_id = 0
            
            # Assign Row IDs to rows that don't have them
            for idx in df_emp[missing_ids].index:
                max_id += 1
                df_emp.at[idx, "Row ID"] = max_id
    
    # Ensure Dept ID is consistent string type
    if not df_dept.empty:
        df_dept["Dept ID"] = df_dept["Dept ID"].astype(str)

    return df_emp[EMP_COLUMNS].copy(), df_dept[DEPT_COLUMNS].copy()


def write_workbook(path: str, df_emp: pd.DataFrame, df_dept: pd.DataFrame):
    """Write two sheets to an Excel workbook atomically."""
    # Ensure consistent data types before writing
    df_emp_copy = df_emp.copy()
    df_dept_copy = df_dept.copy()
    
    # Convert Row ID to int where possible, keep as string otherwise
    if "Row ID" in df_emp_copy.columns:
        df_emp_copy["Row ID"] = df_emp_copy["Row ID"].astype(str)
    
    # Ensure Dept ID is string
    if "Dept ID" in df_dept_copy.columns:
        df_dept_copy["Dept ID"] = df_dept_copy["Dept ID"].astype(str)
    
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    with pd.ExcelWriter(tmp.name, engine="openpyxl") as writer:
        df_emp_copy.to_excel(writer, sheet_name=EMP_SHEET, index=False)
        df_dept_copy.to_excel(writer, sheet_name=DEPT_SHEET, index=False)
    tmp.close()
    os.replace(tmp.name, path)


def next_row_id(df_emp: pd.DataFrame):
    """Generate next Row ID (auto-increment internal ID)."""
    if df_emp.empty or "Row ID" not in df_emp.columns:
        return 1
    existing = df_emp["Row ID"].dropna()
    if existing.empty:
        return 1
    try:
        return int(existing.max()) + 1
    except Exception:
        return len(df_emp) + 1


def next_dept_id(df_dept: pd.DataFrame):
    existing = df_dept["Dept ID"].dropna().astype(str).str.extract(r"(\d+)")[0]
    if existing is None or existing.dropna().empty:
        return "1"
    try:
        return str(existing.dropna().astype(int).max() + 1)
    except Exception:
        return str(len(df_dept) + 1)


# --------------------------- Streamlit UI ---------------------------

st.set_page_config(page_title="Excel Active Directory Portal", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.85);
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    .stButton>button {
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .edit-btn {
        background-color: #4CAF50;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        font-size: 12px;
    }
    .delete-btn {
        background-color: #f44336;
        color: white;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🔐 Excel Active Directory Portal</h1><p style="font-size: 0.9em; opacity: 0.8; margin-top: 0.5rem;">Enterprise User & Department Management System</p></div>', unsafe_allow_html=True)

# Ensure workbook exists
ensure_workbook(EXCEL_PATH)

# Initialize session state
if 'df_emp' not in st.session_state or 'df_dept' not in st.session_state:
    st.session_state.df_emp, st.session_state.df_dept = read_workbook(EXCEL_PATH)
    # Save back if we added Row IDs
    if not st.session_state.df_emp.empty:
        write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
    
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
    st.session_state.edit_id = None
    st.session_state.scroll_to_edit = False

# Initialize pagination
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    
if 'rows_per_page' not in st.session_state:
    st.session_state.rows_per_page = 10

if 'show_bulk_upload' not in st.session_state:
    st.session_state.show_bulk_upload = False

if 'bulk_upload_df' not in st.session_state:
    st.session_state.bulk_upload_df = None

if 'bulk_mapping' not in st.session_state:
    st.session_state.bulk_mapping = {}

if 'bulk_defaults' not in st.session_state:
    st.session_state.bulk_defaults = {}

if 'bulk_dept_actions' not in st.session_state:
    st.session_state.bulk_dept_actions = {}

if 'missing_depts_handled' not in st.session_state:
    st.session_state.missing_depts_handled = False

if 'show_dept_sync' not in st.session_state:
    st.session_state.show_dept_sync = False

if 'sync_dept_actions' not in st.session_state:
    st.session_state.sync_dept_actions = {}

if 'show_dept_manage' not in st.session_state:
    st.session_state.show_dept_manage = False

if 'dept_manage_actions' not in st.session_state:
    st.session_state.dept_manage_actions = {}

# Read data from session state
df_emp = st.session_state.df_emp
df_dept = st.session_state.df_dept

# Sidebar: Controls
st.sidebar.header("⚙️ Controls & Actions")
if st.sidebar.button("🔄 Reload from Excel", width="stretch"):
    st.session_state.df_emp, st.session_state.df_dept = read_workbook(EXCEL_PATH)
    st.rerun()

if st.sidebar.button("💾 Save to Excel", width="stretch"):
    write_workbook(EXCEL_PATH, df_emp, df_dept)
    st.sidebar.success("✅ Saved to Excel.")

# Bulk operations
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Bulk Actions")
if st.sidebar.button("🔄 Activate All Inactive", width="stretch", help="Set all inactive users to active"):
    inactive_count = len(st.session_state.df_emp[st.session_state.df_emp['Status'] == 'Inactive'])
    if inactive_count > 0:
        st.session_state.df_emp.loc[st.session_state.df_emp['Status'] == 'Inactive', 'Status'] = 'Active'
        st.session_state.df_emp.loc[st.session_state.df_emp['Status'] == 'Active', 'Last Updated'] = datetime.utcnow().isoformat()
        write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
        st.sidebar.success(f"✅ Activated {inactive_count} user(s)")
        st.rerun()
    else:
        st.sidebar.info("No inactive users found")

if st.sidebar.button("📧 Export User List (CSV)", width="stretch", help="Download complete user list"):
    csv_data = st.session_state.df_emp.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        "⬇️ Download CSV",
        csv_data,
        file_name=f"user_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        width="stretch"
    )

if st.sidebar.button("📥 Bulk Upload Users", width="stretch", help="Import multiple users from Excel/CSV"):
    st.session_state.show_bulk_upload = True
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Sync Departments", width="stretch", help="Review and sync departments from employee records"):
    st.session_state.show_dept_sync = True
    st.rerun()

if st.sidebar.button("✏️ Manage Departments", width="stretch", help="View, rename, merge or delete existing departments"):
    st.session_state.show_dept_manage = True
    st.rerun()

# Quick stats with styled metrics
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")
total_users = len(df_emp)
active_users = len(df_emp[df_emp['Status'] == 'Active'])
inactive_users = len(df_emp[df_emp['Status'] == 'Inactive'])

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    st.metric("Total Users", total_users)
    st.metric("Active", active_users)
with col_s2:
    st.metric("Departments", len(df_dept))
    st.metric("Inactive", inactive_users)

# Search & Filter area
st.sidebar.markdown("---")
st.sidebar.header("🔍 Search & Filters")

# Clear Filters button at the top
if st.sidebar.button("🔄 Clear All Filters", width="stretch", help="Reset all search filters"):
    # Clear by using unique keys that will reset
    if 'clear_filters_counter' not in st.session_state:
        st.session_state.clear_filters_counter = 0
    st.session_state.clear_filters_counter += 1
    st.rerun()

# Use counter to reset widgets
if 'clear_filters_counter' not in st.session_state:
    st.session_state.clear_filters_counter = 0

filter_key_suffix = f"_{st.session_state.clear_filters_counter}"

# Use session state for search with debouncing
if 'search_name' not in st.session_state:
    st.session_state.search_name = ""
if 'search_ext' not in st.session_state:
    st.session_state.search_ext = ""
if 'search_empid' not in st.session_state:
    st.session_state.search_empid = ""
if 'search_loc' not in st.session_state:
    st.session_state.search_loc = ""
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()

name_filter = st.sidebar.text_input("Name contains", key=f"name_filter_input{filter_key_suffix}")
ext_filter = st.sidebar.text_input("Extension", key=f"ext_filter_input{filter_key_suffix}")
empid_filter = st.sidebar.text_input("Employee ID", key=f"empid_filter_input{filter_key_suffix}")
loc_filter = st.sidebar.text_input("Location contains", key=f"loc_filter_input{filter_key_suffix}")
status_filter = st.sidebar.selectbox("Status", options=["Any", "Active", "Inactive"], index=0, key=f"status_filter{filter_key_suffix}")

# Department filter with multiselect
# Re-read Departments from the saved workbook to ensure options reflect persisted data only
try:
    _wl_emp, _wl_dept = read_workbook(EXCEL_PATH)
    persisted_dept_names = _wl_dept["Department Name"].dropna().astype(str).str.strip().unique().tolist()
except Exception:
    persisted_dept_names = df_dept["Department Name"].dropna().astype(str).str.strip().unique().tolist()

dept_options = sorted([d for d in persisted_dept_names if d and d != 'nan'])
selected_depts = st.sidebar.multiselect("Department", options=dept_options, key=f"dept_filter{filter_key_suffix}")

# Main layout: two columns
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📋 Employee Directory")

    # Apply filters
    df_view = df_emp.copy()
    if name_filter:
        df_view = df_view[df_view["Name"].str.contains(name_filter, case=False, na=False)]
    if ext_filter := ext_filter.strip():
        df_view = df_view[df_view["Extension"].astype(str).str.contains(ext_filter, na=False)]
    if empid_filter:
        df_view = df_view[df_view["Employee ID"].astype(str).str.contains(empid_filter, na=False)]
    if loc_filter:
        df_view = df_view[df_view["Location"].str.contains(loc_filter, case=False, na=False)]
    if status_filter != "Any":
        df_view = df_view[df_view["Status"] == status_filter]
    if selected_depts:
        df_view = df_view[df_view["Department"].isin(selected_depts)]

    # Global search bar at top with clear button
    col_quick1, col_quick2 = st.columns([4, 1])
    with col_quick1:
        st.markdown("**🔎 Quick Search (searches all columns)**")
        if 'clear_all_counter' not in st.session_state:
            st.session_state.clear_all_counter = 0
        global_search = st.text_input("Type to search across all fields...", key=f"global_search_{st.session_state.clear_all_counter}", label_visibility="collapsed", placeholder="Search all columns...")
    with col_quick2:
        st.markdown("&nbsp;")  # Spacing to align with search box
        if st.button("🔄 Clear All", help="Clear all filters and searches"):
            st.session_state.clear_filters_counter = st.session_state.get('clear_filters_counter', 0) + 1
            st.session_state.clear_all_counter = st.session_state.get('clear_all_counter', 0) + 1
            st.rerun()
    
    if global_search:
        # Search across all string columns
        mask = df_view.apply(lambda row: row.astype(str).str.contains(global_search, case=False, na=False).any(), axis=1)
        df_view = df_view[mask]

    # Pagination controls
    total_rows = len(df_view)
    rows_per_page = st.session_state.rows_per_page
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)
    
    # Show count with styled badge
    st.markdown(f"**Showing {len(df_view)} of {len(df_emp)} employees**")
    
    # Pagination selector
    col_pag1, col_pag2, col_pag3, col_pag4, col_pag5, col_pag6 = st.columns([1, 2, 0.8, 0.8, 0.8, 0.8])
    with col_pag1:
        rows_per_page = st.selectbox("Rows per page:", [5, 10, 20, 50, 100], 
                                      index=[5, 10, 20, 50, 100].index(st.session_state.rows_per_page),
                                      key="rows_selector")
        st.session_state.rows_per_page = rows_per_page
    
    with col_pag2:
        st.write(f"Page {st.session_state.page_number + 1} of {total_pages}")
    
    # Reset to first page if out of bounds or negative
    if st.session_state.page_number >= total_pages:
        st.session_state.page_number = max(0, total_pages - 1)
    if st.session_state.page_number < 0:
        st.session_state.page_number = 0
    
    with col_pag3:
        if st.button("⏮️ First", disabled=(st.session_state.page_number == 0)):
            st.session_state.page_number = 0
            st.rerun()
    
    with col_pag4:
        if st.button("⬅️ Prev", disabled=(st.session_state.page_number == 0)):
            st.session_state.page_number = max(0, st.session_state.page_number - 1)
            st.rerun()
    
    with col_pag5:
        if st.button("Next ➡️", disabled=(st.session_state.page_number >= total_pages - 1)):
            st.session_state.page_number = min(total_pages - 1, st.session_state.page_number + 1)
            st.rerun()
    
    with col_pag6:
        if st.button("Last ⏭️", disabled=(st.session_state.page_number >= total_pages - 1)):
            st.session_state.page_number = max(0, total_pages - 1)
            st.rerun()

    # Display table with headers and action buttons for each row
    if not df_view.empty:
        # Calculate pagination
        start_idx = st.session_state.page_number * rows_per_page
        end_idx = min(start_idx + rows_per_page, total_rows)
        df_page = df_view.iloc[start_idx:end_idx]
        
        # Header row with styling
        st.markdown("""
        <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    padding: 10px; 
                    border-radius: 8px 8px 0 0; 
                    color: white; 
                    font-weight: bold;'>
        </div>
        """, unsafe_allow_html=True)
        
        header_cols = st.columns([0.4, 0.8, 1.5, 1, 1.2, 0.8, 1.2, 0.8, 1, 0.6])
        headers = ["Row", "Emp ID", "Name", "Extension", "Department", "Cell", "Location", "Status", "Notes", "Action"]
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")
        
        st.markdown("---")
        
        # Data rows in scrollable container
        for display_idx, (idx, row) in enumerate(df_page.iterrows(), start=start_idx + 1):
            cols = st.columns([0.4, 0.8, 1.5, 1, 1.2, 0.8, 1.2, 0.8, 1, 0.6])
            
            # Display row data
            cols[0].write(f"{row.get('Row ID', display_idx)}")  # Show Row ID instead of sequential number
            emp_id_display = str(row.get('Employee ID', '')).strip()
            cols[1].write(emp_id_display if emp_id_display and emp_id_display != 'nan' else '-')
            cols[2].write(row['Name'])
            cols[3].write(row['Extension'])
            cols[4].write(row['Department'] if row['Department'] else '-')
            cols[5].write(row['Cell Number'] if row['Cell Number'] else '-')
            cols[6].write(row['Location'] if row['Location'] else '-')
            
            # Status badge
            status_color = "🟢" if row['Status'] == 'Active' else "🔴"
            cols[7].write(f"{status_color}")
            
            # Notes (truncated)
            notes_text = str(row.get('Notes', ''))
            cols[8].write(notes_text[:15] + '...' if len(notes_text) > 15 else notes_text)
            
            # Edit button
            if cols[9].button("✏️", key=f"edit_{idx}_{display_idx}", help="Edit this employee"):
                st.session_state.edit_mode = True
                st.session_state.edit_id = row['Row ID']  # Use Row ID instead of Employee ID
                st.session_state.scroll_to_edit = True
                st.rerun()
            
            # Light separator
            st.markdown("<hr style='margin: 5px 0; opacity: 0.3;'>", unsafe_allow_html=True)
    else:
        st.info("No employees found matching the filters.")

    # Download filtered data
    st.markdown("---")
    st.markdown("**📥 Export Data**")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl1:
        # Generate Excel data on button click
        def generate_excel_filtered():
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_view.to_excel(writer, index=False, sheet_name=EMP_SHEET)
            return output.getvalue()
        
        st.download_button(
            "📊 Excel (Filtered)", 
            data=generate_excel_filtered(),
            file_name=f"filtered_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            width="stretch",
            key="download_excel_filtered"
        )
    with col_dl2:
        st.download_button(
            "📄 CSV (Filtered)", 
            data=df_view.to_csv(index=False).encode('utf-8'), 
            file_name=f"filtered_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            mime="text/csv", 
            width="stretch",
            key="download_csv_filtered"
        )
    with col_dl3:
        # Export all data
        def generate_excel_all():
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_emp.to_excel(writer, index=False, sheet_name=EMP_SHEET)
            return output.getvalue()
        
        st.download_button(
            "📊 Excel (All)", 
            data=generate_excel_all(),
            file_name=f"all_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            width="stretch",
            key="download_excel_all"
        )

    st.markdown("---")

    # Edit / Delete actions - Enhanced with multiple search options
    # Add container for edit section
    edit_container = st.container()
    
    with edit_container:
        if st.session_state.edit_mode and st.session_state.edit_id:
            # Add visual separator and highlight with unique ID
            st.markdown("---")
            st.markdown('<div id="employee-edit-form-anchor"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                        padding: 15px; 
                        border-radius: 10px; 
                        margin: 20px 0;
                        animation: highlight-pulse 1.5s ease-in-out;'>
                <h3 style='color: white; margin: 0;'>✏️ Edit Employee Form</h3>
                <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9em;'>
                    Make your changes below and click Save
                </p>
            </div>
            <style>
                @keyframes highlight-pulse {
                    0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
                    50% { box-shadow: 0 0 20px 10px rgba(102, 126, 234, 0.3); }
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Enhanced JavaScript to scroll to this section
            if st.session_state.scroll_to_edit:
                st.markdown("""
                <script>
                    (function() {
                        function scrollToEditForm() {
                            const element = document.getElementById('employee-edit-form-anchor');
                            if (element) {
                                element.scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});
                                // Add a slight delay then scroll again to ensure it's visible
                                setTimeout(function() {
                                    element.scrollIntoView({behavior: 'smooth', block: 'start'});
                                }, 100);
                            }
                        }
                        
                        // Try multiple times to ensure DOM is ready
                        setTimeout(scrollToEditForm, 100);
                        setTimeout(scrollToEditForm, 300);
                        setTimeout(scrollToEditForm, 500);
                    })();
                </script>
                """, unsafe_allow_html=True)
                st.session_state.scroll_to_edit = False
            
            matched = df_emp[df_emp["Row ID"].astype(str) == str(st.session_state.edit_id)]
            if not matched.empty:
                row = matched.iloc[0]
                with st.form("edit_form"):
                    row_id_display = row.get('Row ID', 'N/A')
                    st.markdown(f"**Editing Employee: {row['Name']}**")
                    st.caption(f"Row ID: {row_id_display} | Original Employee ID: {row['Employee ID']}")
                
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        # Allow editing Employee ID
                        new_employee_id = st.text_input("Employee ID", value=row["Employee ID"], help="Optional - You can change or leave blank")
                        name = st.text_input("Name *", value=row["Name"]) 
                        extension = st.text_input("Extension", value=row["Extension"]) 
                        department = st.selectbox("Department", options=[""] + dept_options, index=(dept_options.index(row["Department"]) + 1) if row["Department"] in dept_options else 0)
                    with col_e2:
                        cell = st.text_input("Cell Number", value=row["Cell Number"])
                        location = st.text_input("Location", value=row["Location"]) 
                        status = st.selectbox("Status", options=["Active", "Inactive"], index=0 if row["Status"]=="Active" else 1)
                        notes = st.text_area("Notes", value=row.get("Notes", ""))
                    
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        submitted = st.form_submit_button("💾 Save Changes", width="stretch")
                    with col_b2:
                        delete_btn = st.form_submit_button("🗑️ Delete User", width="stretch")
                    with col_b3:
                        cancel_btn = st.form_submit_button("❌ Cancel", width="stretch")

                    if submitted:
                        if not name.strip():
                            st.error("⚠️ Name is required!")
                        elif not extension.strip():
                            st.error("⚠️ Extension is required!")
                        else:
                            idx = matched.index[0]
                            new_employee_id = new_employee_id.strip()
                            # Check if new Employee ID is different and already exists
                            if new_employee_id != str(row["Employee ID"]):
                                # Only check for duplicates if Employee ID is provided
                                if new_employee_id and new_employee_id in st.session_state.df_emp["Employee ID"].astype(str).values:
                                    st.error(f"⚠️ Employee ID '{new_employee_id}' already exists! Please use a different ID.")
                                else:
                                    # Preserve Row ID if it exists
                                    if "Row ID" not in st.session_state.df_emp.columns or pd.isna(st.session_state.df_emp.at[idx, "Row ID"]):
                                        st.session_state.df_emp.at[idx, "Row ID"] = next_row_id(st.session_state.df_emp)
                                    
                                    st.session_state.df_emp.at[idx, "Employee ID"] = str(new_employee_id) if new_employee_id else ""
                                    st.session_state.df_emp.at[idx, "Name"] = str(name).strip()
                                    st.session_state.df_emp.at[idx, "Extension"] = str(extension).strip()
                                    st.session_state.df_emp.at[idx, "Department"] = str(department).strip() if department else ""
                                    st.session_state.df_emp.at[idx, "Cell Number"] = str(cell).strip() if cell and str(cell).strip() else ""
                                    st.session_state.df_emp.at[idx, "Location"] = str(location).strip() if location and str(location).strip() else ""
                                    st.session_state.df_emp.at[idx, "Status"] = str(status)
                                    st.session_state.df_emp.at[idx, "Notes"] = str(notes).strip() if notes and str(notes).strip() else ""
                                    st.session_state.df_emp.at[idx, "Last Updated"] = datetime.utcnow().isoformat()
                                    write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                                    st.success("✅ Saved changes to employee and updated Excel.")
                                    # Clear edit mode BEFORE rerun
                                    st.session_state.edit_mode = False
                                    st.session_state.edit_id = None
                                    time.sleep(0.3)  # Brief pause to show success message
                                    st.rerun()
                            else:
                                # Preserve Row ID if it exists
                                if "Row ID" not in st.session_state.df_emp.columns or pd.isna(st.session_state.df_emp.at[idx, "Row ID"]):
                                    st.session_state.df_emp.at[idx, "Row ID"] = next_row_id(st.session_state.df_emp)
                                
                                st.session_state.df_emp.at[idx, "Name"] = str(name).strip()
                                st.session_state.df_emp.at[idx, "Extension"] = str(extension).strip()
                                st.session_state.df_emp.at[idx, "Department"] = str(department).strip() if department else ""
                                st.session_state.df_emp.at[idx, "Cell Number"] = str(cell).strip() if cell and str(cell).strip() else ""
                                st.session_state.df_emp.at[idx, "Location"] = str(location).strip() if location and str(location).strip() else ""
                                st.session_state.df_emp.at[idx, "Status"] = str(status)
                                st.session_state.df_emp.at[idx, "Notes"] = str(notes).strip() if notes and str(notes).strip() else ""
                                st.session_state.df_emp.at[idx, "Last Updated"] = datetime.utcnow().isoformat()
                                write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                                st.success("✅ Saved changes to employee and updated Excel.")
                                # Clear edit mode BEFORE rerun
                                st.session_state.edit_mode = False
                                st.session_state.edit_id = None
                                time.sleep(0.3)  # Brief pause to show success message
                                st.rerun()
                    
                    if delete_btn:
                        idx = matched.index[0]
                        st.session_state.df_emp = st.session_state.df_emp.drop(index=idx).reset_index(drop=True)
                        write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                        st.success("🗑️ Deleted employee and updated Excel.")
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.rerun()
                        
                    if cancel_btn:
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.rerun()
        else:
            st.subheader("✏️ Edit / Delete Employee")
            st.markdown("**Search by multiple criteria:**")
            
            search_by = st.radio("Search by:", ["Employee ID", "Name", "Extension", "Cell Number"], horizontal=True)
            
            if search_by == "Employee ID":
                search_value = st.text_input("Enter Employee ID (partial match)")
                if search_value:
                    matched = df_emp[df_emp["Employee ID"].astype(str).str.contains(search_value, case=False, na=False)]
            elif search_by == "Name":
                search_value = st.text_input("Enter Name (partial match)")
                if search_value:
                    matched = df_emp[df_emp["Name"].str.contains(search_value, case=False, na=False)]
            elif search_by == "Extension":
                search_value = st.text_input("Enter Extension (partial match)")
                if search_value:
                    matched = df_emp[df_emp["Extension"].astype(str).str.contains(search_value, case=False, na=False)]
            else:  # Cell Number
                search_value = st.text_input("Enter Cell Number (partial match)")
                if search_value:
                    matched = df_emp[df_emp["Cell Number"].astype(str).str.contains(search_value, case=False, na=False)]
            
            if 'search_value' in locals() and search_value:
                if matched.empty:
                    st.info("❌ No employee found with that criteria.")
                else:
                    st.success(f"✅ Found {len(matched)} employee(s)")
                    for idx, row in matched.iterrows():
                        col1_s, col2_s = st.columns([3, 1])
                        with col1_s:
                            st.write(f"**{row['Name']}** - ID: {row['Employee ID']} - Ext: {row['Extension']} - Status: {row['Status']}")
                        with col2_s:
                            if st.button(f"✏️ Edit", key=f"select_edit_{idx}"):
                                st.session_state.edit_mode = True
                                st.session_state.edit_id = row['Row ID']  # Use Row ID instead of Employee ID
                                st.session_state.scroll_to_edit = True
                                st.rerun()
    
    # View Departments section - collapsible with search
    st.markdown("---")
    if 'show_dept_view' not in st.session_state:
        st.session_state.show_dept_view = False
    
    col_dept_btn1, col_dept_btn2 = st.columns([2, 1])
    with col_dept_btn1:
        st.subheader("🏢 View Departments")
    with col_dept_btn2:
        if st.button("👁️ Toggle View" if st.session_state.show_dept_view else "👁️ Show", key="toggle_dept_view"):
            st.session_state.show_dept_view = not st.session_state.show_dept_view
            st.rerun()
    
    if st.session_state.show_dept_view:
        st.info("💡 Use 'Manage Departments' in sidebar for full edit/merge/delete capabilities")
        
        # Search departments
        dept_view_search = st.text_input("🔍 Search departments (partial match)", key="dept_view_search", placeholder="Enter department name...")
        
        # Filter departments based on search
        if dept_view_search:
            filtered_depts = df_dept[df_dept["Department Name"].str.contains(dept_view_search, case=False, na=False)]
        else:
            filtered_depts = df_dept
        
        # Display in scrollable container
        if filtered_depts.empty:
            st.info("❌ No departments found")
        else:
            st.success(f"📋 Showing {len(filtered_depts)} department(s)")
            with st.container(height=400):
                for idx, dept_row in filtered_depts.iterrows():
                    dept_name = dept_row["Department Name"]
                    dept_desc = dept_row["Description"] if dept_row["Description"] and dept_row["Description"] != 'nan' else "No description"
                    emp_count = len(df_emp[df_emp["Department"].astype(str).str.strip() == dept_name])
                    
                    with st.expander(f"🏢 **{dept_name}** ({emp_count} employees)", expanded=False):
                        st.write(f"**Dept ID:** {dept_row['Dept ID']}")
                        st.write(f"**Description:** {dept_desc}")
                        st.write(f"**Employees:** {emp_count}")
                        
                        if emp_count > 0:
                            st.markdown("**Assigned Employees:**")
                            assigned_emps = df_emp[df_emp["Department"].astype(str).str.strip() == dept_name]
                            for _, emp in assigned_emps.head(10).iterrows():
                                st.write(f"• {emp['Name']} ({emp.get('Employee ID', 'N/A')}) - Ext: {emp['Extension']}")
                            if emp_count > 10:
                                st.write(f"... and {emp_count - 10} more employee(s)")

with col2:
    st.subheader("➕ Quick Add")
    st.markdown("**Add New Employee**")
    with st.form("add_emp_form", clear_on_submit=True):
        new_empid = st.text_input("Employee ID", placeholder="EMP001 (Optional)")
        new_name = st.text_input("Name *", placeholder="John Doe")
        new_extension = st.text_input("Extension (4 digits) *", placeholder="1234")
        new_department = st.selectbox("Department", options=[""] + dept_options)
        new_cell = st.text_input("Cell Number", placeholder="+1234567890")
        new_location = st.text_input("Location", placeholder="New York")
        new_status = st.selectbox("Status", options=["Active", "Inactive"], index=0)
        new_notes = st.text_area("Notes", placeholder="Additional information...")
        submit_new = st.form_submit_button("➕ Add Employee", width="stretch")
        
        if submit_new:
            if not new_name:
                st.error("⚠️ Name is required!")
            elif not new_extension:
                st.error("⚠️ Extension is required!")
            else:
                eid = new_empid.strip() if new_empid.strip() else ""
                
                # Check if Employee ID already exists (only if provided)
                if eid and eid in st.session_state.df_emp["Employee ID"].astype(str).values:
                    st.error(f"⚠️ Employee ID '{eid}' already exists! Please use a different ID.")
                else:
                    # Generate next Row ID
                    row_id = next_row_id(st.session_state.df_emp)
                    
                    new_row = {
                        "Row ID": row_id,
                        "Employee ID": eid,
                        "Name": new_name,
                        "Extension": new_extension,
                        "Department": new_department,
                        "Cell Number": str(new_cell).strip() if new_cell and str(new_cell).strip() else "",
                        "Location": str(new_location).strip() if new_location and str(new_location).strip() else "",
                        "Status": new_status,
                        "Notes": str(new_notes).strip() if new_notes and str(new_notes).strip() else "",
                        "Last Updated": datetime.utcnow().isoformat()
                    }
                    st.session_state.df_emp = pd.concat([st.session_state.df_emp, pd.DataFrame([new_row])], ignore_index=True)
                    write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                    st.success(f"✅ Added {new_name} with Employee ID {eid} (Row #{row_id}).")
                    st.rerun()

    st.markdown("---")
    st.subheader("🏢 Add Department")
    st.info("💡 Use 'Manage Departments' button in sidebar to view/edit/delete departments")
    with st.form("add_dept_form", clear_on_submit=True):
        dname = st.text_input("Department Name *", placeholder="IT Department")
        ddesc = st.text_area("Description", placeholder="Information Technology Department")
        add_dept_btn = st.form_submit_button("➕ Add Department", width="stretch")
        if add_dept_btn:
            if not dname.strip():
                st.error("⚠️ Department name is required!")
            elif dname.strip().lower() in st.session_state.df_dept["Department Name"].str.lower().values:
                st.error(f"⚠️ Department '{dname.strip()}' already exists! Please use a different name.")
            else:
                did = next_dept_id(st.session_state.df_dept)
                st.session_state.df_dept = pd.concat([st.session_state.df_dept, pd.DataFrame([{"Dept ID": did, "Department Name": dname.strip(), "Description": ddesc.strip()}])], ignore_index=True)
                write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                st.success(f"✅ Added department '{dname.strip()}'")
                st.rerun()

    st.markdown("---")
    st.subheader("✏️ Edit / Delete Department")
    st.markdown("**Search by name (partial match):**")
    
    edit_dept_search = st.text_input("Enter Department Name (partial match)", key="dept_search_edit")
    if edit_dept_search:
        # Search by partial name match
        matched_depts = df_dept[df_dept["Department Name"].str.contains(edit_dept_search, case=False, na=False)]
        
        if matched_depts.empty:
            st.info("❌ No department found with that name.")
        else:
            st.success(f"✅ Found {len(matched_depts)} department(s)")
            for idx, dept_row in matched_depts.iterrows():
                col1_d, col2_d = st.columns([3, 1])
                with col1_d:
                    emp_count = len(df_emp[df_emp['Department'] == dept_row['Department Name']])
                    st.write(f"**{dept_row['Department Name']}** - ID: {dept_row['Dept ID']} - Employees: {emp_count}")
                with col2_d:
                    if st.button(f"✏️ Edit", key=f"select_dept_edit_{idx}"):
                        st.session_state.edit_dept_mode = True
                        st.session_state.edit_dept_idx = idx
                        st.rerun()
    
    # Show edit form if department selected
    if 'edit_dept_mode' not in st.session_state:
        st.session_state.edit_dept_mode = False
        st.session_state.edit_dept_idx = None
    
    if st.session_state.edit_dept_mode and st.session_state.edit_dept_idx is not None:
        idx = st.session_state.edit_dept_idx
        if idx in df_dept.index:
            row = df_dept.loc[idx]
            old_dept_name = row['Department Name']
            
            st.markdown("---")
            st.markdown('<div id="department-edit-form-anchor"></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); 
                        padding: 12px; 
                        border-radius: 8px; 
                        margin: 15px 0;
                        animation: highlight-pulse 1.5s ease-in-out;'>
                <h4 style='color: white; margin: 0;'>✏️ Editing: {old_dept_name}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # JavaScript to scroll department edit into view
            st.markdown("""
            <script>
                (function() {
                    function scrollToDeptForm() {
                        const element = document.getElementById('department-edit-form-anchor');
                        if (element) {
                            element.scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});
                            setTimeout(function() {
                                element.scrollIntoView({behavior: 'smooth', block: 'start'});
                            }, 100);
                        }
                    }
                    
                    setTimeout(scrollToDeptForm, 100);
                    setTimeout(scrollToDeptForm, 300);
                    setTimeout(scrollToDeptForm, 500);
                })();
            </script>
            """, unsafe_allow_html=True)
            
            with st.form("edit_dept_form", clear_on_submit=True):
                dn = st.text_input("Department Name *", value=old_dept_name) 
                dd = st.text_area("Description", value=row["Description"]) 
                
                col_d1, col_d2, col_d3 = st.columns(3)
                with col_d1:
                    save_dept = st.form_submit_button("💾 Save", width="stretch")
                with col_d2:
                    del_dept = st.form_submit_button("🗑️ Delete", width="stretch")
                with col_d3:
                    cancel_dept = st.form_submit_button("❌ Cancel", width="stretch")
                    
                if save_dept:
                    if not dn.strip():
                        st.error("⚠️ Department name is required!")
                    elif dn.strip().lower() != old_dept_name.lower() and dn.strip().lower() in df_dept["Department Name"].str.lower().values:
                        st.error(f"⚠️ Department '{dn.strip()}' already exists!")
                        st.info("💡 Use 'Manage Departments' in sidebar to merge departments, or choose a different name")
                    else:
                        # Explicitly convert to string to avoid dtype warnings
                        st.session_state.df_dept.at[idx, "Department Name"] = str(dn.strip())
                        st.session_state.df_dept.at[idx, "Description"] = str(dd.strip()) if dd.strip() else ""
                        
                        # Update department name in all employee records
                        if old_dept_name != dn.strip():
                            st.session_state.df_emp.loc[st.session_state.df_emp["Department"] == old_dept_name, "Department"] = str(dn.strip())
                            st.info(f"📝 Updated department name from '{old_dept_name}' to '{dn.strip()}' in all employee records.")
                        
                        write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                        st.success("✅ Department updated.")
                        # Clear edit mode BEFORE rerun
                        st.session_state.edit_dept_mode = False
                        st.session_state.edit_dept_idx = None
                        time.sleep(0.5)  # Brief pause to show success message
                        st.rerun()
                    
                if del_dept:
                    dept_name = st.session_state.df_dept.at[idx, "Department Name"]
                    emp_count = len(st.session_state.df_emp[st.session_state.df_emp["Department"] == dept_name])
                    
                    if emp_count > 0:
                        st.warning(f"⚠️ This department has {emp_count} employee(s). They will be unassigned.")
                    
                    st.session_state.df_dept = st.session_state.df_dept.drop(index=idx).reset_index(drop=True)
                    # Remove department from employees (set to blank)
                    st.session_state.df_emp.loc[st.session_state.df_emp["Department"] == dept_name, "Department"] = ""
                    write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                    st.success("🗑️ Deleted department and cleared assignments in employees.")
                    st.session_state.edit_dept_mode = False
                    st.session_state.edit_dept_idx = None
                    st.rerun()
                
                if cancel_dept:
                    st.session_state.edit_dept_mode = False
                    st.session_state.edit_dept_idx = None
                    st.rerun()

st.markdown("---")
st.markdown("---")

# Footer section with better styling
col_foot1, col_foot2, col_foot3 = st.columns(3)
with col_foot1:
    st.metric("📁 Data Source", "Excel Workbook")
    st.caption(f"File: `{EXCEL_PATH}`")
with col_foot2:
    if os.path.exists(EXCEL_PATH):
        mod_time = datetime.fromtimestamp(os.path.getmtime(EXCEL_PATH))
        st.metric("🕐 Last Modified", mod_time.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        st.metric("🕐 Last Modified", "N/A")
with col_foot3:
    file_size = os.path.getsize(EXCEL_PATH) if os.path.exists(EXCEL_PATH) else 0
    st.metric("📊 File Size", f"{file_size / 1024:.2f} KB")

# Footer: show raw data and last saved time
with st.expander("🔍 Raw Employees Data (for debugging)"):
    # Convert to string types for display to avoid Arrow errors
    df_emp_display = df_emp.copy()
    df_emp_display = df_emp_display.astype(str)
    st.dataframe(df_emp_display, width="stretch")

with st.expander("🔍 Raw Departments Data (for debugging)"):
    # Convert to string types for display to avoid Arrow errors
    df_dept_display = df_dept.copy()
    df_dept_display = df_dept_display.astype(str)
    st.dataframe(df_dept_display, width="stretch")

st.markdown("---")

# Bulk Upload Section
if st.session_state.show_bulk_upload:
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;'>
        <h3 style='color: white; margin: 0;'>📥 Bulk Upload Employees</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9em;'>
            Upload Excel or CSV file to import multiple employees at once
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_bulk1, col_bulk2 = st.columns([2, 1])
    
    with col_bulk1:
        st.markdown("### Step 1: Upload File")
        uploaded_file = st.file_uploader(
            "Choose Excel (.xlsx) or CSV file", 
            type=['xlsx', 'xls', 'csv'],
            help="Upload a file containing employee data"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                if uploaded_file.name.endswith('.csv'):
                    bulk_df = pd.read_csv(uploaded_file)
                else:
                    bulk_df = pd.read_excel(uploaded_file, engine='openpyxl')
                
                st.success(f"✅ File uploaded successfully! Found {len(bulk_df)} rows and {len(bulk_df.columns)} columns.")
                st.session_state.bulk_upload_df = bulk_df
                
                # Show preview
                st.markdown("**📋 File Preview (first 5 rows):**")
                st.dataframe(bulk_df.head(), use_container_width=True)
                
                st.markdown("---")
                st.markdown("### Step 2: Map Columns")
                st.info("💡 Map columns from your file to the system fields. Unmapped columns will be ignored.")
                
                # Column mapping
                file_columns = ["(Don't Import)"] + list(bulk_df.columns)
                system_columns = [col for col in EMP_COLUMNS if col not in ["Row ID", "Last Updated"]]
                
                col_map1, col_map2 = st.columns(2)
                mapping = {}
                
                with col_map1:
                    st.markdown("**📄 Map Required Fields:**")
                    for sys_col in ["Employee ID", "Name", "Extension"]:
                        # Try to auto-detect matching column
                        default_idx = 0
                        for idx, file_col in enumerate(file_columns):
                            if file_col.lower() == sys_col.lower() or file_col.lower().replace(" ", "") == sys_col.lower().replace(" ", ""):
                                default_idx = idx
                                break
                        
                        selected = st.selectbox(
                            f"{sys_col} {'*' if sys_col in ['Name', 'Extension'] else '(Optional)'}",
                            options=file_columns,
                            index=default_idx,
                            key=f"map_{sys_col}"
                        )
                        if selected != "(Don't Import)":
                            mapping[sys_col] = selected
                
                with col_map2:
                    st.markdown("**📋 Map Optional Fields:**")
                    for sys_col in ["Department", "Cell Number", "Location", "Status", "Notes"]:
                        # Try to auto-detect matching column
                        default_idx = 0
                        for idx, file_col in enumerate(file_columns):
                            if file_col.lower() == sys_col.lower() or file_col.lower().replace(" ", "") == sys_col.lower().replace(" ", ""):
                                default_idx = idx
                                break
                        
                        selected = st.selectbox(
                            f"{sys_col}",
                            options=file_columns,
                            index=default_idx,
                            key=f"map_{sys_col}"
                        )
                        if selected != "(Don't Import)":
                            mapping[sys_col] = selected
                
                st.session_state.bulk_mapping = mapping
                
                st.markdown("---")
                st.markdown("### Step 3: Set Default Values (Optional)")
                st.info("💡 Set default values for fields not in your file, or to override imported values.")
                
                col_def1, col_def2, col_def3 = st.columns(3)
                defaults = {}
                
                with col_def1:
                    dept_default = st.selectbox("Default Department", options=["(Use Mapped Value)"] + dept_options, key="def_dept")
                    if dept_default != "(Use Mapped Value)":
                        defaults["Department"] = dept_default
                    
                    status_default = st.selectbox("Default Status", options=["(Use Mapped Value)", "Active", "Inactive"], key="def_status")
                    if status_default != "(Use Mapped Value)":
                        defaults["Status"] = status_default
                
                with col_def2:
                    location_default = st.text_input("Default Location", placeholder="(Use Mapped Value)", key="def_loc")
                    if location_default.strip():
                        defaults["Location"] = location_default.strip()
                
                with col_def3:
                    notes_default = st.text_area("Default Notes", placeholder="(Use Mapped Value)", key="def_notes")
                    if notes_default.strip():
                        defaults["Notes"] = notes_default.strip()
                
                st.session_state.bulk_defaults = defaults
                
                st.markdown("---")
                st.markdown("### Step 4: Handle Missing Departments")
                
                # Extract unique departments from import file
                import_departments = set()
                for idx, row in bulk_df.iterrows():
                    dept_value = None
                    if "Department" in mapping:
                        dept_value = row[mapping["Department"]] if pd.notna(row[mapping["Department"]]) else None
                    
                    # Check if default department is set
                    if "Department" in defaults:
                        dept_value = defaults["Department"]
                    
                    if dept_value and str(dept_value).strip():
                        import_departments.add(str(dept_value).strip())
                
                # Check which departments don't exist
                existing_dept_names = set(st.session_state.df_dept["Department Name"].astype(str).str.strip().values)
                missing_departments = import_departments - existing_dept_names
                
                if missing_departments:
                    st.warning(f"⚠️ Found {len(missing_departments)} department(s) that don't exist in the system")
                    st.info("💡 Choose an action for each missing department")
                    
                    for dept_name in sorted(missing_departments):
                        dept_key = f"dept_{dept_name}"
                        
                        with st.expander(f"🏢 Department: **{dept_name}**", expanded=True):
                            col_d1, col_d2 = st.columns([2, 1])
                            
                            with col_d1:
                                action = st.radio(
                                    f"Action for '{dept_name}':",
                                    options=["Create New", "Map to Existing", "Skip (Leave Blank)"],
                                    key=f"{dept_key}_action",
                                    horizontal=True
                                )
                                
                                if action == "Create New":
                                    desc = st.text_input(
                                        "Department Description (Optional):",
                                        key=f"{dept_key}_desc",
                                        placeholder="Enter description..."
                                    )
                                    st.session_state.bulk_dept_actions[dept_name] = {
                                        "action": "create",
                                        "description": desc.strip() if desc else ""
                                    }
                                    st.success(f"✅ Will create new department: {dept_name}")
                                
                                elif action == "Map to Existing":
                                    existing_dept = st.selectbox(
                                        "Select existing department:",
                                        options=[""] + sorted(existing_dept_names),
                                        key=f"{dept_key}_map"
                                    )
                                    if existing_dept:
                                        st.session_state.bulk_dept_actions[dept_name] = {
                                            "action": "map",
                                            "target": existing_dept
                                        }
                                        st.info(f"🔄 Will map '{dept_name}' → '{existing_dept}'")
                                    else:
                                        st.warning("⚠️ Please select a department to map to")
                                
                                else:  # Skip
                                    st.session_state.bulk_dept_actions[dept_name] = {
                                        "action": "skip"
                                    }
                                    st.info(f"⏭️ Will skip '{dept_name}' (employees will have no department)")
                            
                            with col_d2:
                                # Show count of employees using this department
                                emp_count = sum(1 for idx, row in bulk_df.iterrows() 
                                              if "Department" in mapping and 
                                              pd.notna(row[mapping["Department"]]) and 
                                              str(row[mapping["Department"]]).strip() == dept_name)
                                st.metric("Employees", emp_count)
                    
                    st.session_state.missing_depts_handled = True
                else:
                    st.success("✅ All departments already exist in the system")
                    st.session_state.missing_depts_handled = True
                
                st.markdown("---")
                st.markdown("### Step 5: Review & Handle Duplicates")
                
                # Initialize selection state
                if 'bulk_selections' not in st.session_state:
                    st.session_state.bulk_selections = {}
                
                # Only proceed if departments are handled
                if not st.session_state.missing_depts_handled:
                    st.info("⏳ Please handle missing departments above before proceeding to import")
                else:
                    # Create preview dataframe with duplicate detection
                    preview_data = []
                    duplicate_records = []
                    error_records = []
                    
                    existing_emp_ids = set(st.session_state.df_emp["Employee ID"].astype(str).values)
                    existing_extensions = set(st.session_state.df_emp["Extension"].astype(str).values)
                    
                    for idx, row in bulk_df.iterrows():
                        new_emp = {
                            "Row ID": next_row_id(st.session_state.df_emp) + len(preview_data) + len(duplicate_records),
                            "File Row": idx + 2,  # Excel row number (1-indexed + header)
                        }
                        
                        # Map columns
                        for sys_col, file_col in mapping.items():
                            value = row[file_col] if pd.notna(row[file_col]) else ""
                            new_emp[sys_col] = str(value).strip()
                        
                        # Apply defaults (override if set)
                        for sys_col, default_value in defaults.items():
                            new_emp[sys_col] = default_value
                        
                        # Apply department mappings/skips
                        if "Department" in new_emp:
                            dept_name = new_emp["Department"]
                            if dept_name in st.session_state.bulk_dept_actions:
                                action = st.session_state.bulk_dept_actions[dept_name]
                                if action["action"] == "map":
                                    new_emp["Department"] = action["target"]
                                elif action["action"] == "skip":
                                    new_emp["Department"] = ""
                                # If "create", keep the department name as-is
                        
                        # Fill missing required columns
                        for col in EMP_COLUMNS:
                            if col not in new_emp:
                                if col == "Last Updated":
                                    new_emp[col] = datetime.utcnow().isoformat()
                                else:
                                    new_emp[col] = ""
                        
                        # Validate
                        row_errors = []
                        if not new_emp.get("Name", "").strip():
                            row_errors.append("Missing Name")
                        if not new_emp.get("Extension", "").strip():
                            row_errors.append("Missing Extension")
                        
                        # Check for duplicates
                        emp_id = new_emp.get("Employee ID", "").strip()
                        extension = new_emp.get("Extension", "").strip()
                        
                        duplicate_issues = []
                        if emp_id and emp_id in existing_emp_ids:
                            duplicate_issues.append(f"Employee ID '{emp_id}' exists")
                        if extension and extension in existing_extensions:
                            duplicate_issues.append(f"Extension '{extension}' exists")
                        
                        if row_errors:
                            new_emp["Errors"] = ", ".join(row_errors)
                            error_records.append(new_emp)
                        elif duplicate_issues:
                            new_emp["Duplicate Issues"] = duplicate_issues
                            duplicate_records.append(new_emp)
                            # Initialize selection state for this record
                            record_key = f"row_{new_emp['File Row']}"
                            if record_key not in st.session_state.bulk_selections:
                                st.session_state.bulk_selections[record_key] = {"import": False, "replace": False}
                        else:
                            preview_data.append(new_emp)
                            # Add to tracking sets
                            if emp_id:
                                existing_emp_ids.add(emp_id)
                            if extension:
                                existing_extensions.add(extension)
                    
                    # Show clean records
                    if preview_data:
                        st.markdown(f"**✅ {len(preview_data)} Clean Records (No Issues):**")
                        preview_df = pd.DataFrame(preview_data)
                        st.dataframe(preview_df[["File Row", "Employee ID", "Name", "Extension", "Department", "Location", "Status"]], use_container_width=True, height=200)
                    
                    # Show duplicate records with checkboxes
                    if duplicate_records:
                        st.markdown(f"**⚠️ {len(duplicate_records)} Records with Duplicates:**")
                        st.info("💡 Check the boxes to choose how to handle each duplicate record")
                    
                        # Create scrollable container
                        for dup_emp in duplicate_records:
                            record_key = f"row_{dup_emp['File Row']}"
                            
                            with st.expander(f"Row {dup_emp['File Row']}: {dup_emp['Name']} - Issues: {', '.join(dup_emp['Duplicate Issues'])}", expanded=False):
                                col_dup1, col_dup2 = st.columns([3, 1])
                                
                                with col_dup1:
                                    st.markdown(f"**📋 Record Details:**")
                                    st.write(f"- **Employee ID:** {dup_emp.get('Employee ID', 'N/A')}")
                                    st.write(f"- **Name:** {dup_emp.get('Name', 'N/A')}")
                                    st.write(f"- **Extension:** {dup_emp.get('Extension', 'N/A')}")
                                    st.write(f"- **Department:** {dup_emp.get('Department', 'N/A')}")
                                    st.write(f"- **Location:** {dup_emp.get('Location', 'N/A')}")
                                    st.write(f"- **Status:** {dup_emp.get('Status', 'N/A')}")
                                    
                                    # Show existing conflicting records
                                    st.markdown("**🔍 Existing Conflicting Record(s):**")
                                    emp_id = dup_emp.get('Employee ID', '').strip()
                                    extension = dup_emp.get('Extension', '').strip()
                                    
                                    conflicts = st.session_state.df_emp[
                                        (st.session_state.df_emp['Employee ID'].astype(str) == emp_id) | 
                                        (st.session_state.df_emp['Extension'].astype(str) == extension)
                                    ]
                                    if not conflicts.empty:
                                        st.dataframe(conflicts[["Employee ID", "Name", "Extension", "Department", "Status"]], use_container_width=True)
                                
                                with col_dup2:
                                    st.markdown("**🎯 Action:**")
                                    
                                    import_check = st.checkbox(
                                        "✅ Import as New",
                                        value=st.session_state.bulk_selections[record_key]["import"],
                                        key=f"{record_key}_import",
                                        help="Import this record with a new Row ID (duplicate IDs will be kept)"
                                    )
                                    st.session_state.bulk_selections[record_key]["import"] = import_check
                                    
                                    replace_check = st.checkbox(
                                        "🔄 Replace Existing",
                                        value=st.session_state.bulk_selections[record_key]["replace"],
                                        key=f"{record_key}_replace",
                                        help="Find and update the existing record with this data"
                                    )
                                    st.session_state.bulk_selections[record_key]["replace"] = replace_check
                                    
                                    if import_check and replace_check:
                                        st.warning("⚠️ Select only one action!")
                                    
                                    if not import_check and not replace_check:
                                        st.info("⏭️ Will be skipped")
                    
                    # Show error records
                    if error_records:
                        st.markdown(f"**❌ {len(error_records)} Records with Errors (Will be Skipped):**")
                        for err_emp in error_records[:5]:  # Show first 5
                            st.error(f"Row {err_emp['File Row']}: {err_emp.get('Name', 'N/A')} - {err_emp['Errors']}")
                        if len(error_records) > 5:
                            st.warning(f"... and {len(error_records) - 5} more error records")
                    
                    # Calculate totals
                    selected_duplicates = sum(1 for key, val in st.session_state.bulk_selections.items() 
                                             if val["import"] != val["replace"] and (val["import"] or val["replace"]))
                    total_to_import = len(preview_data) + selected_duplicates
                    
                    st.markdown("---")
                    st.markdown(f"### 📊 Import Summary")
                    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
                    with col_sum1:
                        st.metric("Clean Records", len(preview_data))
                    with col_sum2:
                        st.metric("Selected Duplicates", selected_duplicates)
                    with col_sum3:
                        st.metric("Will Skip", len(error_records) + len(duplicate_records) - selected_duplicates)
                    with col_sum4:
                        st.metric("Total to Import", total_to_import, delta=None)
                    
                    # Import buttons
                    st.markdown("---")
                    col_imp1, col_imp2, col_imp3 = st.columns(3)
                    
                    with col_imp1:
                        if st.button("✅ Import Selected Records", disabled=total_to_import == 0, width="stretch", type="primary", key="bulk_import_btn"):
                            imported_count = 0
                            replaced_count = 0
                            created_depts = []
                            
                            # First, create new departments based on bulk_dept_actions
                            for dept_name, action in st.session_state.bulk_dept_actions.items():
                                if action["action"] == "create":
                                    # Check if department already exists (shouldn't, but safety check)
                                    if dept_name not in st.session_state.df_dept["Department Name"].values:
                                        did = next_dept_id(st.session_state.df_dept)
                                        new_dept = {
                                            "Dept ID": did,
                                            "Department Name": dept_name,
                                            "Description": action.get("description", "")
                                        }
                                        st.session_state.df_dept = pd.concat([st.session_state.df_dept, pd.DataFrame([new_dept])], ignore_index=True)
                                        created_depts.append(dept_name)
                            
                            # Import clean records
                            for emp in preview_data:
                                emp_copy = {k: v for k, v in emp.items() if k in EMP_COLUMNS}
                                st.session_state.df_emp = pd.concat([st.session_state.df_emp, pd.DataFrame([emp_copy])], ignore_index=True)
                                imported_count += 1
                            
                            # Handle duplicate records based on selection
                            for dup_emp in duplicate_records:
                                record_key = f"row_{dup_emp['File Row']}"
                                selection = st.session_state.bulk_selections.get(record_key, {})
                                
                                if selection.get("import") and not selection.get("replace"):
                                    # Import as new record
                                    emp_copy = {k: v for k, v in dup_emp.items() if k in EMP_COLUMNS}
                                    st.session_state.df_emp = pd.concat([st.session_state.df_emp, pd.DataFrame([emp_copy])], ignore_index=True)
                                    imported_count += 1
                                
                                elif selection.get("replace") and not selection.get("import"):
                                    # Replace existing record
                                    emp_id = dup_emp.get('Employee ID', '').strip()
                                    extension = dup_emp.get('Extension', '').strip()
                                    
                                    # Find existing record by Employee ID first, then Extension
                                    if emp_id:
                                        existing_idx = st.session_state.df_emp[st.session_state.df_emp['Employee ID'].astype(str) == emp_id].index
                                    elif extension:
                                        existing_idx = st.session_state.df_emp[st.session_state.df_emp['Extension'].astype(str) == extension].index
                                    else:
                                        existing_idx = []
                                    
                                    if len(existing_idx) > 0:
                                        idx = existing_idx[0]
                                        # Update all fields except Row ID
                                        for col in EMP_COLUMNS:
                                            if col != "Row ID" and col in dup_emp:
                                                st.session_state.df_emp.at[idx, col] = str(dup_emp[col])
                                        st.session_state.df_emp.at[idx, "Last Updated"] = datetime.utcnow().isoformat()
                                        replaced_count += 1
                            
                            # Save to Excel
                            write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                            
                            # Show success message with details
                            success_msg = f"🎉 Successfully imported {imported_count} new records and updated {replaced_count} existing records!"
                            if created_depts:
                                success_msg += f"\n\n🏢 Created {len(created_depts)} new department(s): {', '.join(created_depts)}"
                            st.success(success_msg)
                            
                            # Reset state
                            st.session_state.show_bulk_upload = False
                            st.session_state.bulk_upload_df = None
                            st.session_state.bulk_mapping = {}
                            st.session_state.bulk_defaults = {}
                            st.session_state.bulk_selections = {}
                            st.session_state.bulk_dept_actions = {}
                            st.session_state.missing_depts_handled = False
                            time.sleep(1.5)
                            st.rerun()
                    
                    with col_imp2:
                        if st.button("📋 Download Template", width="stretch"):
                            template_df = pd.DataFrame(columns=["Employee ID", "Name", "Extension", "Department", "Cell Number", "Location", "Status", "Notes"])
                            template_df.loc[0] = ["EMP001", "John Doe", "1234", "IT", "+1234567890", "New York", "Active", "Sample employee"]
                            st.download_button(
                                "⬇️ Download Excel Template",
                                data=template_df.to_csv(index=False).encode('utf-8'),
                                file_name="employee_import_template.csv",
                                mime="text/csv"
                            )
                    
                    with col_imp3:
                        if st.button("❌ Cancel Import", width="stretch"):
                            st.session_state.show_bulk_upload = False
                            st.session_state.bulk_upload_df = None
                            st.session_state.bulk_mapping = {}
                            st.session_state.bulk_defaults = {}
                            st.session_state.bulk_dept_actions = {}
                            st.session_state.missing_depts_handled = False
                            st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please ensure your file is a valid Excel (.xlsx) or CSV file.")
    
    with col_bulk2:
        st.markdown("### 📖 Help & Tips")
        st.markdown("""
        **File Requirements:**
        - Excel (.xlsx, .xls) or CSV format
        - First row should contain column headers
        - At least Name and Extension columns
        
        **Required Fields:**
        - **Name**: Employee full name
        - **Extension**: 4-digit extension (recommended)
        
        **Optional Fields:**
        - Employee ID (can be left blank)
        - Department
        - Cell Number
        - Location
        - Status (Active/Inactive)
        - Notes
        
        **Tips:**
        - Use column mapping if your headers don't match exactly
        - Set default values to apply the same value to all imported employees
        - Review preview before importing
        - Duplicate Employee IDs will be skipped
        
        **Best Practices:**
        - Download the template for correct format
        - Clean your data before import
        - Import in batches if you have many records
        """)

st.markdown("---")

# Department Sync Section
if st.session_state.show_dept_sync:
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;'>
        <h3 style='color: white; margin: 0;'>🔄 Sync Departments from Employee Records</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9em;'>
            Review and handle departments found in employee records but not in the department list
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Find departments in employees that don't exist in departments table
    # Always read from the persisted workbook to get true state
    _sync_emp, _sync_dept = read_workbook(EXCEL_PATH)
    
    emp_depts = set(_sync_emp["Department"].dropna().astype(str).str.strip().values)
    emp_depts = {d for d in emp_depts if d and d != 'nan' and d != ''}
    
    existing_depts = set(_sync_dept["Department Name"].dropna().astype(str).str.strip().values)
    existing_depts = {d for d in existing_depts if d and d != 'nan' and d != ''}
    
    missing_depts = emp_depts - existing_depts
    
    if missing_depts:
        st.warning(f"⚠️ Found {len(missing_depts)} department(s) in employee records that don't exist in the department list")
        st.info("💡 Choose an action for each department to maintain data consistency")
        
        col_sync1, col_sync2 = st.columns([2, 1])
        
        with col_sync1:
            # Use a scrollable container to avoid long pages
            st.markdown(f"### 📋 Departments to Review ({len(missing_depts)})")
            with st.container(height=600):
                for dept_name in sorted(missing_depts):
                    dept_key = f"sync_dept_{dept_name}"
                    
                    with st.expander(f"🏢 Department: **{dept_name}**", expanded=True):
                        col_d1, col_d2 = st.columns([3, 1])
                        
                        with col_d1:
                            action = st.radio(
                                f"Action for '{dept_name}':",
                                options=["Create New Department", "Merge with Another Missing Department", "Map to Existing Department", "Update Employee Records (Remove Department)"],
                                key=f"{dept_key}_action",
                                help="Choose how to handle this department"
                            )
                            
                            if action == "Create New Department":
                                # Option to rename before creating
                                col_rename1, col_rename2 = st.columns([1, 3])
                                with col_rename1:
                                    rename = st.checkbox("Rename?", key=f"{dept_key}_rename_check")
                                with col_rename2:
                                    if rename:
                                        new_name = st.text_input(
                                            "New department name:",
                                            value=dept_name,
                                            key=f"{dept_key}_newname",
                                            help="Enter the corrected/preferred name"
                                        )
                                    else:
                                        new_name = dept_name
                                
                                # Check if new name already exists in existing departments
                                if rename and new_name and new_name.strip():
                                    existing_names_lower = [n.lower() for n in existing_depts if n]
                                    if new_name.strip().lower() in existing_names_lower:
                                        st.error(f"⚠️ Department '{new_name.strip()}' already exists!")
                                        st.info("💡 Options: Use 'Map to Existing Department' to merge with existing, or choose a different name")
                                        new_name = None  # Block creation
                                
                                if new_name is not None:
                                    desc = st.text_input(
                                        "Department Description (Optional):",
                                        key=f"{dept_key}_desc",
                                        placeholder="Enter description..."
                                    )
                                    st.session_state.sync_dept_actions[dept_name] = {
                                        "action": "create",
                                        "new_name": new_name.strip() if new_name else dept_name,
                                        "description": desc.strip() if desc else "Synced from employee records"
                                    }
                                    display_name = new_name if rename and new_name else dept_name
                                    st.success(f"✅ Will create new department: {display_name}")
                            
                            elif action == "Merge with Another Missing Department":
                                # Merge multiple missing departments into one
                                other_missing = [d for d in sorted(missing_depts) if d != dept_name]
                                
                                if not other_missing:
                                    st.warning("⚠️ No other missing departments to merge with")
                                else:
                                    merge_target = st.selectbox(
                                        "Select department to merge with:",
                                        options=[""] + other_missing,
                                        key=f"{dept_key}_merge",
                                        help="Both departments will be combined under one name"
                                    )
                                    
                                    if merge_target:
                                        # Option to rename the merged result
                                        use_custom_name = st.checkbox("Use custom name for merged department?", key=f"{dept_key}_merge_custom")
                                        if use_custom_name:
                                            merged_name = st.text_input(
                                                "Merged department name:",
                                                value=merge_target,
                                                key=f"{dept_key}_merge_name",
                                                help="Enter the final name for the merged department"
                                            )
                                        else:
                                            merged_name = merge_target
                                        
                                        st.session_state.sync_dept_actions[dept_name] = {
                                            "action": "merge",
                                            "merge_target": merge_target,
                                            "merged_name": merged_name.strip() if merged_name else merge_target
                                        }
                                        st.info(f"🔄 Will merge '{dept_name}' + '{merge_target}' → '{merged_name if use_custom_name else merge_target}'")
                                    else:
                                        st.warning("⚠️ Please select a department to merge with")
                            
                            elif action == "Map to Existing Department":
                                target_dept = st.selectbox(
                                    "Select existing department to map to:",
                                    options=[""] + sorted(existing_depts),
                                    key=f"{dept_key}_map",
                                    help="Employee records will be updated to use the selected department"
                                )
                                if target_dept:
                                    st.session_state.sync_dept_actions[dept_name] = {
                                        "action": "map",
                                        "target": target_dept
                                    }
                                    st.info(f"🔄 Will update employees from '{dept_name}' → '{target_dept}'")
                                else:
                                    st.warning("⚠️ Please select a department to map to")
                            
                            else:  # Update Employee Records
                                st.session_state.sync_dept_actions[dept_name] = {
                                    "action": "remove"
                                }
                                st.warning(f"⚠️ Will remove department from employee records (set to blank)")
                        
                        with col_d2:
                            # Show affected employees from persisted data
                            affected_emps = _sync_emp[
                                _sync_emp["Department"].astype(str).str.strip() == dept_name
                            ]
                            st.metric("Affected Employees", len(affected_emps))
                            
                            if len(affected_emps) > 0:
                                with st.expander("👥 View Employees"):
                                    for _, emp in affected_emps.iterrows():
                                        st.write(f"• {emp['Name']} ({emp.get('Employee ID', 'N/A')})")
        
        with col_sync2:
            st.markdown("### 📖 Quick Guide")
            st.info("""
**Create New:** Add department (can rename)

**Merge Missing:** Combine 2 missing depts

**Map to Existing:** Fix typos/duplicates

**Remove:** Clear from employee records
            """)
        
        st.markdown("---")
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("✅ Apply Changes", width="stretch", type="primary", key="apply_sync_btn"):
                # Check if all departments have valid actions
                incomplete = []
                for dept_name in missing_depts:
                    if dept_name not in st.session_state.sync_dept_actions:
                        incomplete.append(dept_name)
                    elif st.session_state.sync_dept_actions[dept_name]["action"] == "map":
                        if "target" not in st.session_state.sync_dept_actions[dept_name]:
                            incomplete.append(dept_name)
                
                if incomplete:
                    st.error(f"⚠️ Please complete actions for: {', '.join(incomplete)}")
                else:
                    created_count = 0
                    mapped_count = 0
                    removed_count = 0
                    merged_count = 0
                    renamed_count = 0
                    
                    # Track merged departments to avoid duplicate processing
                    processed_merges = set()
                    
                    for dept_name, action in st.session_state.sync_dept_actions.items():
                        if action["action"] == "create":
                            # Create new department (with optional rename)
                            did = next_dept_id(st.session_state.df_dept)
                            final_name = action.get("new_name", dept_name)
                            
                            new_dept = {
                                "Dept ID": did,
                                "Department Name": final_name,
                                "Description": action.get("description", "Synced from employee records")
                            }
                            st.session_state.df_dept = pd.concat([st.session_state.df_dept, pd.DataFrame([new_dept])], ignore_index=True)
                            
                            # Update employee records if renamed
                            if final_name != dept_name:
                                mask = st.session_state.df_emp["Department"].astype(str).str.strip() == dept_name
                                st.session_state.df_emp.loc[mask, "Department"] = final_name
                                st.session_state.df_emp.loc[mask, "Last Updated"] = datetime.utcnow().isoformat()
                                renamed_count += 1
                            
                            created_count += 1
                        
                        elif action["action"] == "merge":
                            # Merge two missing departments into one
                            merge_target = action.get("merge_target")
                            merged_name = action.get("merged_name", merge_target)
                            
                            # Create a unique key for this merge pair
                            merge_key = tuple(sorted([dept_name, merge_target]))
                            
                            if merge_key not in processed_merges:
                                # Create the merged department
                                did = next_dept_id(st.session_state.df_dept)
                                new_dept = {
                                    "Dept ID": did,
                                    "Department Name": merged_name,
                                    "Description": f"Merged from: {dept_name}, {merge_target}"
                                }
                                st.session_state.df_dept = pd.concat([st.session_state.df_dept, pd.DataFrame([new_dept])], ignore_index=True)
                                
                                # Update employee records for both departments
                                mask1 = st.session_state.df_emp["Department"].astype(str).str.strip() == dept_name
                                mask2 = st.session_state.df_emp["Department"].astype(str).str.strip() == merge_target
                                combined_mask = mask1 | mask2
                                
                                st.session_state.df_emp.loc[combined_mask, "Department"] = merged_name
                                st.session_state.df_emp.loc[combined_mask, "Last Updated"] = datetime.utcnow().isoformat()
                                
                                merged_count += 1
                                processed_merges.add(merge_key)
                        
                        elif action["action"] == "map":
                            # Update employee records to use existing department
                            target = action["target"]
                            mask = st.session_state.df_emp["Department"].astype(str).str.strip() == dept_name
                            st.session_state.df_emp.loc[mask, "Department"] = target
                            st.session_state.df_emp.loc[mask, "Last Updated"] = datetime.utcnow().isoformat()
                            mapped_count += len(st.session_state.df_emp[mask])
                        
                        elif action["action"] == "remove":
                            # Remove department from employee records
                            mask = st.session_state.df_emp["Department"].astype(str).str.strip() == dept_name
                            st.session_state.df_emp.loc[mask, "Department"] = ""
                            st.session_state.df_emp.loc[mask, "Last Updated"] = datetime.utcnow().isoformat()
                            removed_count += len(st.session_state.df_emp[mask])
                    
                    # Save changes
                    write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                    
                    # Show success message
                    success_msg = "🎉 Sync completed!\n\n"
                    if created_count > 0:
                        success_msg += f"✅ Created {created_count} new department(s)\n"
                    if merged_count > 0:
                        success_msg += f"🔀 Merged {merged_count} department pair(s) into one\n"
                    if renamed_count > 0:
                        success_msg += f"✏️ Renamed {renamed_count} department(s)\n"
                    if mapped_count > 0:
                        success_msg += f"🔄 Updated {mapped_count} employee record(s) with mapped departments\n"
                    if removed_count > 0:
                        success_msg += f"🗑️ Removed department from {removed_count} employee record(s)\n"
                    
                    st.success(success_msg)
                    
                    # Reset state
                    st.session_state.show_dept_sync = False
                    st.session_state.sync_dept_actions = {}
                    time.sleep(2)
                    st.rerun()
        
        with col_btn2:
            if st.button("🔄 Select All → Create New", width="stretch", help="Quick action: Create all missing departments"):
                for dept_name in missing_depts:
                    st.session_state.sync_dept_actions[dept_name] = {
                        "action": "create",
                        "description": "Synced from employee records"
                    }
                st.rerun()
        
        with col_btn3:
            if st.button("❌ Cancel Sync", width="stretch"):
                st.session_state.show_dept_sync = False
                st.session_state.sync_dept_actions = {}
                st.rerun()
    
    else:
        st.success("✅ All departments are in sync! No missing departments found in employee records.")
        
        # Show departments that are properly synced
        if emp_depts:
            st.info(f"📋 Found {len(emp_depts)} department(s) in employee records - all exist in the department list")
            with st.expander("View synced departments"):
                for dept in sorted(emp_depts):
                    emp_count = len(_sync_emp[_sync_emp["Department"].astype(str).str.strip() == dept])
                    st.write(f"✅ **{dept}** - {emp_count} employee(s)")
        else:
            st.info("No departments assigned to any employees yet")
        
        if st.button("🔙 Back to Main View", width="stretch"):
            st.session_state.show_dept_sync = False
            st.rerun()

st.markdown("---")

# Department Management Section
if st.session_state.show_dept_manage:
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;'>
        <h3 style='color: white; margin: 0;'>✏️ Manage Existing Departments</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.9em;'>
            Rename, merge, or delete departments from the department list
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Read current departments from persisted file
    _manage_emp, _manage_dept = read_workbook(EXCEL_PATH)
    
    if len(_manage_dept) == 0:
        st.info("No departments found in the department list")
    else:
        # Add search functionality
        search_dept = st.text_input("� Search departments by name", key="search_dept_manage", placeholder="Type to filter departments...")
        
        # Filter departments based on search
        if search_dept:
            filtered_dept = _manage_dept[_manage_dept["Department Name"].astype(str).str.contains(search_dept, case=False, na=False)]
        else:
            filtered_dept = _manage_dept
        
        st.info(f"📋 Showing {len(filtered_dept)} of {len(_manage_dept)} department(s)")
        
        # Use a scrollable container to avoid long pages
        st.markdown(f"### 📋 Department List")
        with st.container(height=600):
            if len(filtered_dept) == 0:
                st.warning("No departments found matching your search")
            else:
                for _, dept_row in filtered_dept.iterrows():
                    dept_id = dept_row["Dept ID"]
                    dept_name = str(dept_row["Department Name"]).strip()
                    dept_desc = str(dept_row.get("Description", "")).strip()
                    dept_key = f"manage_dept_{dept_id}"
                    
                    # Count employees using this department
                    emp_count = len(_manage_emp[_manage_emp["Department"].astype(str).str.strip() == dept_name])
                    
                    with st.expander(f"🏢 **{dept_name}** ({emp_count} employee(s))", expanded=False):
                        col_m1, col_m2 = st.columns([3, 1])
                        
                        with col_m1:
                            action = st.radio(
                                f"Action for '{dept_name}':",
                                options=["No Change", "Rename Department", "Merge with Another Department", "Delete Department"],
                                key=f"{dept_key}_action",
                                help="Choose how to modify this department"
                            )
                            
                            if action == "No Change":
                                if dept_id in st.session_state.dept_manage_actions:
                                    del st.session_state.dept_manage_actions[dept_id]
                            
                            elif action == "Rename Department":
                                new_name = st.text_input(
                                    "New department name:",
                                    value=dept_name,
                                    key=f"{dept_key}_newname",
                                    help="Enter the new name for this department"
                                )
                                new_desc = st.text_input(
                                    "Update description (optional):",
                                    value=dept_desc if dept_desc != 'nan' else "",
                                    key=f"{dept_key}_newdesc",
                                    placeholder="Enter description..."
                                )
                                
                                if new_name and new_name.strip() != dept_name:
                                    # Check if new name already exists (excluding current department)
                                    existing_names_lower = [
                                        n.lower() for n in _manage_dept["Department Name"].tolist() 
                                        if n and n.strip().lower() != dept_name.lower()
                                    ]
                                    
                                    if new_name.strip().lower() in existing_names_lower:
                                        st.error(f"⚠️ Department '{new_name.strip()}' already exists!")
                                        st.info("💡 Options: Use 'Merge with Another Department' to combine them, or choose a different name")
                                    else:
                                        st.session_state.dept_manage_actions[dept_id] = {
                                            "action": "rename",
                                            "old_name": dept_name,
                                            "new_name": new_name.strip(),
                                            "new_desc": new_desc.strip() if new_desc else dept_desc
                                        }
                                        st.success(f"✏️ Will rename: '{dept_name}' → '{new_name.strip()}'")
                                        if emp_count > 0:
                                            st.info(f"📝 Will update {emp_count} employee record(s)")
                                else:
                                    st.warning("⚠️ Please enter a different name")
                            
                            elif action == "Merge with Another Department":
                                # Get other departments (excluding current one)
                                other_depts = _manage_dept[_manage_dept["Dept ID"] != dept_id]["Department Name"].tolist()
                                
                                if not other_depts:
                                    st.warning("⚠️ No other departments available to merge with")
                                else:
                                    merge_target = st.selectbox(
                                        "Select department to merge with:",
                                        options=[""] + sorted([str(d).strip() for d in other_depts]),
                                        key=f"{dept_key}_merge_target",
                                        help="Both departments will be combined"
                                    )
                                    
                                    if merge_target:
                                        # Get the target department ID for later processing
                                        target_dept_id = _manage_dept[_manage_dept["Department Name"].astype(str).str.strip() == merge_target]["Dept ID"].iloc[0]
                                        
                                        # Ask which name to keep or use custom
                                        merge_mode = st.radio(
                                            "Choose final department name:",
                                            options=[f"Keep '{dept_name}'", f"Keep '{merge_target}'", "Use custom name"],
                                            key=f"{dept_key}_merge_mode"
                                        )
                                        
                                        if merge_mode == f"Keep '{dept_name}'":
                                            final_name = dept_name
                                            delete_id = target_dept_id
                                        elif merge_mode == f"Keep '{merge_target}'":
                                            final_name = merge_target
                                            delete_id = dept_id
                                        else:  # Use custom name
                                            final_name = st.text_input(
                                                "Enter new department name:",
                                                value=dept_name,
                                                key=f"{dept_key}_merge_custom",
                                                help="Enter the final name for the merged department"
                                            )
                                            delete_id = target_dept_id  # Delete target, rename current
                                        
                                        if final_name and final_name.strip():
                                            target_emp_count = len(_manage_emp[_manage_emp["Department"].astype(str).str.strip() == merge_target])
                                            
                                            st.session_state.dept_manage_actions[dept_id] = {
                                                "action": "merge_two",
                                                "dept1_name": dept_name,
                                                "dept1_id": dept_id,
                                                "dept2_name": merge_target,
                                                "dept2_id": target_dept_id,
                                                "final_name": final_name.strip(),
                                                "delete_id": delete_id
                                            }
                                            st.success(f"🔀 Will merge: '{dept_name}' + '{merge_target}' → '{final_name.strip()}'")
                                            total_emps = emp_count + target_emp_count
                                            if total_emps > 0:
                                                st.info(f"📝 Will combine {emp_count} + {target_emp_count} = {total_emps} employee(s)")
                                    else:
                                        st.warning("⚠️ Please select a department to merge with")
                            
                            elif action == "Delete Department":
                                if emp_count > 0:
                                    st.error(f"⚠️ Cannot delete: {emp_count} employee(s) are assigned to this department")
                                    st.info("💡 Either merge with another department or reassign employees first")
                                else:
                                    confirm = st.checkbox(f"Confirm deletion of '{dept_name}'", key=f"{dept_key}_delete_confirm")
                                    if confirm:
                                        st.session_state.dept_manage_actions[dept_id] = {
                                            "action": "delete",
                                            "old_name": dept_name
                                        }
                                        st.warning(f"🗑️ Will delete department: '{dept_name}'")
                        
                        with col_m2:
                            st.metric("Dept ID", dept_id)
                            st.metric("Employees", emp_count)
                            
                            if emp_count > 0:
                                with st.expander("👥 View"):
                                    affected_emps = _manage_emp[_manage_emp["Department"].astype(str).str.strip() == dept_name]
                                    for _, emp in affected_emps.head(10).iterrows():
                                        st.write(f"• {emp['Name']}")
                                    if emp_count > 10:
                                        st.write(f"... and {emp_count - 10} more")
        
        st.markdown("---")
        
        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("✅ Apply Changes", width="stretch", type="primary", key="apply_manage_btn"):
                if not st.session_state.dept_manage_actions:
                    st.warning("⚠️ No changes to apply")
                else:
                    renamed_count = 0
                    merged_count = 0
                    deleted_count = 0
                    
                    for dept_id, action_data in st.session_state.dept_manage_actions.items():
                        action = action_data["action"]
                        
                        if action == "rename":
                            # Rename department in department list
                            mask_dept = st.session_state.df_dept["Dept ID"] == dept_id
                            st.session_state.df_dept.loc[mask_dept, "Department Name"] = action_data["new_name"]
                            if action_data.get("new_desc"):
                                st.session_state.df_dept.loc[mask_dept, "Description"] = action_data["new_desc"]
                            
                            # Update all employee records
                            mask_emp = st.session_state.df_emp["Department"].astype(str).str.strip() == action_data["old_name"]
                            st.session_state.df_emp.loc[mask_emp, "Department"] = action_data["new_name"]
                            st.session_state.df_emp.loc[mask_emp, "Last Updated"] = datetime.utcnow().isoformat()
                            
                            renamed_count += 1
                        
                        elif action == "merge":
                            # Move employees to target department
                            mask_emp = st.session_state.df_emp["Department"].astype(str).str.strip() == action_data["old_name"]
                            st.session_state.df_emp.loc[mask_emp, "Department"] = action_data["target"]
                            st.session_state.df_emp.loc[mask_emp, "Last Updated"] = datetime.utcnow().isoformat()
                            
                            # Delete source department
                            st.session_state.df_dept = st.session_state.df_dept[st.session_state.df_dept["Dept ID"] != dept_id]
                            
                            merged_count += 1
                        
                        elif action == "merge_two":
                            # Merge two departments into one (possibly with new name)
                            dept1_name = action_data["dept1_name"]
                            dept2_name = action_data["dept2_name"]
                            final_name = action_data["final_name"]
                            delete_id = action_data["delete_id"]
                            keep_id = action_data["dept1_id"] if delete_id == action_data["dept2_id"] else action_data["dept2_id"]
                            
                            # Update the kept department's name to final name
                            mask_dept = st.session_state.df_dept["Dept ID"] == keep_id
                            st.session_state.df_dept.loc[mask_dept, "Department Name"] = final_name
                            st.session_state.df_dept.loc[mask_dept, "Description"] = f"Merged from: {dept1_name}, {dept2_name}"
                            
                            # Update all employees from both departments to use final name
                            mask_emp1 = st.session_state.df_emp["Department"].astype(str).str.strip() == dept1_name
                            mask_emp2 = st.session_state.df_emp["Department"].astype(str).str.strip() == dept2_name
                            combined_mask = mask_emp1 | mask_emp2
                            st.session_state.df_emp.loc[combined_mask, "Department"] = final_name
                            st.session_state.df_emp.loc[combined_mask, "Last Updated"] = datetime.utcnow().isoformat()
                            
                            # Delete the other department
                            st.session_state.df_dept = st.session_state.df_dept[st.session_state.df_dept["Dept ID"] != delete_id]
                            
                            merged_count += 1
                        
                        elif action == "delete":
                            # Delete department (only if no employees)
                            st.session_state.df_dept = st.session_state.df_dept[st.session_state.df_dept["Dept ID"] != dept_id]
                            deleted_count += 1
                    
                    # Save changes
                    write_workbook(EXCEL_PATH, st.session_state.df_emp, st.session_state.df_dept)
                    
                    # Show success message
                    success_msg = "🎉 Department management completed!\n\n"
                    if renamed_count > 0:
                        success_msg += f"✏️ Renamed {renamed_count} department(s)\n"
                    if merged_count > 0:
                        success_msg += f"🔀 Merged {merged_count} department(s)\n"
                    if deleted_count > 0:
                        success_msg += f"🗑️ Deleted {deleted_count} department(s)\n"
                    
                    st.success(success_msg)
                    
                    # Reset state
                    st.session_state.show_dept_manage = False
                    st.session_state.dept_manage_actions = {}
                    time.sleep(2)
                    st.rerun()
        
        with col_btn2:
            if st.button("❌ Cancel", width="stretch", key="cancel_manage_btn"):
                st.session_state.show_dept_manage = False
                st.session_state.dept_manage_actions = {}
                st.rerun()
        
        with col_btn3:
            changes_count = len(st.session_state.dept_manage_actions)
            st.metric("Pending Changes", changes_count)
    
    st.markdown("---")
    
    if st.button("🔙 Back to Main View", width="stretch"):
        st.session_state.show_dept_manage = False
        st.rerun()

st.markdown("---")

# Advanced Features Section
with st.expander("📊 Advanced Analytics & Reports"):
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        st.markdown("**👥 Users by Department**")
        if not df_dept.empty:
            dept_stats = []
            for dept_name in df_dept["Department Name"].unique():
                count = len(df_emp[df_emp['Department'] == dept_name])
                dept_stats.append({"Department": dept_name, "Users": count})
            st.dataframe(pd.DataFrame(dept_stats), hide_index=True, width="stretch")
    
    with col_a2:
        st.markdown("**📈 Status Distribution**")
        status_counts = df_emp['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        st.dataframe(status_counts, hide_index=True, width="stretch")
    
    with col_a3:
        st.markdown("**🔢 Extension Usage**")
        if not df_emp.empty:
            ext_4digit = df_emp[df_emp['Extension'].str.len() == 4]
            st.metric("4-Digit Extensions", len(ext_4digit))
            st.metric("Total Extensions", len(df_emp[df_emp['Extension'] != '']))

with st.expander("🔍 Audit Log (Last 10 Updates)"):
    if not df_emp.empty and 'Last Updated' in df_emp.columns:
        recent = df_emp[df_emp['Last Updated'] != ''].sort_values('Last Updated', ascending=False).head(10)
        if not recent.empty:
            audit_display = recent[['Row ID', 'Name', 'Employee ID', 'Department', 'Status', 'Last Updated']].copy()
            # Convert to display-friendly format
            for col in audit_display.columns:
                audit_display[col] = audit_display[col].astype(str)
            st.dataframe(audit_display, hide_index=True, width="stretch")
        else:
            st.info("No audit trail available yet")
    else:
        st.info("No audit trail available yet")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💡 <strong>Tip:</strong> You can directly edit the Excel file and click 'Reload from Excel' to sync changes.</p>
    <p style='font-size: 0.9em;'>Built with ❤️ using Streamlit | Active Directory Portal v2.3 - Enhanced Edition</p>
    <p style='font-size: 0.8em; opacity: 0.7;'>Features: User CRUD • Department Management • Search & Filter • Bulk Operations • Audit Log • Analytics</p>
</div>
""", unsafe_allow_html=True)