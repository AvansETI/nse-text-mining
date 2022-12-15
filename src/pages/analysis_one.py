from io import StringIO


def run():
    import streamlit as st
    import pandas as pd

    st.header('An example text for analysis one page')

    # this is needed to get the data_file from the session storage.
    # The StringIO converts the stored string to a file pandas can use.
    if 'data_file' in st.session_state:
        file = StringIO(st.session_state['data_file'])

        df = pd.read_csv(file)
        st.write(df)


if __name__ == "__main__":
    run()
