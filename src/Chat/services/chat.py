from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from pinecone import Pinecone

from langchain_core.prompts import ChatPromptTemplate

from langchain_huggingface import (
    HuggingFaceEndpoint,
)

from langchain_pinecone import PineconeVectorStore

from src.utils.settings import Settings


# -----------------------------------
# Embeddings
# -----------------------------------
embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=Settings.HUGGINGFACEHUB_API_TOKEN,
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------------
# Pinecone
# -----------------------------------
pc = Pinecone(
    api_key=Settings.PINECONE_API_KEY
)

index = pc.Index(Settings.INDEX_NAME)


# -----------------------------------
# Vector Store
# -----------------------------------
vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings
)


# -----------------------------------
# HuggingFace LLM
# -----------------------------------
llm = HuggingFaceEndpoint(
    repo_id="openai/gpt-oss-120b",
    task="text-generation",
    huggingfacehub_api_token=Settings.HUGGINGFACEHUB_API_TOKEN,
    max_new_tokens=512,
    temperature=0.3
)


# -----------------------------------
# Ask AI
# -----------------------------------
async def ask_ai(
        chat_id: str,
        question: str,
):

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 5,
            "score_threshold": 0.6,
            "namespace": chat_id
        }
    )

    docs = retriever.invoke(question)

    # -----------------------------------
    # No PDF Context
    # -----------------------------------
    if not docs:

        response = llm.invoke(question)

        return {
            "source": "llm",
            "answer": response
        }

    # -----------------------------------
    # PDF Context Found
    # -----------------------------------
    context = "\n\n".join([
        doc.page_content
        for doc in docs
    ])

    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful AI assistant.

Answer the user's question ONLY using the PDF context.

If answer is not available in the context,
say:
"I could not find this information in the uploaded PDF."

PDF Context:
{context}

Question:
{question}
"""
    )

    chain = prompt | llm

    response = chain.invoke({
        "context": context,
        "question": question
    })

    return {
        "source": "pdf",
        "answer": response
    }