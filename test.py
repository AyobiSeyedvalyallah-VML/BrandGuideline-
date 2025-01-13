from io import StringIO
import pandas as pd
import streamlit as st
import openai
from helpers import prompt_transformer
uploaded_files = st.file_uploader(
    "Please upload the Brand Guideline file",
    accept_multiple_files=True,
    type=['html']
)
st.session_state.setdefault("extract", True)
st.session_state.setdefault("df", '')

for uploaded_file in uploaded_files:

    bytes_data = uploaded_file.read()
    
    html_content = bytes_data.decode('utf-8')
    if st.session_state['extract']:
        with st.spinner("Extracting data..."):
            try:
                df = prompt_transformer(html_content)
            except:
                df = prompt_transformer(html_content)
            st.session_state['df'] = df
            st.session_state['extract']=False
        st.snow()
    
    df = pd.read_csv(StringIO(st.session_state['df']))

    choice = st.selectbox(
        "Select the Type",
        [i for i in df['category'].unique()],
        index=None,
        placeholder="Please select the category..."
    )
    temp = df[df['category']==choice]
    cols = st.columns(3)
    for index,row in temp.iterrows():
        with cols[index % 3]:
            st.image(row['image_link'],use_container_width =False)
