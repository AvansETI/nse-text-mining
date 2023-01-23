from collections import OrderedDict
import math
import streamlit as st
from draw_stack import Page, PageDrawStack
from tools.data.collocation import get_bigram_grid, negativity_rating, plot_creater, positivity_rating
from tools.data.sentiment import get_sentiment_of_dataset
from pyecharts import options as opts
from streamlit_echarts import st_echarts
import pandas as pd
from tools.ui.charts import get_pie_chart_options

# define drawing queue
stack = PageDrawStack()

st.set_page_config(layout="wide")

# page title and text
st.title('Sentiment analysis')
st.caption(
    """In this page the answers are analysed for sentiment""")


def draw_warning_message():
    st.warning("You need to preprocess the data first")


def draw_pick_analysis_method():
    option = st.selectbox('What method should be used for the sentiment analysis? (default: Textblob)',
                          ('Textblob', 'Vader', 'Transformer'))

    st.info("""The method may impact findings. For example: vader uses a translate API,
    which may impact the score. It is recommended to use the default.""", icon='ℹ️')

    if st.button('Execute'):
        st.session_state['sentiment_method'] = option

        stack.set_stage_should_draw_state('total_analysis', True)
        stack.set_stage_should_draw_state('per_question_analysis', True)


def draw_analysis_total():
    def safe_division(a, b):
        return b and round(a / b, 2) or 0

    method = st.session_state['sentiment_method']
    data = st.session_state['cleaned_data']

    with st.expander('Total sentiment of answers', expanded=True):
        with st.spinner('Calculating sentiment...'):
            result = get_sentiment_of_dataset(dataset=data, columns=['Jaar', 'Actuele BRIN-code volgens CROHO',
                                                                     'Actuele naam instelling volgens CROHO', 'Actuele CROHO-code volgens CROHO',
                                                                     'Actuele Opleidingsnaam volgens CROHO', 'Actuele BRIN-volgnummer volgens CROHO', 'Type Student',
                                                                     'Opleidingsvorm (vt dt du)', 'Academie', 'Studiejaar volgens instelling',
                                                                     'Kunstopleiding', 'Afstandsonderwijs',
                                                                     ], analysis_type=method)
            st.session_state['sentiment_analysis'] = result

            positive, negative = 0, 0
            for key in result.keys():
                question = result[key]

                positive = positive + question['positive']
                negative = negative + question['negative']

            reponses = [
                'Good job, that\'s more positive than negative responses',
                'There is some room for improvement, there are more negative than positive responses'
                ]
            conclusion = reponses[0] if positive > negative else reponses[1]

            negative_questions = {}
            for question in result.keys():
                negative_questions[question] = result[question]['negative']
            negative_questions = dict(sorted(negative_questions.items(), key=lambda x: x[1]))

            positive_questions = {}
            for question in result.keys():
                positive_questions[question] = result[question]['positive']
            positive_questions = dict(sorted(positive_questions.items(), key=lambda x: x[1]))

            st.markdown(f"""
            Of the respondends {safe_division(positive, (positive + negative)) * 100}% of their answers where positive,
            compared to {safe_division(negative, (positive + negative)) * 100}%
            negative. {conclusion}. The following questions have the most negative responses `{list(negative_questions)[-3:]}`.
            The questions `{list(positive_questions)[-3:]}` had the most positive responses.
            """)

            col1, col2 = st.columns(2)
            col1.metric("positive", positive, positive - negative)
            col2.metric("negative", negative, negative - positive)

            options = get_pie_chart_options(['positive', 'negative'], {'positive': positive, 'negative': negative})
            st_echarts(options=options, height='250px')


def draw_analysis_per_question():
    sentiment_analysis = st.session_state['sentiment_analysis']
    data = st.session_state['cleaned_data']

    with st.expander('Per question'):
        for label in sentiment_analysis.keys():
            positive = sentiment_analysis[label]['positive']
            negative = sentiment_analysis[label]['negative']

            st.subheader(label)

            st.caption('Sentiment')

            col1, col2 = st.columns(2)
            col1.metric("positive", positive, positive - negative)
            col2.metric("negative", negative, negative - positive)

            st.caption('Collocation')
            st.info('Collocation uses predefined word scores to score a text. This is not the same score as the sentiment analysis method chosen above.')

            question = pd.DataFrame(data[label])
            # question.set_index('number', inplace=True)

            bigram = get_bigram_grid(question)
            fig = plot_creater(bigram, label)

            st.pyplot(fig)
            # st.write(data[label].head())


# create a follower for the queue
page = Page('Sentiment page')
# create a handler for the stage_should_draw_changed event,
# call draw function if should draw = true
page.add_handler('stage_should_draw_changed',
                 lambda event_value: stack.get_draw_stage(event_value['stage_name']).draw_func() if event_value['state'] else None)

stack.listen(page)

if 'cleaned_data' in st.session_state:
    stack.add_draw_stage('pick_analysis', draw_pick_analysis_method, True)
    stack.add_draw_stage('total_analysis', draw_analysis_total)
    stack.add_draw_stage('per_question_analysis', draw_analysis_per_question)
else:
    stack.add_draw_stage('message', draw_warning_message, True)

stack.start()
