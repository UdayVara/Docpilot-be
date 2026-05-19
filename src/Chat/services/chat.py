from langchain_huggingface import HuggingFaceEndpointEmbeddings, ChatHuggingFace
from langchain_core.output_parsers import StrOutputParser
from pinecone import Pinecone
import traceback

from langchain_core.prompts import ChatPromptTemplate

from langchain_huggingface import (
    HuggingFaceEndpoint,
)

from langchain_pinecone import PineconeVectorStore

from src.models.messages import Message
from src.utils.db.session import SessionLocal
from src.utils.settings import Settings


# -----------------------------------
# Embeddings
# -----------------------------------
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=Settings.HUGGINGFACEHUB_API_TOKEN,
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
    huggingfacehub_api_token=Settings.HUGGINGFACEHUB_API_TOKEN
)

model = ChatHuggingFace(llm=llm)



# -----------------------------------
# Ask AI
# -----------------------------------
async def ask_ai(
        chat_id: str,
        question: str,
):

    db = SessionLocal()

    try:

        # -----------------------------------
        # Save User Message
        # -----------------------------------
        user_message = Message(
            role="user",
            message=question,
            chat_id=chat_id
        )

        db.add(user_message)
        db.commit()

        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.6,
                "namespace": chat_id
            }
        )

        docs = retriever.invoke(question)
        strParser = StrOutputParser()
        # -----------------------------------
        # No PDF Context
        # -----------------------------------
        if not docs:

            simpleChain = model | strParser
            response = simpleChain.invoke(question)

            # Save Assistant Message
            assistant_message = Message(
                role="assistant",
                message=str(response),
                chat_id=chat_id
            )

            db.add(assistant_message)
            db.commit()

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

        chain = prompt | model | strParser

        response = chain.invoke({
            "context": context,
            "question": question
        })

        # Save Assistant Message
        assistant_message = Message(
            role="assistant",
            message=str(response),
            chat_id=chat_id
        )

        db.add(assistant_message)
        db.commit()

        return {
            "source": "pdf",
            "answer": response
        }
    except Exception as e:
        traceback.print_exc()

        raise Exception(str(e))
    finally:
        db.close()