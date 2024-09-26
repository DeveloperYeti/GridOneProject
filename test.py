
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)

with open('Example.txt', 'r', encoding='utf-8') as file:
    text = file.read()

text_splitter = RecursiveCharacterTextSplitter(  
    separators = ["\n","\n\n"],    
    chunk_size = 100,
    chunk_overlap  = 50,
    length_function = len,
    is_separator_regex = False,
)
texts = text_splitter.create_documents([text])
texts

from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
embedding_function = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")

from langchain.vectorstores import FAISS
db = FAISS.from_documents(texts, embedding_function )

retriever = db.as_retriever(search_type="similarity", search_kwargs={'k':5, 'fetch_k': 50})
retriever.get_relevant_documents("상속이 뭐야.")

query = "상속이 뭐야."
docs = db.similarity_search(query)
print(docs[0].page_content)

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap

template = """
Answer the question as based only on the following context:
{context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

from langchain_community.chat_models import ChatOllama
llm = ChatOllama(model="gemma2:9b", temperature=0, base_url="http://127.0.0.1:11434/") #http://127.0.0.1:11434

from langchain.schema.runnable import RunnableMap
chain = RunnableMap({
    "context": lambda x: retriever.get_relevant_documents(x['question']),
    "question": lambda x: x['question']
}) | prompt | llm

from IPython.display import Markdown
Markdown(chain.invoke({'question': "상속이 뭐야"}).content)