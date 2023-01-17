def run():
    import streamlit as st

    st.header('An example text for analysis one page')

    if 'cleaned_data' in st.session_state:
        df = st.session_state['cleaned_data']

        st.write(df)


if __name__ == "__main__":
    run()
