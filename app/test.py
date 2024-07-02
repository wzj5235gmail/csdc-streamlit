from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
import dotenv

dotenv.load_dotenv()

vectors_path = '/Users/danieljames/coding/csdc-streamlit/app/vectors_shenzhen'

vectorstore = FAISS.load_local(vectors_path, QianfanEmbeddingsEndpoint(model="bge_large_zh", endpoint="bge_large_zh"), allow_dangerous_deserialization=True)

print(type(vectorstore))
print(dir(vectorstore))