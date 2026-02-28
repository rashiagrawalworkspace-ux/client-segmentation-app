import streamlit as st
import pandas as pd
from pymongo import MongoClient

# --- 1. App Configuration ---
st.set_page_config(page_title="Client Segmentation", page_icon="💎", layout="centered")
st.markdown("""<style>div.row-widget.stRadio > div { flex-direction:row; flex-wrap: wrap; gap: 10px; }</style>""", unsafe_allow_html=True)

INPUT_FILE = "unsegmented_contacts.csv"

# --- 2. Database Connection ---
@st.cache_resource
def init_connection():
    # Connects to MongoDB using the secret URI we put in Streamlit settings
    return MongoClient(st.secrets["MONGO_URI"])

client = init_connection()
# Create a database called 'CoutureDB' and a collection (table) called 'LabeledClients'
db = client.CoutureDB
collection = db.LabeledClients

# --- 3. Data Loading & Smart Resume ---
@st.cache_data
def load_data():
    return pd.read_csv(INPUT_FILE)

df_input = load_data()
total_contacts = len(df_input)

# Ask MongoDB how many clients have already been labeled to set the bookmark
labeled_count = collection.count_documents({})

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = labeled_count

# --- 4. The User Interface ---
st.title("Client Segmentation Portal 💎")
st.progress(st.session_state.current_idx / total_contacts if total_contacts > 0 else 0)
st.caption(f"Progress: {st.session_state.current_idx} out of {total_contacts} done")

if st.session_state.current_idx < total_contacts:
    contact = df_input.iloc[st.session_state.current_idx]
    
    st.success(f"**👤 {contact['Contact_Name']}**\n\n📞 {contact['Phone_Number']}\n\n📌 {contact['Context_Notes']}")
    st.write("---")
    
    affluence = st.radio("💰 **Affluence Level**", ['High Ticket', 'Medium', 'Low', 'Not sure'])
    relationship = st.radio("🤝 **Relationship**", ['Very Close', 'Acquaintance', 'Strictly Professional', "Don't remember"])
    persona = st.radio("👗 **Client Persona**", ['Regular', 'Not a Regular', "Don't Know"])
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    # Go Back Logic
    with col1:
        if st.session_state.current_idx > 0:
            if st.button("⬅️ GO BACK & EDIT", use_container_width=True):
                # Delete the most recently added document from MongoDB
                last_contact = df_input.iloc[st.session_state.current_idx - 1]
                collection.delete_one({"Contact_ID": last_contact['Contact_ID']})
                
                st.session_state.current_idx -= 1
                st.rerun()

    # Save to Cloud Logic
    with col2:
        if st.button("💾 SAVE & NEXT", type="primary", use_container_width=True):
            # Create the data payload
            payload = contact.to_dict()
            payload['Affluence'] = affluence
            payload['Relationship'] = relationship
            payload['Persona'] = persona
            
            # Insert directly into MongoDB Atlas
            collection.insert_one(payload)
            
            st.session_state.current_idx += 1
            st.rerun()
else:
    st.balloons()
    st.success("🎉 All done! You can close this window. Thank you!")

# --- 5. Admin Panel (For You to Download the DB) ---
st.sidebar.title("🛠️ Admin Panel")
current_db_count = collection.count_documents({})
st.sidebar.success(f"✅ {current_db_count} contacts safely secured in Cloud Database.")

if current_db_count > 0:
    # Fetch all data from MongoDB and convert back to a Pandas DataFrame
    cursor = collection.find({}, {'_id': False}) # Exclude MongoDB's internal ID
    cloud_df = pd.DataFrame(list(cursor))
    
    st.sidebar.download_button(
        label="📥 Download Cloud Data (CSV)",
        data=cloud_df.to_csv(index=False).encode('utf-8'),
        file_name="mongodb_labeled_contacts.csv",
        mime="text/csv"
    )
    if st.sidebar.checkbox("👀 Preview Cloud Data"):
        st.sidebar.dataframe(cloud_df.tail())