
from newspaper import Article
import xml.etree.ElementTree as ET
import requests
import pandas as pd
from transformers import pipeline
import streamlit as st

@st.cache(allow_output_mutation=True)
def get_article_data(url):
  try:
    article = Article(url)
    article.download()
    article.parse()
    # html = article.html
    text = article.text
    return text
  except Exception as e:
    return ('Error -' + str(e), "")

@st.cache(allow_output_mutation=True)
def get_headlines():
    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"

    resp = requests.get(url)
    tree = ET.fromstring(resp.content)

    news_data = []
    for ind, child in enumerate(tree.iter()):
        if child.tag == 'title':
            news_data.append((child.text, list(tree.iter())[ind+1].text))
    
    df = pd.DataFrame(news_data, columns=['Headline', 'URL'])
    return df

@st.cache(allow_output_mutation = True)
def get_news(df):
    hub_model_id = "model"
    summarizer = pipeline("summarization", model=hub_model_id)
    df['Summary'] = df['news'].apply(summarizer)
    df['Summary'] = df['Summary'].apply(lambda x: x[0]['summary_text'])
    return df
    

st.set_page_config(page_title="autoShorts", layout="wide")
st.title('AutoShorts - Summarized News')

with st.container():
    clicked = st.button('Summarize Today\'s News')

status_bar = st.progress(0)


if clicked:
    
    status_bar.progress(20)

    df = get_headlines()
    status_bar.progress(30)

    df['news'] = df['URL'].apply(get_article_data)
    status_bar.progress(40)

    df = df[df['news'].str.startswith('Error -')==False]
    df = df[df['news'].apply(len) > 100]
    status_bar.progress(50)
    
    df['news'] = df['news'].apply(lambda x: x.replace('\n', ''))
    status_bar.progress(60)

    df = get_news(df)
    status_bar.progress(100)

    for i in range(1, len(df)+1, 2):
        with st.container():
            st.markdown("""---""")
            col1, col2 = st.columns(2)
            try:
                with col1:
                    st.subheader(df['Headline'].iloc[i-1])
                    st.write(df['Summary'].iloc[i-1])
                    st.caption("Read full article: [here]({})".format(df['URL'].iloc[i-1]))
                    
            except:
                pass

            try:
                with col2:
                    st.subheader(df['Headline'].iloc[i])
                    st.write(df['Summary'].iloc[i])
                    st.caption("Read full article: [here]({})".format(df['URL'].iloc[i]))
            except:
                pass

            

