import chromadb
from chromadb.api.models.Collection import Collection
import os
from job_record import JobRecord


class dbBuilder:

    def __init__(self, jobs, profile):
        self.dbpath = os.getenv("DB_PATH")
        self.jobs = jobs
        self.profile = profile

    def create_document_string(self, j: JobRecord) -> str:
        searchable_data = j.model_dump(
            exclude_none=True,
            include={'tech_stack', 'responsibilities', 'benefits'}
        )
        valid_items = [f"{key.replace('_', ' ').title()}: {val}" for key, val in searchable_data.items()]
        return ". ".join(valid_items)

    def create_db(self) -> Collection:
        chroma_client = chromadb.PersistentClient(path=self.dbpath)

        # Check is an older version of the db exists
        try:
            chroma_client.delete_collection(name="ai_jobs_vector_db")
        except Exception:
            print("No existing ai_jobs_vector_db. Create new one.")

        db = chroma_client.get_or_create_collection(name="ai_jobs_vector_db")
        ids = [job.id for job in self.jobs]
        metadata = [job.model_dump(exclude={'tech_stack','responsibilities', 'benefits'}) for job in self.jobs]
        documents = [self.create_document_string(job) for job in self.jobs]
        db.add(
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        return db

    def query_match(self, db: Collection) -> dict:
        results = db.query(
            query_texts=[self.profile],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

        for i in range(len(results['documents'][0])):
            print(f"Match {i + 1} (Distance: {results['distances'][0][i]}):")
            print(f"Job Info: {results['metadatas'][0][i]}")
            print(f"Description: {results['documents'][0][i]}\n")

        return results

    def run(self):
        db = self.create_db()
        self.output = self.query_match(db)