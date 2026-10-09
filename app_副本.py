"""Interactive demo using bundled synthetic fixtures only."""
import pandas as pd
import streamlit as st
from src.pipeline import ROOT, read_table, validate

st.set_page_config(page_title='EHR Migration Quality Demo', layout='wide')
st.title('EHR Migration & Data Quality')
st.caption('Min Gao · Synthetic portfolio demonstration · Import preparation')
st.info('Fictional data and generic target schema. No connection to Avatar or Credible.')
c = read_table(ROOT/'data/raw/clients.csv', 'clients')
a = read_table(ROOT/'data/raw/admissions.csv', 'admissions')
m = read_table(ROOT/'data/reference/program_mapping.csv', 'mapping')
with st.expander('Inspect the source data and mapping'):
    st.dataframe(c, hide_index=True)
    st.dataframe(a, hide_index=True)
    st.dataframe(m, hide_index=True)
st.write('Validate IDs, required fields, dates, program mappings, and client dependencies.')
if st.button('Run validation', type='primary'):
    st.session_state['validation'] = validate(c, a, m)
if 'validation' in st.session_state:
    result = st.session_state['validation']
    rec = result['reconciliation']
    left, middle, right = st.columns(3)
    left.metric('Source rows', int(rec['input_rows'].sum()))
    middle.metric('Ready rows', int(rec['ready_rows'].sum()))
    right.metric('Rows requiring review', int(rec['review_rows'].sum()))
    st.subheader('Reconciliation')
    st.dataframe(rec, hide_index=True)
    st.caption('Source rows = ready rows + review rows. Rule violations can exceed review rows.')
    errors = result['exceptions']
    st.subheader('Rule violations')
    if not errors.empty:
        st.bar_chart(errors['rule'].value_counts())
        options = ['All'] + sorted(errors['rule'].unique().tolist())
        selected = st.selectbox('Filter by rule', options)
        st.dataframe(errors if selected == 'All' else errors[errors['rule'] == selected], hide_index=True)
    for name in ['clients_ready', 'admissions_ready', 'clients_review', 'admissions_review', 'exceptions', 'reconciliation']:
        st.download_button(f'Download {name}', result[name].to_csv(index=False).encode('utf-8'),
                           file_name=f'{name}.csv', mime='text/csv')
