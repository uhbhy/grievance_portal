import streamlit as st
import datetime
import sqlite3
import pandas as pd
from io import BytesIO

#configure page
st.set_page_config(
    page_title="Grievance Submission Portal",
    page_icon="📩",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items=None
)

#create a db connection
def init_db():
    conn = sqlite3.connect('grievances.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            category TEXT,
            date_of_incident TEXT,
            description TEXT,
            file_name TEXT,
            file_data BLOB,
            submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_complaint(name, email, category, date_of_incident, description, file_name, file_data):
    conn = sqlite3.connect('grievances.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO complaints (name, email, category, date_of_incident, description, file_name, file_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, category, date_of_incident, description, file_name, file_data))
    conn.commit()
    conn.close()

def fetch_complaints():
    conn = sqlite3.connect('grievances.db')
    c = conn.cursor()
    c.execute("SELECT id, name, email, category, date_of_incident, description, file_name, file_data, submission_time FROM complaints ORDER BY submission_time DESC")
    data = c.fetchall()
    conn.close()
    return data

def complaints_log_section():
    st.subheader("📜 Complaints Log")
    complaints = fetch_complaints()

    if complaints:
        # Display complaints with a delete button for each
        for complaint in complaints:
            complaint_id, name, email, category, date_of_incident, description, file_name, file_data, submission_time = complaint
            
            with st.expander(f"Complaint ID {complaint_id} - {category} by {name}"):
                st.write(f"**Name:** {name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Category:** {category}")
                st.write(f"**Date of Incident:** {date_of_incident}")
                st.write(f"**Description:** {description}")
                
                if file_data and file_name:
                    file_bytes = BytesIO(file_data)
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        st.image(file_bytes, caption=file_name, use_container_width=True)
                    else:
                        st.download_button(
                            label="📎 Download Attachment",
                            data=file_bytes,
                            file_name=file_name,
                        )
                st.write(f"**Submitted At:** {submission_time}")

                # Add a Delete button with a unique key
                if st.button("Remove Complaint", key=f"delete_{complaint_id}"):
                    delete_complaint(complaint_id)
                    st.success(f"Complaint ID {complaint_id} removed successfully.")
                    st.rerun()  # Rerun to refresh the complaints log
    else:
        st.info("No complaints have been submitted yet...")


def delete_complaint(complaint_id):
    conn = sqlite3.connect('grievances.db')
    c = conn.cursor()
    c.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()


def main():
    init_db()

    st.title("📩 Grievance Submission Portal")

    st.sidebar.image("Grievance-Redressal-Cell.jpg",use_container_width=True)

    menu=["Submit a complaint","Complaints log"]
    choice=st.sidebar.selectbox("",menu)

    if choice=="Submit a complaint":
        # Create a form
        with st.form("Complaint_form"):
            st.subheader("Enter details here...")

            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            category = st.selectbox("Category of Grievance", ["Emotional Negligence 💔", "Communication Breakdown 📵", "Quality Time Deficit 🕰️","Unfulfilled Promises 🎯", "Other"])
            date_of_incident = st.date_input("Date of Incident", value=datetime.date.today())
            description = st.text_area("Description of the Issue", height=150)
            attachment = st.file_uploader("Attach relevant documents/screenshots (optional)")

            submitted = st.form_submit_button("Submit Grievance")

        #checking if submit button is clicked
            if submitted:
                #if submitted check if required fields are provided
                if name and email and description:
                    if attachment:
                        file_name = attachment.name
                        file_data = attachment.getvalue()
                    else:
                        file_name = None
                        file_data = None
                    insert_complaint(name, email, category, str(date_of_incident), description, file_name,file_data)
                    st.success("✅ Grievance submitted successfully!")
                    st.write("**Name:**", name)
                    st.write("**Email:**", email)
                    st.write("**Category:**", category)
                    st.write("**Date of Incident:**", date_of_incident)
                    st.write("**Description:**", description)

                    if attachment:
                        if attachment.type.startswith('image/'):
                            st.image(attachment, caption=attachment.name, use_container_width=True)
                        else:
                            st.info(f"Attached file: {attachment.name}")

                #if not submitted ask to resubmit with all necessary fields
                else:
                    st.warning("⚠️ Please fill in all required fields (Name, Email, and Description).")
    if choice=="Complaints log":
        complaints_log_section()
        

if __name__=="__main__":
    main()
