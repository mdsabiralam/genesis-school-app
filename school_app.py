import streamlit as st
import pandas as pd

# ১. পেজ কনফিগারেশন (Page Configuration)
st.set_page_config(
    page_title="Genesis English School",
    page_icon="🎓",
    layout="wide"
)

# ২. সেশন স্টেট (ডেটা মেমোরিতে রাখা - যাতে পেজ রিলোড হলে ডেটা না হারায়)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ছাত্র-ছাত্রীদের ডিফল্ট তালিকা
if 'students' not in st.session_state:
    st.session_state.students = [
        {"Name": "Rahim Sheikh", "Class": "Class 5", "Roll": "01", "Guardian": "Karim Sheikh", "Contact": "01711223344"},
        {"Name": "Sadia Akhtar", "Class": "Class 4", "Roll": "05", "Guardian": "Abdur Rahman", "Contact": "01911223344"}
    ]

# শিক্ষকদের ডিফল্ট তালিকা
if 'teachers' not in st.session_state:
    st.session_state.teachers = [
        {"Name": "Mr. Ahmed", "Subject": "English", "Qualification": "M.A in English"},
        {"Name": "Ms. Farzana", "Subject": "Mathematics", "Qualification": "B.Sc (Math)"}
    ]

# ৩. সাইডবার মেনু (Sidebar Menu)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/201/201614.png", width=50)
    st.title("Genesis School")
    st.write("Enlightening the Future")
    st.markdown("---")
    
    # নেভিগেশন মেনু
    menu = st.radio("Navigation", ["Home", "About Us", "Admin Portal"])
    
    st.markdown("---")
    # লগআউট বাটন (যদি লগইন করা থাকে)
    if st.session_state.logged_in:
        st.success("✅ Admin Logged In")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# ৪. মেইন পেজ কন্টেন্ট (Main Page Content)

# >>> হোম পেজ (Home) <<<
if menu == "Home":
    st.title("Welcome to Genesis English School 🎓")
    st.image("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-1.2.1&auto=format&fit=crop&w=1200&q=80", caption="Our Campus")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Principal's Message")
        st.info('"Our goal is not just academic excellence, but to mold children with strong moral values."')
    with col2:
        st.subheader("Why Choose Us?")
        st.write("✅ Experienced Faculty")
        st.write("✅ Modern Computer Lab")
        st.write("✅ Spacious Playground")

# >>> আমাদের কথা (About Us) <<<
elif menu == "About Us":
    st.header("About Genesis English School")
    st.write("Established in 2025, we are committed to providing world-class education following the National Curriculum in English Medium.")
    
    st.subheader("Admission Information")
    st.warning("📢 Admission is currently OPEN for Play Group to Class 5")
    
    st.subheader("Contact Us")
    st.markdown("📍 **Address:** College Road, Dinajpur")
    st.markdown("📞 **Phone:** +880 1711-223344")

# >>> অ্যাডমিন লগইন এবং ড্যাশবোর্ড (Admin Portal) <<<
elif menu == "Admin Portal":
    
    # যদি লগইন না করা থাকে -> লগইন ফর্ম দেখাবে
    if not st.session_state.logged_in:
        st.header("🔐 Staff Login")
        with st.form("login_form"):
            username = st.text_input("Username (Type 'admin')")
            password = st.text_input("Password (Type '1234')", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if username == "admin" and password == "1234":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Incorrect Username or Password")
    
    # যদি লগইন করা থাকে -> ড্যাশবোর্ড দেখাবে
    else:
        st.header("📊 Admin Dashboard")
        
        # ট্যাব তৈরি করা হয়েছে আলাদা সেকশনের জন্য
        tab1, tab2 = st.tabs(["👨‍🎓 Student Management", "👨‍🏫 Teachers List"])
        
        # --- ছাত্র ব্যবস্থাপনা ট্যাব ---
        with tab1:
            st.subheader("Add New Student")
            # নতুন ছাত্র যোগ করার ফর্ম
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Student Name")
                    roll = st.text_input("Roll No")
                    guardian = st.text_input("Guardian Name")
                with col2:
                    s_class = st.selectbox("Class", ["Play", "Nursery", "Class 1", "Class 2", "Class 3", "Class 4", "Class 5"])
                    contact = st.text_input("Contact No")
                
                if st.form_submit_button("Save Student"):
                    if name and roll:
                        new_student = {
                            "Name": name, "Class": s_class, "Roll": roll,
                            "Guardian": guardian, "Contact": contact
                        }
                        st.session_state.students.append(new_student)
                        st.success("Student added successfully!")
                        st.rerun()
                    else:
                        st.error("Name and Roll are required.")
            
            st.divider()
            st.subheader("All Students List")
            
            # ছাত্র তালিকা প্রদর্শন (টেবিল আকারে)
            if st.session_state.students:
                df = pd.DataFrame(st.session_state.students)
                st.dataframe(df, use_container_width=True)
                
                # ডিলিট করার অপশন
                st.write("---")
                delete_student = st.selectbox("Select Student to Remove", [s['Name'] for s in st.session_state.students])
                if st.button("Delete Selected Student"):
                    st.session_state.students = [s for s in st.session_state.students if s['Name'] != delete_student]
                    st.rerun()
            else:
                st.info("No students found.")

        # --- শিক্ষক তালিকা ট্যাব ---
        with tab2:
            st.subheader("Faculty Members")
            df_teachers = pd.DataFrame(st.session_state.teachers)
            st.dataframe(df_teachers, use_container_width=True)