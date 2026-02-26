from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import logging
from pathlib import Path

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial document analysis system using CrewAI",
    version="1.0.0",
)


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Execute the crew to analyze financial documents

    Args:
        query (str): User's analysis query
        file_path (str): Path to the uploaded financial document

    Returns:
        str: Analysis results from the crew
    """
    try:
        logger.info(f"Starting crew analysis with query: {query}")

        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[analyze_financial_document],
            process=Process.sequential,
        )

        result = financial_crew.kickoff({"query": query})
        logger.info("Crew analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error running crew: {str(e)}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Financial Document Analyzer API is running",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "operational",
        "service": "Financial Document Analyzer",
        "environment": "ready",
    }


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(
        default="Analyze this financial document for investment insights"
    ),
):
    """Analyze financial document and provide comprehensive recommendations

    Args:
        file (UploadFile): Financial document to analyze (PDF)
        query (str): User's specific analysis question/request

    Returns:
        dict: Analysis results including status, query, and analysis content
    """

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Validate file
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported. Please upload a .pdf file.",
            )

        # Save uploaded file
        logger.info(f"Saving file: {file.filename}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved successfully: {file_path}")

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Process the financial document
        logger.info(f"Processing document: {file.filename} with query: {query}")
        response = run_crew(query=query.strip(), file_path=file_path)

        return {
            "status": "success",
            "query": query.strip(),
            "analysis": str(response),
            "file_processed": file.filename,
            "document_id": file_id,
        }

    except HTTPException as e:
        logger.error(f"HTTP Error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error processing financial document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}",
        )

    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as cleanup_error:
                logger.warning(
                    f"Could not delete file {file_path}: {str(cleanup_error)}"
                )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Financial Document Analyzer API...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)