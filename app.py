import streamlit as st
import yaml
import gspread
from gspread_dataframe import get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Application Setup

with open('config.yaml') as file:
        config = yaml.safe_load(file)

GOOGLE_SERVICE_ACCOUNT_FILE = st.secrets['GOOGLE_SERVICE_ACCOUNT_FILE']
GOOGLE_SHEET_URL = config['google_sheet_url']
GOOGLE_SHEET_NAME = config['google_sheet_name']

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

st.title(config['title'])

# Group FAQs by topic
faq_df = read_faq_sheet(GOOGLE_SHEET_URL, GOOGLE_SHEET_NAME)
grouped_faqs = faq_df.groupby('Topic')

for topic, group in grouped_faqs:
    st.subheader(f"{topic}")

    for _, row in group.iterrows():
        st.markdown(f"**{row['Question']}**  \n{row['Answer']}  \n")