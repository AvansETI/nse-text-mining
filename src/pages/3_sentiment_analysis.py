import streamlit as st
from draw_stack import Page, PageDrawStack
from tools.data.sentiment import get_sentiment_of_dataset
from pyecharts import options as opts
from streamlit_echarts import st_echarts

from tools.ui.charts import get_pie_chart_options

# define drawing queue
stack = PageDrawStack()

st.set_page_config(layout="wide")

# page title and text
st.title('Sentiment analysis')
st.caption(
    """In this page the answers are analysed for sentiment""")


def draw_pick_analysis_method():
    option = st.selectbox('What method should be used for the sentiment analysis? (default: Textblob)',
                          ('Textblob', 'Vader', 'Transformer'))
    st.info('The method may impact findings. For example: vader uses a translate API, which may impact the score.', icon='ℹ️')
    if st.button('Execute'):
        st.session_state['sentiment_method'] = option

        stack.set_stage_should_draw_state('total_analysis', True)
        stack.set_stage_should_draw_state('per_question_analysis', True)


def draw_analysis_total():
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

            st.markdown(f"""
            Of the respondends {(positive / (positive + negative)) * 100}% of their answers where positive, compared to {(negative / (positive + negative)) * 100}%
            negative. {conclusion}. The following questions seemed to lead to the most negative responses {'{placeholder}'}. The questions {'{placeholder}'} seemed to have mostly positive responses.
            """)

            st.markdown(f"""
            The following themes seem to cause the negative responses and could be improved upon: {'{placeholder}'}. The following themes are seen as positive {'placeholder'}.
            """)

            col1, col2 = st.columns(2)
            col1.metric("positive", positive, positive - negative)
            col2.metric("negative", negative, negative - positive)

            options = get_pie_chart_options(['positive', 'negative'], {'positive': positive, 'negative': negative})
            st_echarts(options=options, height='250px')


def draw_analysis_per_question():
    sentiment_analysis = st.session_state['sentiment_analysis']

    with st.expander('Per question'):
        for label in sentiment_analysis.keys():
            positive = sentiment_analysis[label]['positive']
            negative = sentiment_analysis[label]['negative']

            st.subheader(label)

            col1, col2 = st.columns(2)
            col1.metric("positive", positive, positive - negative)
            col2.metric("negative", negative, negative - positive)


# create a follower for the queue
page = Page('Sentiment page')
# create a handler for the stage_should_draw_changed event,
# call draw function if should draw = true
page.add_handler('stage_should_draw_changed',
                 lambda event_value: stack.get_draw_stage(event_value['stage_name']).draw_func() if event_value['state'] else None)

stack.listen(page)

stack.add_draw_stage('pick_analysis', draw_pick_analysis_method, True)
stack.add_draw_stage('total_analysis', draw_analysis_total)
stack.add_draw_stage('per_question_analysis', draw_analysis_per_question)

stack.start()
