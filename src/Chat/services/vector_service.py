from tempfile import NamedTemporaryFile


from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone, ServerlessSpec

from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils.settings import Settings


# -----------------------------
# Embedding Model
# -----------------------------
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=Settings.HUGGINGFACEHUB_API_TOKEN,
)


# -----------------------------
# Pinecone Client
# -----------------------------
pc = Pinecone(
    api_key=Settings.PINECONE_API_KEY
)

INDEX_NAME = Settings.INDEX_NAME


# -----------------------------
# Create Index
# -----------------------------
def create_index_if_not_exists():

    existing_indexes = [
        index["name"]
        for index in pc.list_indexes()
    ]

    if INDEX_NAME not in existing_indexes:

        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )


# -----------------------------
# Process PDF + Store Vectors
# -----------------------------
async def process_pdf_and_store_vectors(
        file,
        chat_id: str,
        user_id: str,
):

    create_index_if_not_exists()

    # reset pointer
    file.file.seek(0)

    # save temp pdf
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:

        temp_file.write(await file.read())

        temp_path = temp_file.name

    # load pdf
    loader = PyPDFLoader(temp_path)

    documents = loader.load()
    print("documents:", len(documents))
    print("path",temp_path)
    # split chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)
    print("chunks:", len(chunks))
    # add metadata
    for chunk in chunks:

        chunk.metadata["chat_id"] = chat_id
        chunk.metadata["user_id"] = user_id

    # connect existing pinecone index
    index = pc.Index(INDEX_NAME)

    # vector store
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=chat_id
    )

    # store vectors
    ids = vector_store.add_documents(chunks)

    print("INSERTED IDS:", ids)
    print("TOTAL CHUNKS:", len(chunks))

    return True