import streamlit as st
import yaml

with open('config.yaml') as file:
        config = yaml.safe_load(file)

st.title(config['title'])