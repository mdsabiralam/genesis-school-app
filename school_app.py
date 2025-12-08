import streamlit as st
import pandas as pd
from firebase_admin import initialize_app, firestore, credentials
import os
import json
from google.oauth2 import service_account
import firebase_admin 
# import pyrebase # Pyrebase is removed to fix deployment issues

# --- 1. CONFIGURATION AND FIREBASE SETUP ---
# FIX: Removed unstable Pyrebase integration logic. Reverted to Admin SDK only.
try:
    if st.secrets.get("firebase", {}):
        firestore_creds = st.secrets["firebase"]
        project_name = firestore_creds.get("project_id", "default-app-name")
        
        if 'db' not in st.session_state or st.session_state.db is None: 
            
            # Prepare Admin SDK (for Firestore) Credentials
            creds_dict = {
                "type": firestore_creds.get("type"),
                "project_id": firestore_creds.get("project_id"),
                "private_key_id": firestore_creds.get("private_key_id"),
                "private_key": firestore_creds.get("private_key").replace('\\n', '\n'), 
                "client_email": firestore_creds.get("client_email"),
                "client_id": firestore_creds.get("client_id"),
                "auth_uri": firestore_creds.get("auth_uri"),
                "token_uri": firestore_creds.get("token_uri"),
                "auth_provider_x509_cert_url": firestore_creds.get("auth_provider_x509_cert_url"),
                "client_x509_cert_url": firestore_creds.get("client_x509_cert_url"),
            }
            creds = credentials.Certificate(creds_dict)
            
            # Use try/except logic to handle the "already exists" error gracefully
            firebase_app = None
            try:
                firebase_app = initialize_app(creds, name=project_name)
            except ValueError:
                # App already exists, retrieve the existing app instance
                firebase_app = firebase_admin.get_app(name=project_name)

            db = firestore.client(firebase_app)
            st.session_state.db = db
            
            # Pyrebase initialization code removed
            st.success("Connected to Firebase Firestore successfully! (Authentication is hardcoded)")

        elif 'db' not in st.session_state:
             st.session_state.db = firestore.client(firebase_admin.get_app(project_name))

    else:
        st.warning("Firebase credentials not found. Using temporary in-memory store.")
        st.session_state.db = None 
        st.session_state.temp_data = {
            'students': [
                {'Name': 'Rajesh Mandal', 'Class': 'Class 10', 'Roll No.': 101, 'id': 's1'},
                {'Name': 'Priyanka Das', 'Class': 'Class 9', 'Roll No.': 102, 'id': 's2'},
            ],
            'teachers': [
                {'Name': 'Mr. Aniruddha Sen', 'Subject': 'Math', 'id': 't1'},
                {'Name': 'Mrs. Rehana Khatun', 'Subject': 'English', 'id': 't2'},
            ]
        }

except Exception as e:
    st.error(f"Error during Firebase setup: {e}. Please check your secrets.")
    st.session_state.db = None
    st.session_state.temp_data = {} 


# --- 2. DATA MANAGEMENT FUNCTIONS (UNCHANGED) ---

FIRESTORE_COLLECTION_NAME = "school_data"

def load_data(data_type):
    """Loads data from Firestore or temporary store."""
    if st.session_state.db:
        try:
            docs = st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).stream()
            data = [doc.to_dict() for doc in docs]
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error loading data from Firestore: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame(st.session_state.temp_data.get(data_type, []))

def save_data(data_type, new_entry):
    """Saves new data to Firestore or temporary store."""
    if st.session_state.db:
        try:
            doc_ref = st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).document()
            new_entry['id'] = doc_ref.id 
            doc_ref.set(new_entry)
            st.success(f"New {data_type} data saved successfully!")
        except Exception as e:
            st.error(f"Failed to save data to Firestore: {e}")
    else:
        data = st.session_state.temp_data[data_type]
        new_entry['id'] = str(len(data) + 1)
        data.append(new_entry)
        st.session_state.temp_data[data_type] = data
        st.success(f"New {data_type} data saved temporarily!")

def delete_data(data_type, row_id):
    """Deletes data from Firestore or temporary store."""
    if st.session_state.db:
        try:
            st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).document(row_id).delete()
            st.success(f"Data successfully deleted.")
        except Exception as e:
            st.error(f"Failed to delete data from Firestore: {e}")
    else:
        data = st.session_state.temp_data[data_type]
        st.session_state.temp_data[data_type] = [item for item in data if item.get('id') != row_id]
        st.success(f"Data successfully deleted from temporary store.")

# --- 3. UI FUNCTIONS AND AUTHENTICATION LOGIC (Hardcoded Login) ---

st.set_page_config(layout="wide", page_title="Genesis English School Portal")

def home_page():
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Genesis English School 🎓</h1>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏫 Our Campus")
        st.info("Principal's Message")
        st.markdown(
            """
            <div style="background-color: #e6f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                <p style="font-style: italic; margin: 0;'>
                "Our goal is not just academic excellence, but fostering strong moral values in children."
                </p>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.subheader("✅ Why Choose Us?")
        st.markdown("""
        - **Experienced Faculty**
        - **Modern Computer Lab**
        - **Spacious Playground**
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌐 Contact")
    st.write("Address: 10/A, Shantiniketan Road, Kolkata - 700032")
    st.write("Phone: (033) XXXX-XXXX")

def about_us_page():
    st.markdown("<h1 style='color: #1f77b4;'>About Us</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Our Mission and Vision")
    st.write("Genesis English School is committed to providing world-class education in a safe, supportive, and stimulating environment.")
    st.subheader("History")
    st.write("Established in 2005, Genesis English School is recognized as one of the best educational institutions in the city.")
    st.subheader("Contact Information")
    st.markdown("""
    - **Email:** info@genesisschool.edu
    - **Address:** 10/A, Shantiniketan Road, Kolkata - 700032
    """)

def admin_portal():
    st.markdown("<h1 style='color: #1f77b4;'>Admin Portal</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('logged_in', False):
        st.subheader("🔐 Staff Login")
        
        # Reverted to simple hardcoded login
        with st.form("login_form"):
            email_input = st.text_input("Username (admin)")
            password_input = st.text_input("Password (1234)", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if email_input == "admin" and password_input == "1234":
                    st.session_state.logged_in = True
                    st.session_state.user_info = {'email': 'admin@genesis.edu'} # Mock user info
                    st.rerun()
                else:
                    st.error("Login Failed: Invalid username or password.")
        
        st.markdown("---")
        if not st.session_state.db:
            st.warning("Data is currently saved only temporarily. To make it permanent, ensure Firebase is configured.")

    else:
        st.success(f"Logged In Successfully as: {st.session_state.user_info['email']}")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_info = {}
            st.rerun()
            
        st.markdown("---")
        
        # --- Data Management Tabs ---
        tab1, tab2 = st.tabs(["👨‍🎓 Student Management", "👨‍🏫 Teachers List"])
        
        with tab1:
            st.subheader("Student Data")
            students_df = load_data('students')
            if not students_df.empty: st.dataframe(students_df[['Name', 'Class', 'Roll No.']], use_container_width=True)
            else: st.info("No student data found.")
            
            st.markdown("#### Add New Student")
            with st.form("add_student_form"):
                new_name = st.text_input("Name", key="s_name")
                new_class = st.selectbox("Class", options=['Class 8', 'Class 9', 'Class 10'], key="s_class")
                new_roll = st.number_input("Roll No.", min_value=1, key="s_roll")
                add_submitted = st.form_submit_button("Add Student")
                
                if add_submitted and new_name:
                    new_student = {'Name': new_name, 'Class': new_class, 'Roll No.': new_roll}
                    save_data('students', new_student)
                    st.rerun()

            st.markdown("#### Delete Data")
            if not students_df.empty:
                with st.form("delete_student_form"):
                    delete_options = students_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1).tolist()
                    delete_selection = st.selectbox("Select Student to Delete", options=delete_options, key="s_delete_select")
                    delete_id = None
                    try: delete_id = students_df.loc[students_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1) == delete_selection, 'id'].iloc[0]
                    except IndexError: pass
                    delete_submitted = st.form_submit_button("Delete Selected Student")
                    
                    if delete_submitted and delete_id:
                        delete_data('students', delete_id)
                        st.rerun()

        with tab2:
            st.subheader("Teachers Data")
            teachers_df = load_data('teachers')
            if not teachers_df.empty: st.dataframe(teachers_df[['Name', 'Subject']], use_container_width=True)
            else: st.info("No teacher data found.")

            st.markdown("#### Add New Teacher")
            with st.form("add_teacher_form"):
                t_name = st.text_input("Name", key="t_name")
                t_subject = st.text_input("Subject", key="t_subject")
                t_add_submitted = st.form_submit_button("Add Teacher")
                
                if t_add_submitted and t_name:
                    new_teacher = {'Name': t_name, 'Subject': t_subject}
                    save_data('teachers', new_teacher)
                    st.rerun()
            
            st.markdown("#### Delete Data")
            if not teachers_df.empty:
                with st.form("delete_teacher_form"):
                    delete_options = teachers_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1).tolist()
                    delete_selection = st.selectbox("Select Teacher to Delete", options=delete_options, key="t_delete_select")
                    delete_id = None
                    try: delete_id = teachers_df.loc[teachers_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1) == delete_selection, 'id'].iloc[0]
                    except IndexError: pass
                    t_delete_submitted = st.form_submit_button("Delete Selected Teacher")
                    
                    if t_delete_submitted and delete_id:
                        delete_data('teachers', delete_id)
                        st.rerun()

# --- 4. NAVIGATION ---
PAGES = {
    "Home": home_page,
    "About Us": about_us_page,
    "Admin Portal": admin_portal
}

st.sidebar.title("Menu")
selection = st.sidebar.radio("Select Page:", list(PAGES.keys()))
PAGES[selection]()
