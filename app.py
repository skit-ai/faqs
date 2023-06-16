import streamlit as st
import gspread
from algoliasearch.search_client import SearchClient
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from st_keyup import st_keyup

# Application Setup

GOOGLE_SERVICE_ACCOUNT_FILE = st.secrets['GOOGLE_SERVICE_ACCOUNT_FILE']
GOOGLE_SHEET_URL = st.secrets['config']['google_sheet_url']
GOOGLE_SHEET_NAME = st.secrets['config']['google_sheet_name']

ALGOLIA_APP_ID = st.secrets['algolia']['ALGOLIA_APP_ID']
ALGOLIA_API_KEY = st.secrets['algolia']['ALGOLIA_API_KEY']
ALGOLIA_INDEX_NAME = st.secrets['config']['algolia_index_name']

# Read FAQs from Google Sheet
@st.cache_resource(ttl=14400)  # Cache for 4 hours
def read_faq_sheet(sheet_url, sheet_name):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_SERVICE_ACCOUNT_FILE, ['https://spreadsheets.google.com/feeds']
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    faq_df = get_as_dataframe(sheet)
    faq_df = faq_df.dropna(how='all')
    return faq_df

# Search FAQs using Algolia
def search_faqs(query):
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    index = client.init_index(ALGOLIA_INDEX_NAME)
    search_results = index.search(query)
    hits = pd.DataFrame(search_results['hits'])
    return hits.loc[:, ['Topic', 'Question', 'Answer']]

def display_df(value, df):

    if not value:
         df = read_faq_sheet(GOOGLE_SHEET_URL, GOOGLE_SHEET_NAME)
    elif len(value)<3:
         st.write("Please enter at least 3 characters to search")
    else:
         df = search_faqs(value)

    grouped_faqs = df.groupby('Topic')
    
    for topic, group in grouped_faqs:
        st.subheader(f"{topic}")

        for _, row in group.iterrows():
            st.markdown(f"**{row['Question']}**  \n{row['Answer']}  \n")

def main():
    st.title(st.secrets['config']['title'])

    # Search bar
    value = st_keyup("Search Here", debounce=500)

    # Group FAQs by topic
    display_df(value, None)

if __name__ == "__main__":
    main()