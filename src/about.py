def run():
    import streamlit as st

    st.title('About this project')
    st.markdown('This project was specified by Institutional Research within Avans University of Applied Sciences to students of the Artificial Intelligence minor. For this project, different analysis and processing methods for the open answers of the NSE are being investigated in order to gain more insight into these answers.')
    st.markdown('This application will serve as a proof of concept to demonstrate that processing open-ended survey responses is possible and can be performed reliably using AI, with an emphasis on text mining.')
    st.subheader('Text Mining')
    st.markdown('Text mining is a part of data mining that searches for patterns within large amounts of data. Working with text documents requires first "cleaning" the texts before working with Natural Language Processing (NLP). Cleaning involves removing stop words, articles and misspelled words, among others, then NLP enables a computer to "read" and process different types of text documents like the human brain can. After cleaning texts and applying NLP, several methods are available to extract information from a text (document).')

    st.subheader('Proof of concept')
    st.markdown('In this proof of concept, several methods have been developed to demonstrate that, with the help of text mining, the processing of open answers can be made easier. This proof of concept also shows that the results of these methods are reliable and can possibly be used for scoring academies in the future.')

    if st.button(''):
        st.balloons()


if __name__ == "__main__":
    run()
