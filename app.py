import streamlit as st
import gspread
from algoliasearch.search_client import SearchClient
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from st_keyup import st_keyup

# Application Setup

GOOGLE_SHEET_URL = st.secrets['config']['google_sheet_url']
GOOGLE_SHEET_NAME = st.secrets['config']['google_sheet_name']

ALGOLIA_APP_ID = st.secrets['algolia']['ALGOLIA_APP_ID']
ALGOLIA_API_KEY = st.secrets['algolia']['ALGOLIA_API_KEY']
ALGOLIA_INDEX_NAME = st.secrets['config']['algolia_index_name']

@st.cache_resource()
def get_sheet(sheet_url, sheet_name):
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets['google'], ['https://spreadsheets.google.com/feeds']
    )
    client = gspread.authorize(credentials)
    return client.open_by_url(sheet_url).worksheet(sheet_name)

# Read FAQs from Google Sheet
def read_faq_sheet(sheet):
    faq_df = get_as_dataframe(sheet)
    faq_df = faq_df.dropna(how='all')
    return faq_df

# Search FAQs using Algolia
def search_faqs(query):
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    index = client.init_index(ALGOLIA_INDEX_NAME)
    search_results = index.search(query)
    if not search_results['hits']:
        return pd.DataFrame()
    hits = pd.DataFrame(search_results['hits'])
    return hits.loc[:, ['Topic', 'Question', 'Answer']]

def display_df(value, df):

    if not value:
         pass
    elif len(value)<3:
         st.write("Please enter at least 3 characters to search")
    else:
         df = search_faqs(value)
    if df.empty:
        st.warning("No results found. Click on the button above to raise a request")
    else:
        grouped_faqs = df.groupby('Topic')     
        for topic, group in grouped_faqs:
            st.subheader(f"{topic}")

            for _, row in group.iterrows():
                st.markdown(f"**{row['Question']}**  \n{row['Answer']}  \n")

def create_faq_request():
    args=(st.session_state.new_faq, st.session_state.user_email)
    row_values = ['', args[0], '', args[1]]
    sheet = get_sheet(GOOGLE_SHEET_URL, GOOGLE_SHEET_NAME)
    sheet.append_row(row_values)
    st.success("Question Submitted Successfully")


def raise_faq_request(search_query):
    button = st.button("Raise an FAQ request")
    if button:
        with st.form("FAQ Request Form"):
            st.write("Raise an FAQ request")
            st.text_input("Enter your question", value=search_query, key='new_faq')
            st.text_input("Enter your email address", key='user_email')
            st.form_submit_button("Submit", on_click=create_faq_request)

def main():
    st.title(st.secrets['config']['title'])

    # Search bar
    value = st_keyup("Search Here")

    raise_faq_request(value)

    sheet = get_sheet(GOOGLE_SHEET_URL, GOOGLE_SHEET_NAME)

    display_df(value, read_faq_sheet(sheet))

if __name__ == "__main__":
    main()