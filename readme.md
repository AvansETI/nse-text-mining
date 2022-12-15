# 1. Text mining project for Avans hogeschool NSE
This projects goal is to provide an application, allowing for easy analysis of the NSE open question results.

## 1.1. Content
- [1. Text mining project for Avans hogeschool NSE](#1-text-mining-project-for-avans-hogeschool-nse)
  - [1.1. Content](#11-content)
  - [1.2. Setting up the environment](#12-setting-up-the-environment)
    - [1.2.1. Linux (\& WSL)](#121-linux--wsl)
    - [1.2.2. Windows](#122-windows)
  - [1.3. Starting the application](#13-starting-the-application)
  - [1.4. Creating a new page](#14-creating-a-new-page)
    - [1.4.1. The page file](#141-the-page-file)
    - [1.4.2. Accessing the uploaded data](#142-accessing-the-uploaded-data)


## 1.2. Setting up the environment
There are several ways of setting up the invironment depending on the OS you use.

### 1.2.1. Linux (& WSL)
Clone this repo and open the directory. Then execute the folowing command: `pipenv shell` & `pipenv install`

### 1.2.2. Windows
Clone this repo and open the directory. TODO: add more

## 1.3. Starting the application
To run the app simply execute `streamlit run ./src/main.py`

## 1.4. Creating a new page

### 1.4.1. The page file
To create a new page you need to add a new file to the `src/pages` folder. An example of what it would look like:

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
    
    # example_page.py

### 1.4.2. Accessing the uploaded data
To acces the data that the user uploaded you have to use the following code:

    # this is needed to get the data_file from the session storage.
    # The StringIO converts the stored string to a file pandas can use.
    if 'data_file' in st.session_state:
        file = StringIO(st.session_state['data_file'])

        df = pd.read_csv(file)
        st.write(df)
the StringIO makes a file from a string so that you can use it pandas.
