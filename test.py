from io import StringIO
import pandas as pd
import streamlit as st
import os
from helpers import prompt_transformer, image_font_generation, fix_csv, capitalize_if_needed
import time
from pathlib import Path

project_dir = Path(__file__).parent.parent
# st.write(os.listdir(project_dir))
# st.write(os.listdir(os.path.join(project_dir,'brandguideline-')))
project_path = os.path.join(project_dir,'brandguideline-')
fonts_folder = os.path.join(project_path,'fonts')
# st.write(os.listdir(os.path.join(project_path,'fonts')))
uploaded_files = st.file_uploader(
    "Please upload the Brand Guideline file",
    accept_multiple_files=True,
    type=['html']
)

st.session_state.setdefault("extract", True)
st.session_state.setdefault("df", '')
st.session_state.setdefault("retry",True)
st.session_state.setdefault('filename','')
file_name = ''
for uploaded_file in uploaded_files:

    bytes_data = uploaded_file.read()
    
    html_content = bytes_data.decode('utf-8')
    if uploaded_file.name is not None:
        st.session_state['filename'] = uploaded_file.name
    # st.write(uploaded_file.name)
    if st.session_state['extract']:
        file_name = uploaded_file.name
        with st.spinner("Extracting data..."):
            try:
                df = prompt_transformer(html_content)
            except:
                df = prompt_transformer(html_content)
            st.session_state['df'] = df
            st.session_state['extract']=False
            # st.snow()
        
    count = 0
    try:
        df = pd.read_csv(StringIO(st.session_state['df']),sep='\t',header=1)
    except:
       if st.session_state['retry']:
            with st.spinner("Retry: Extracting data..."):
                try:
                    time.sleep(5)
                    df = fix_csv(st.session_state['df'])
                    df = pd.read_csv(StringIO(df),sep='\t',header=1)
                    st.session_state['retry'] = False
                    # st.session_state['df'] = df
                except Exception as e:
                    # df = prompt_transformer(html_content)
                    # df = pd.read_csv(StringIO(st.session_state['df']),sep='\t',header=1)
                    # st.session_state['df'] = df
                    st.write('Error: ',"can't parse the file")
    st.write(df)
    choice = st.selectbox(
        "Select the Type",
        [i for i in df['category'].unique()],
        index=None,
        placeholder="Please select the category..."
    )
    df.to_csv('output.csv')
    temp = df[df['category']==choice]
    cols = st.columns(3)
    # st.write(file_name)
    for index,row in temp.iterrows():
        with cols[index % 3]:
            if 'https' not in row['image_link']:
                st.image(f"https://spectrum.adobe.com{row['image_link']}", caption=row['description'],use_container_width =False)
            else:
                st.image(row['image_link'], caption=row['description'],use_container_width =False)
    file_name = capitalize_if_needed(st.session_state['filename'].replace(".html",""))
    # fonts_folder = os.path.join(project_path,'fonts')
    fonts_path = os.path.join(fonts_folder,file_name)
    fonts = os.listdir(fonts_path)
    #fonts = os.listdir(f'./fonts/{file_name}')
    
  
    if choice is not None and 'font' in choice.lower():
        # st.write(file_name)
        c = st.selectbox(
        "Select the font",
        [i for i in fonts],
        index=None,
        placeholder="Please select the font..."
        
       
    )
        if c is not None:
            img = image_font_generation(c,file_name)
            st.image(img)
