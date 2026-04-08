from scrape_aijn import AIscraper
from build_job_database import dbBuilder
import agent


scraper = AIscraper()
scraper.run()
scraped_data = scraper.scraped_jobs

profile = """
    Title: Mid-Level AI Engineer. 
    Skills: Python, pandas, scikit-learn, SQL, Neural Networks, Machine Learning, Deep Learning, ChromaDB, Pinecone, Weaviate, LangChain, RAG. 
    Experience: 4 years building databases, pipelines and agentic workflows.
    """
builder = dbBuilder(scraped_data, profile)
builder.run()
match_output = builder.output

agent = agent.CareerMatchAgent()
job_contexts = agent.format_chroma_results(match_output)

if job_contexts:
    print("\n--- Final Analysis ---\n")
    for j in range(len(job_contexts)):
        try:
            analysis_result = agent.analyze_candidate(profile, job_contexts[j])
        except Exception as e:
            if "503" in str(e):
                print(f"Server busy for job {j}. Skipping or saving for later...")
                analysis_result = None
            else:
                raise e
        print(f"--- MATCH {j + 1} ---")
        print(f"Fit Summary: {analysis_result.fit_summary}")
        print(f"Gap: {analysis_result.skill_gap}")
        print(f"Action: {analysis_result.learning_action}\n")
