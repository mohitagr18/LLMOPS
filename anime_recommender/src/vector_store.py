from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()


class VectorStoreBuilder:
    def __init__(self, csv_path: str, persist_dir: str = None):
        self.csv_path = csv_path
        
        # Get the anime_recommender package root directory
        PACKAGE_ROOT = Path(__file__).resolve().parent.parent
        
        # Set persist_dir to chroma_db inside anime_recommender if not provided
        if persist_dir is None:
            self.persist_dir = str(PACKAGE_ROOT / "chroma_db")
        else:
            self.persist_dir = persist_dir
            
        # Create the directory if it doesn't exist
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    def build_and_save_vectorstore(self):
        loader = CSVLoader(
            file_path=self.csv_path,
            encoding='utf-8',
            metadata_columns=[]
        )

        data = loader.load()

        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = splitter.split_documents(data)

        db = Chroma.from_documents(texts, self.embedding, persist_directory=self.persist_dir)
        db.persist()

    def load_vector_store(self):
        return Chroma(persist_directory=self.persist_dir, embedding_function=self.embedding)
