import streamlit as st
import pandas as pd
import os

# --- 1. App Configuration ---
# Setting the layout to be clean and mobile-friendly
st.set_page_config(page_title="Client Segmentation", page_icon="💎", layout="centered")

# Custom CSS to make radio buttons look a bit bigger and cleaner on mobile
st.markdown("""
    <style>
    div.row-widget.stRadio > div { flex-direction:row; flex-wrap: wrap; gap: 10px; }
    </style>
""", unsafe_allow_html=True)

INPUT_FILE = "unsegmented_contacts.csv"
OUTPUT_FILE = "labeled_contacts.csv"

# --- 2. Data Loading & State Management ---
@st.cache_data
def load_data():
    return pd.read_csv(INPUT_FILE)

df_input = load_data()
total_contacts = len(df_input)

# Smart Resume: Check how many are already done
if not os.path.exists(OUTPUT_FILE):
    new_cols = list(df_input.columns) + ['Affluence', 'Relationship', 'Persona']
    pd.DataFrame(columns=new_cols).to_csv(OUTPUT_FILE, index=False)
    labeled_count = 0
else:
    df_output = pd.read_csv(OUTPUT_FILE)
    labeled_count = len(df_output)

# Set the bookmark
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = labeled_count

# --- 3. The User Interface (Frontend) ---
st.title("Client Segmentation Portal 💎")
st.progress(st.session_state.current_idx / total_contacts)
st.caption(f"Progress: {st.session_state.current_idx} out of {total_contacts} done")

if st.session_state.current_idx < total_contacts:
    contact = df_input.iloc[st.session_state.current_idx]
    
    # Client Info Box
    st.success(f"**👤 {contact['Contact_Name']}**\n\n📞 {contact['Phone_Number']}\n\n📌 {contact['Context_Notes']}")
    
    st.write("---")
    
    # The 3 Questions
    affluence = st.radio("💰 **Affluence Level**", 
                         ['High Ticket', 'Medium', 'Low', 'Not sure'])
    
    relationship = st.radio("🤝 **Relationship**", 
                            ['Very Close', 'Acquaintance', 'Strictly Professional', "Don't Remember"])
    
    persona = st.radio("👗 **Client Persona**", 
                       ['Regular', 'Not a Regular', "Don't Know"])
    
    st.write("---")
    
    # --- 4. The Save Action ---
    if st.button("💾 SAVE & NEXT", type="primary", use_container_width=True):
        # Package the data
        new_row = contact.to_dict()
        new_row['Affluence'] = affluence
        new_row['Relationship'] = relationship
        new_row['Persona'] = persona
        
        # Save to CSV instantly
        pd.DataFrame([new_row]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        
        # Move forward
        st.session_state.current_idx += 1
        st.rerun()
else:
    st.balloons()
    st.success("🎉 All done! You can close this window. Thank you!")