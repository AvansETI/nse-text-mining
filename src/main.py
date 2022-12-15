from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# page title and text
st.title('Avans NSE Analysis')
st.caption(
    """This tool provides analytics for open answers in the national student survey (NSE).
     It has several **pages**, each telling a **story** and showing different aspects of the data.""")

st.header('Let\'s start with the data.')
file = st.file_uploader('Upload a csv file with the NSE results.',
                        type=['csv'], accept_multiple_files=False, help="Upload a file with the results of the NSE. The file has to be a csv file.")

# set file in session
if file is not None:
    # convert the file to a string
    stringio = StringIO(file.getvalue().decode("utf-8"))
    st.session_state['data_file'] = stringio.read()
elif 'data_file' in st.session_state:
    # convert the stored file string to an file pandas can use
    file = StringIO(st.session_state['data_file'])

# if the file is not none display the preview
if file is not None:
    df = pd.read_csv(file)
    st.caption('Data preview: ')
    st.write(df.head())
