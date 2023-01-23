from draw_stack import Page, PageDrawStack
import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# define drawing queue
stack = PageDrawStack()

st.set_page_config(layout="wide")

# page title and text
st.title('Data exploration')
st.caption(
    """This page allows you to get an idea of the data you are working with.""")


def draw_warning_message():
    st.warning("You need to preprocess the data first")


def draw_head():
    with st.expander("The dataset", expanded=True):
        data = st.session_state['cleaned_data']
        st.write(data)


def draw_wordcloud():
    with st.expander("Wordcloud for questions", expanded=True):
        data = st.session_state['cleaned_data']
        data = data.drop(['Jaar', 'Actuele BRIN-code volgens CROHO',
                          'Actuele naam instelling volgens CROHO', 'Actuele CROHO-code volgens CROHO',
                          'Actuele Opleidingsnaam volgens CROHO', 'Actuele BRIN-volgnummer volgens CROHO', 'Type Student',
                          'Opleidingsvorm (vt dt du)', 'Academie', 'Studiejaar volgens instelling',
                          'Kunstopleiding', 'Afstandsonderwijs',
                          ], axis=1)

        options = st.multiselect("Select questions to process", options=data.columns)
        for option in options:
            st.caption(option)

            wordcloud = WordCloud(background_color="black", max_words=5000, contour_width=0, height=100, scale=4, colormap='Reds_r')
            wordcloud.generate(','.join(list(data[option].values)))

            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            ax.set_frame_on(False)
            st.pyplot(fig)


# create a follower for the queue
page = Page('Data exploration')
# create a handler for the stage_should_draw_changed event,
# call draw function if should draw = true
page.add_handler('stage_should_draw_changed',
                 lambda event_value: stack.get_draw_stage(event_value['stage_name']).draw_func() if event_value['state'] else None)

stack.listen(page)

# stack.add_draw_stage('pick_analysis', draw_question_picker_for_wordcloud, True)
if 'cleaned_data' in st.session_state:
    stack.add_draw_stage('head', draw_head, True)
    stack.add_draw_stage('word_cloud', draw_wordcloud, True)
else:
    stack.add_draw_stage('message', draw_warning_message, True)

stack.start()
