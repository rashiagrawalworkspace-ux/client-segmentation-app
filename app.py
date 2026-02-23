import streamlit as st
import pandas as pd
import os

# --- 1. App Configuration ---
st.set_page_config(page_title="Client Segmentation", page_icon="💎", layout="centered")

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

if not os.path.exists(OUTPUT_FILE):
    new_cols = list(df_input.columns) + ['Affluence', 'Relationship', 'Persona']
    pd.DataFrame(columns=new_cols).to_csv(OUTPUT_FILE, index=False)
    labeled_count = 0
else:
    df_output = pd.read_csv(OUTPUT_FILE)
    labeled_count = len(df_output)

if 'current_idx' not in st.session_state:
    st.session_state.current_idx = labeled_count

# --- 3. The User Interface (Frontend) ---
st.title("Client Segmentation Portal 💎")
st.progress(st.session_state.current_idx / total_contacts if total_contacts > 0 else 0)
st.caption(f"Progress: {st.session_state.current_idx} out of {total_contacts} done")

if st.session_state.current_idx < total_contacts:
    contact = df_input.iloc[st.session_state.current_idx]
    
    st.success(f"**👤 {contact['Contact_Name']}**\n\n📞 {contact['Phone_Number']}\n\n📌 {contact['Context_Notes']}")
    st.write("---")
    
    affluence = st.radio("💰 **Affluence Level**", 
                         ['High Ticket', 'Medium', 'Low', 'Not sure'])
    
    relationship = st.radio("🤝 **Relationship**", 
                            ['Very Close', 'Acquaintance', 'Strictly Professional', "Don't remember"])
    
    persona = st.radio("👗 **Client Persona**", 
                       ['Regular', 'Not a Regular', "Don't Know"])
    
    st.write("---")
    
    # --- 4. Navigation & Save Action ---
    col1, col2 = st.columns(2)
    
    with col1:
        # Only show 'Go Back' if she has actually completed at least one entry
        if st.session_state.current_idx > 0:
            if st.button("⬅️ GO BACK & EDIT", use_container_width=True):
                # 1. Read the current output file
                out_df = pd.read_csv(OUTPUT_FILE)
                # 2. Drop the very last row (the one she just did)
                out_df = out_df.iloc[:-1]
                # 3. Overwrite the CSV with the cleaned dataframe
                out_df.to_csv(OUTPUT_FILE, index=False)
                # 4. Move index back by 1 and refresh
                st.session_state.current_idx -= 1
                st.rerun()

    with col2:
        if st.button("💾 SAVE & NEXT", type="primary", use_container_width=True):
            new_row = contact.to_dict()
            new_row['Affluence'] = affluence
            new_row['Relationship'] = relationship
            new_row['Persona'] = persona
            
            pd.DataFrame([new_row]).to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            
            st.session_state.current_idx += 1
            st.rerun()
else:
    st.balloons()
    st.success("🎉 All done! You can close this window. Thank you!")

# --- 5. Admin Panel ---
st.sidebar.title("🛠️ Admin Panel")
if os.path.exists(OUTPUT_FILE):
    output_df = pd.read_csv(OUTPUT_FILE)
    st.sidebar.success(f"✅ {len(output_df)} contacts safely labeled.")
    
    with open(OUTPUT_FILE, "rb") as file:
        st.sidebar.download_button(
            label="📥 Download Labeled CSV", data=file, file_name="final_labeled_contacts.csv", mime="text/csv"
        )
    if st.sidebar.checkbox("👀 Preview Live Data"):
        st.sidebar.dataframe(output_df.tail())
else:
    st.sidebar.warning("No data labeled yet.")