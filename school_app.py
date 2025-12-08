import streamlit as st
import pandas as pd
from firebase_admin import initialize_app, firestore, credentials
import os
import json
from google.oauth2 import service_account

# --- 1. CONFIGURATION AND FIREBASE SETUP ---
# Get Firebase config and initial auth token from the environment variables
# These are provided automatically in the Canvas environment.
try:
    # 1. Check for Firebase credentials in Streamlit Secrets
    if "firestore_creds" not in st.session_state:
        # Check if secrets are available (for Streamlit Cloud deployment)
        if st.secrets.get("firebase", {}):
            st.session_state.firestore_creds = st.secrets["firebase"]
            
            # --- Initialize Firebase Admin SDK using secrets ---
            # Streamlit secrets are securely loaded into st.secrets object.
            
            # Create a credential object from the secrets data
            creds = credentials.Certificate(dict(st.session_state.firestore_creds))
            
            # Initialize the Firebase App (only if not already initialized)
            # The 'name' parameter is necessary to avoid re-initialization error
            if not initialize_app(creds, name=st.session_state.firestore_creds.get("project_id", "default-app-name")):
                initialize_app(creds, name=st.session_state.firestore_creds["project_id"])
            
            # Get the Firestore client
            db = firestore.client()
            st.session_state.db = db
            st.success("Connected to Firebase Firestore successfully!")

        else:
            # Fallback to in-memory store if no secrets are found
            st.warning("Firebase credentials not found. Using temporary in-memory store.")
            st.session_state.db = None # Mark as no real DB connection
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
    st.session_state.temp_data = {} # Ensure temp data exists as fallback

# --- 2. DATA MANAGEMENT FUNCTIONS ---

FIRESTORE_COLLECTION_NAME = "school_data"

def load_data(data_type):
    """Loads data from Firestore or temporary store."""
    if st.session_state.db:
        # Load from Firestore (Real Persistence)
        docs = st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).stream()
        data = [doc.to_dict() for doc in docs]
        return pd.DataFrame(data)
    else:
        # Load from temporary store
        return pd.DataFrame(st.session_state.temp_data.get(data_type, []))

def save_data(data_type, new_entry):
    """Saves new data to Firestore or temporary store."""
    if st.session_state.db:
        # Save to Firestore (Real Persistence)
        try:
            doc_ref = st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).document()
            new_entry['id'] = doc_ref.id # Use Firestore generated ID
            doc_ref.set(new_entry)
            st.success(f"New {data_type} data saved successfully!")
        except Exception as e:
            st.error(f"Failed to save data to Firestore: {e}")
    else:
        # Save to temporary store
        data = st.session_state.temp_data[data_type]
        new_entry['id'] = str(len(data) + 1)
        data.append(new_entry)
        st.session_state.temp_data[data_type] = data
        st.success(f"New {data_type} data saved temporarily!")

def delete_data(data_type, row_id):
    """Deletes data from Firestore or temporary store."""
    if st.session_state.db:
        # Delete from Firestore (Real Persistence)
        try:
            st.session_state.db.collection(FIRESTORE_COLLECTION_NAME).document("main_data").collection(data_type).document(row_id).delete()
            st.success(f"Data successfully deleted.")
        except Exception as e:
            st.error(f"Failed to delete data from Firestore: {e}")
    else:
        # Delete from temporary store
        data = st.session_state.temp_data[data_type]
        st.session_state.temp_data[data_type] = [item for item in data if item.get('id') != row_id]
        st.success(f"Data successfully deleted from temporary store.")

# --- 3. PAGE CONFIGURATION AND FUNCTIONS ---

st.set_page_config(layout="wide", page_title="Genesis English School Portal")

# Load initial data (This will now attempt to load from the real DB if connected)
INITIAL_STUDENTS = load_data('students')
INITIAL_TEACHERS = load_data('teachers')

def home_page():
    """Home Page - School Introduction"""
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
    """About Us Page"""
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
    """Admin Panel and Login Management"""

    st.markdown("<h1 style='color: #1f77b4;'>Admin Portal</h1>", unsafe_allow_html=True)
    
    # --- Login Simulation ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 Admin Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Simple Hardcoded Login for demo
                if username == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()
                else:
                    st.error("Invalid Username or Password.")
        
        st.markdown("---")
        if not st.session_state.db:
            st.warning("Data is currently saved only temporarily. To make it permanent, please ensure Firebase is configured.")

    else:
        st.success("Logged In Successfully!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()
            
        st.markdown("---")
        
        # --- Data Management Tabs ---
        tab1, tab2 = st.tabs(["👨‍🎓 Student Management", "👨‍🏫 Teachers List"])
        
        with tab1:
            st.subheader("Student Data")
            
            # Load Data
            students_df = load_data('students')
            
            if not students_df.empty:
                st.dataframe(students_df[['Name', 'Class', 'Roll No.']], use_container_width=True)
            else:
                st.info("No student data found.")
            
            st.markdown("#### Add New Student")
            with st.form("add_student_form"):
                new_name = st.text_input("Name", key="s_name")
                new_class = st.selectbox("Class", options=['Class 8', 'Class 9', 'Class 10'], key="s_class")
                new_roll = st.number_input("Roll No.", min_value=1, key="s_roll")
                
                add_submitted = st.form_submit_button("Add Student")
                
                if add_submitted and new_name:
                    new_student = {
                        'Name': new_name,
                        'Class': new_class,
                        'Roll No.': new_roll
                    }
                    save_data('students', new_student)
                    st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()

            st.markdown("#### Delete Data")
            if not students_df.empty:
                with st.form("delete_student_form"):
                    # Use 'id' column for deletion as it contains the Firestore Document ID
                    delete_options = students_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1).tolist()
                    delete_selection = st.selectbox("Select Student to Delete", options=delete_options, key="s_delete_select")
                    
                    # Extract the ID from the selected option
                    delete_id = None
                    try:
                        delete_id = students_df.loc[students_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1) == delete_selection, 'id'].iloc[0]
                    except IndexError:
                         pass # Allow empty selection without error

                    delete_submitted = st.form_submit_button("Delete Selected Student")
                    
                    if delete_submitted and delete_id:
                        delete_data('students', delete_id)
                        st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()

        with tab2:
            st.subheader("Teachers Data")
            
            # Load Data
            teachers_df = load_data('teachers')
            
            if not teachers_df.empty:
                 st.dataframe(teachers_df[['Name', 'Subject']], use_container_width=True)
            else:
                 st.info("No teacher data found.")

            st.markdown("#### Add New Teacher")
            with st.form("add_teacher_form"):
                t_name = st.text_input("Name", key="t_name")
                t_subject = st.text_input("Subject", key="t_subject")
                
                t_add_submitted = st.form_submit_button("Add Teacher")
                
                if t_add_submitted and t_name:
                    new_teacher = {
                        'Name': t_name,
                        'Subject': t_subject
                    }
                    save_data('teachers', new_teacher)
                    st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()
            
            st.markdown("#### Delete Data")
            if not teachers_df.empty:
                with st.form("delete_teacher_form"):
                    delete_options = teachers_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1).tolist()
                    delete_selection = st.selectbox("Select Teacher to Delete", options=delete_options, key="t_delete_select")
                    
                    delete_id = None
                    try:
                        delete_id = teachers_df.loc[teachers_df.apply(lambda row: f"{row['Name']} ({row.get('id', 'N/A')})", axis=1) == delete_selection, 'id'].iloc[0]
                    except IndexError:
                         pass # Allow empty selection without error

                    t_delete_submitted = st.form_submit_button("Delete Selected Teacher")
                    
                    if t_delete_submitted and delete_id:
                        delete_data('teachers', delete_id)
                        st.rerun() # Corrected: st.experimental_rerun() -> st.rerun()

# --- 4. NAVIGATION ---
PAGES = {
    "Home": home_page,
    "About Us": about_us_page,
    "Admin Portal": admin_portal
}

st.sidebar.title("Menu")
selection = st.sidebar.radio("Select Page:", list(PAGES.keys()))
PAGES[selection]()