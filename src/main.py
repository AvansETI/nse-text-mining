from io import StringIO
import streamlit as st
import pandas as pd
from draw_stack import Page, PageDrawStack
from tools.data.preprocessing import clean, spell_check_data
from annotated_text import annotated_text

st.set_page_config(layout="wide")

# define drawing queue
stack = PageDrawStack()

# page title and text
st.title('Avans NSE Analysis')
st.caption(
    """This tool provides analytics for open answers in the national student survey (NSE).
     It has several **pages**, each telling a **story** and showing different aspects of the data.""")


def draw_file_upload():
    st.header('Let\'s start with the data.')
    file = st.file_uploader('Upload a csv file with the NSE results.',
                            type=['csv'], accept_multiple_files=False,
                            help="Upload a file with the results of the NSE. The file has to be a csv file.")

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

        stack.set_stage_should_draw_state('clean_data', True)


def draw_cleaning_data():
    st.subheader('Preprocessing the data')

    if 'data_file' in st.session_state:
        data = pd.read_csv(StringIO(st.session_state['data_file']))
        cleaned_data = clean(data, ['Jaar', 'Actuele BRIN-code volgens CROHO',
                                    'Actuele naam instelling volgens CROHO', 'Actuele CROHO-code volgens CROHO',
                                    'Actuele Opleidingsnaam volgens CROHO', 'Actuele BRIN-volgnummer volgens CROHO', 'Type Student',
                                    'Opleidingsvorm (vt dt du)', 'Academie', 'Studiejaar volgens instelling',
                                    'Kunstopleiding', 'Afstandsonderwijs',
                                    ], exclude=True)
        st.session_state['cleaned_data'] = cleaned_data

        with st.expander('Cleaning the data'):
            st.caption("""In this step all empty values are set to \'empty_field\',
                punctuation is removed and the text is converted to lower case.""")

            st.dataframe(cleaned_data.head())

    # remove items that should always draw and are therefore already drawn
    stages = list(stack.get_stages())
    stages.remove('clean_data')
    stages.remove('file_upload')

    # load a multiselect with all options except the defaults
    options = st.multiselect('Select or remove preprocessing steps', options=stages,
                             default=stages)

    # tell queue that the selected items should be drawn
    if st.button('Execute steps'):
        for option in options:
            stack.set_stage_should_draw_state(option, True)


def draw_spelling_check():
    cleaned_data = st.session_state['cleaned_data']

    with st.expander('Spelling check'):
        st.caption('In this step the answers are checked for spelling mistakes.')

        if cleaned_data is not None:
            result = {}
            with st.spinner('Checking spelling...'):
                result = spell_check_data(cleaned_data, ['Jaar', 'Actuele BRIN-code volgens CROHO',
                                                         'Actuele naam instelling volgens CROHO', 'Actuele CROHO-code volgens CROHO',
                                                         'Actuele Opleidingsnaam volgens CROHO', 'Actuele BRIN-volgnummer volgens CROHO', 'Type Student',
                                                         'Opleidingsvorm (vt dt du)', 'Academie', 'Studiejaar volgens instelling',
                                                         'Kunstopleiding', 'Afstandsonderwijs',
                                                         ], exclude=True)

                st.json(result)


def draw_test():
    st.header('test!')


# create a follower for the queue
page = Page('main page')
# create a handler for the stage_should_draw_changed event,
# call draw function if should draw = true
page.add_handler('stage_should_draw_changed',
                 lambda event_value: stack.get_draw_stage(event_value['stage_name']).draw_func() if event_value['state'] else None)

# subscribe to stack
stack.listen(page)

# always draw file upload
stack.add_draw_stage('file_upload', draw_file_upload, should_draw=True)

# conditional draws
stack.add_draw_stage('clean_data', draw_cleaning_data)
stack.add_draw_stage('spelling_check', draw_spelling_check)
stack.add_draw_stage('test', draw_test)

stack.start()
