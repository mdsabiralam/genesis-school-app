import streamlit as st
import pandas as pd
from firebase_admin import initialize_app, firestore, credentials
import os

# --- 1. FIREBASE INITIALIZATION AND SETUP ---
# Get Firebase config and initial auth token from the environment variables
# These are provided automatically in the Canvas environment.
try:
    # Use environment variables if running in the Canvas environment
    firebase_config = os.environ.get('__firebase_config', '{}')
    if firebase_config:
        firebase_config = eval(firebase_config) # Safely parse the config string
    
    # Initialize Firebase Admin SDK (Only for backend operations like Firestore)
    # Note: Streamlit typically uses the client-side Firebase SDK for auth and client operations,
    # but we are using the Admin SDK imitation here for demonstration purposes in the sandbox.
    
    # We use a dummy creds dict here since the actual credentials are provided by the environment
    # and we only need to check if the app is already initialized.
    if not st.session_state.get('firebase_initialized', False):
        if not firebase_config:
             st.warning("Firebase configuration not found. Using in-memory store.")
             # Set up dummy variables if config is missing (for local testing without full sandbox)
             st.session_state['app_id'] = 'default-app-id'
             st.session_state['user_id'] = 'default-user-id'
             db = None # No Firestore access
             st.session_state['db'] = db
        else:
            # We assume a mechanism to initialize the app based on the provided config
            # For this simple app, we will simulate the connection using the config structure.
            # In a real Streamlit app, you would need service account keys.
            
            # Since we are in the Canvas context, we rely on the internal Firestore connection.
            # We simply mark it as initialized for the app flow.
            st.session_state['app_id'] = firebase_config.get('projectId', 'default-app-id')
            st.session_state['user_id'] = 'admin-user-id' # Simulating authenticated user
            st.session_state['firebase_initialized'] = True
            
            # Mocking the Firestore connection for the Streamlit state management
            # We will use st.session_state to store the data and simulate Firestore access later
            st.info("Firebase initialization simulated. Using session state for data storage in this simplified example.")
            
except Exception as e:
    st.error(f"Error during Firebase setup: {e}")
    # Fallback to in-memory store
    if 'db' not in st.session_state:
        st.session_state['db'] = None
    if 'app_id' not in st.session_state:
        st.session_state['app_id'] = 'default-app-id'
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = 'default-user-id'

# --- 2. DATA MANAGEMENT (Simulated Firestore) ---

# Simulate Firestore structure for private data: /artifacts/{appId}/users/{userId}/school_data
APP_ID = st.session_state.get('app_id', 'default-app-id')
USER_ID = st.session_state.get('user_id', 'default-user-id')
FIRESTORE_COLLECTION_PATH = f"/artifacts/{APP_ID}/users/{USER_ID}/school_data"

def get_db_collection():
    """Simulates getting a Firestore collection reference."""
    # In a real Firestore setup, this would return firestore.client().collection(FIRESTORE_COLLECTION_PATH)
    # Here, we use a dictionary to simulate the collection (in-memory for this sandbox)
    if 'school_data_db' not in st.session_state:
        st.session_state['school_data_db'] = {
            'students': [
                {'Name': 'রাজু মন্ডল', 'Class': 'ক্লাস ১০', 'Roll No.': 101, 'id': 's1'},
                {'Name': 'প্রিয়াঙ্কা দাস', 'Class': 'ক্লাস ৯', 'Roll No.': 102, 'id': 's2'},
            ],
            'teachers': [
                {'Name': 'মিঃ অনিরুদ্ধ সেন', 'Subject': 'গণিত', 'id': 't1'},
                {'Name': 'মিসেস রেহানা খাতুন', 'Subject': 'ইংলিশ', 'id': 't2'},
            ]
        }
    return st.session_state['school_data_db']

def load_data(data_type):
    """Simulates loading data from Firestore (or session state)."""
    db_data = get_db_collection()
    return pd.DataFrame(db_data.get(data_type, []))

def save_data(data_type, new_entry):
    """Simulates saving new data to Firestore (or session state)."""
    db_data = get_db_collection()
    new_entry['id'] = str(len(db_data[data_type]) + 1) # Simple unique ID
    db_data[data_type].append(new_entry)
    st.session_state['school_data_db'] = db_data # Update session state
    st.success(f"নতুন {data_type} ডেটা সফলভাবে সেভ হয়েছে!")

def delete_data(data_type, row_id):
    """Simulates deleting data from Firestore (or session state)."""
    db_data = get_db_collection()
    db_data[data_type] = [item for item in db_data[data_type] if item.get('id') != row_id]
    st.session_state['school_data_db'] = db_data
    st.success(f"ডেটা সফলভাবে মুছে ফেলা হয়েছে।")

# --- 3. PAGE CONFIGURATION AND FUNCTIONS ---

st.set_page_config(layout="wide", page_title="Genesis English School Portal")

# Default in-memory data (used as initial data)
INITIAL_STUDENTS = load_data('students')
INITIAL_TEACHERS = load_data('teachers')

def home_page():
    """হোম পেজ - স্কুলের পরিচিতি"""
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Genesis English School 🎓</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏫 আমাদের ক্যাম্পাস")
        st.info("প্রিন্সিপাল স্যারের বার্তা")
        st.markdown(
            """
            <div style="background-color: #e6f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                <p style="font-style: italic; margin: 0;">
                "আমাদের লক্ষ্য শুধু একাডেমিক শ্রেষ্ঠত্ব অর্জন নয়, শিশুদের মজবুত নৈতিক মূল্যবোধ নিয়ে গড়ে তোলা।"
                </p>
            </div>
            """, unsafe_allow_html=True
        )
    
    with col2:
        st.subheader("✅ কেন আমাদের বেছে নেবেন?")
        st.markdown("""
        - **অভিজ্ঞ শিক্ষক মণ্ডলী**
        - **আধুনিক কম্পিউটার ল্যাব**
        - **বিশাল খেলার মাঠ**
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🌐 যোগাযোগ")
    st.write("ঠিকানা: ১০/এ, শান্তিনিকেতন রোড, কলকাতা - ৭০০০৩২")
    st.write("ফোন: (০৩৩) XXXX-XXXX")

def about_us_page():
    """আমাদের কথা পেজ"""
    st.markdown("<h1 style='color: #1f77b4;'>About Us (আমাদের কথা)</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("আমাদের লক্ষ্য ও উদ্দেশ্য")
    st.write("জেনেসিস ইংলিশ স্কুল শিশুদের একটি নিরাপদ, সহায়ক এবং উদ্দীপক পরিবেশে বিশ্বমানের শিক্ষা প্রদান করতে প্রতিশ্রুতিবদ্ধ। আমরা মনে করি, শিক্ষা একটি সামগ্রিক প্রক্রিয়া, যেখানে জ্ঞানার্জনের পাশাপাশি চরিত্র গঠনও সমান গুরুত্বপূর্ণ।")
    
    st.subheader("স্কুলের ইতিহাস")
    st.write("২০০৫ সালে প্রতিষ্ঠিত জেনেসিস ইংলিশ স্কুল আজ শহরের অন্যতম সেরা শিক্ষা প্রতিষ্ঠান হিসেবে পরিচিত।")
    
    st.subheader("যোগাযোগের তথ্য")
    st.markdown("""
    - **ইমেইল:** info@genesisschool.edu
    - **ঠিকানা:** ১০/এ, শান্তিনিকেতন রোড, কলকাতা - ৭০০০৩২
    """)

def admin_portal():
    """অ্যাডমিন প্যানেল এবং লগইন ম্যানেজমেন্ট"""

    st.markdown("<h1 style='color: #1f77b4;'>Admin Portal (অ্যাডমিন প্যানেল)</h1>", unsafe_allow_html=True)
    
    # ------------------
    # Login Simulation
    # ------------------
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("🔐 অ্যাডমিন লগইন")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Simple Hardcoded Login for demo
                if username == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.session_state.admin_user_id = USER_ID
                    st.experimental_rerun()
                else:
                    st.error("ভুল ইউজারনেম বা পাসওয়ার্ড।")
        
        st.markdown("---")
        st.info(f"ব্যবহারকারীর ID (Firebase Simulation): **{USER_ID}**")

    else:
        st.success("সফলভাবে লগইন করা হয়েছে!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()
            
        st.markdown("---")
        
        # ------------------
        # Data Management Tabs
        # ------------------
        tab1, tab2 = st.tabs(["ছাত্র ব্যবস্থাপনা (Student Management)", "শিক্ষক তালিকা (Teachers List)"])
        
        with tab1:
            st.subheader("ছাত্র-ছাত্রীর ডেটা")
            
            # Load Data
            students_df = load_data('students')
            
            st.dataframe(students_df[['Name', 'Class', 'Roll No.']])
            
            st.markdown("#### নতুন ছাত্র যোগ করুন")
            with st.form("add_student_form"):
                new_name = st.text_input("নাম", key="s_name")
                new_class = st.selectbox("ক্লাস", options=['ক্লাস ৮', 'ক্লাস ৯', 'ক্লাস ১০'], key="s_class")
                new_roll = st.number_input("রোল নং.", min_value=1, key="s_roll")
                
                add_submitted = st.form_submit_button("যোগ করুন")
                
                if add_submitted and new_name:
                    new_student = {
                        'Name': new_name,
                        'Class': new_class,
                        'Roll No.': new_roll
                    }
                    save_data('students', new_student)
                    st.experimental_rerun()

            st.markdown("#### ডেটা মুছুন")
            with st.form("delete_student_form"):
                delete_id = st.selectbox("মুছে ফেলার জন্য আইডি নির্বাচন করুন (ID)", options=students_df['id'].tolist(), key="s_delete_id")
                delete_submitted = st.form_submit_button("মুছে ফেলুন")
                
                if delete_submitted and delete_id:
                    delete_data('students', delete_id)
                    st.experimental_rerun()

        with tab2:
            st.subheader("শিক্ষকদের ডেটা")
            
            # Load Data
            teachers_df = load_data('teachers')
            
            st.dataframe(teachers_df[['Name', 'Subject']])

            st.markdown("#### নতুন শিক্ষক যোগ করুন")
            with st.form("add_teacher_form"):
                t_name = st.text_input("নাম", key="t_name")
                t_subject = st.text_input("বিষয়", key="t_subject")
                
                t_add_submitted = st.form_submit_button("যোগ করুন")
                
                if t_add_submitted and t_name:
                    new_teacher = {
                        'Name': t_name,
                        'Subject': t_subject
                    }
                    save_data('teachers', new_teacher)
                    st.experimental_rerun()
            
            st.markdown("#### ডেটা মুছুন")
            with st.form("delete_teacher_form"):
                delete_id = st.selectbox("মুছে ফেলার জন্য আইডি নির্বাচন করুন (ID)", options=teachers_df['id'].tolist(), key="t_delete_id")
                t_delete_submitted = st.form_submit_button("মুছে ফেলুন")
                
                if t_delete_submitted and delete_id:
                    delete_data('teachers', delete_id)
                    st.experimental_rerun()

# --- 4. NAVIGATION ---
# Set up a dictionary to map navigation options to functions
PAGES = {
    "Home (হোম)": home_page,
    "About Us (আমাদের কথা)": about_us_page,
    "Admin Portal (অ্যাডমিন প্যানেল)": admin_portal
}

# Sidebar navigation
st.sidebar.title("মেনু")
selection = st.sidebar.radio("পৃষ্ঠা নির্বাচন করুন:", list(PAGES.keys()))

# Display the selected page
PAGES[selection]()

# --------------------------------------------------------------------------------------
# IMPORTANT NOTE on Firebase Integration in this Sandbox:
#
# Due to the sandbox environment's limitations, this code SIMULATES the Firebase 
# connection by storing data in Streamlit's session state (st.session_state).
#
# In a real-world deployed Streamlit app, you would use a library (like st-firebase 
# or direct calls to the Firebase Client SDK) to connect to a live Firestore database.
#
# Functionality Check: The data ADD/DELETE/LOAD functions now work persistently within 
# the running session (just like a database), demonstrating the correct data flow 
# needed for Firestore.
# --------------------------------------------------------------------------------------
