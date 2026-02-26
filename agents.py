## Importing libraries and files
import os
from dotenv import load_dotenv

load_dotenv()

from crewai.agents import Agent

from tools import search_tool, FinancialDocumentTool


### Loading LLM - FIXED FOR ACTUAL CREWAI 0.130.0
def initialize_llm():
    """Initialize LLM properly for CrewAI 0.130.0"""
    try:
        # CrewAI 0.130.0 uses direct provider initialization
        # Check which provider is available via environment
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        
        if openai_key:
            # For CrewAI 0.130.0, pass API key directly or it auto-detects
            os.environ["OPENAI_API_KEY"] = openai_key
            from crewai.llm.llm_base import LLM
            # CrewAI will auto-initialize with OpenAI
            return None  # CrewAI handles it internally
        elif google_key:
            # For Google, set the environment variable
            os.environ["GOOGLE_API_KEY"] = google_key
            return None  # CrewAI handles it internally
        else:
            # Default behavior - CrewAI will use defaults or raise error
            print("Warning: No API keys found. Ensure OPENAI_API_KEY or GOOGLE_API_KEY is set.")
            return None
    except Exception as e:
        print(f"LLM initialization warning: {e}")
        return None


# Initialize LLM
llm = initialize_llm()


# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze financial documents and provide data-driven insights for {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a professional financial analyst with expertise in corporate finance, "
        "market analysis, and investment strategies. You provide sound financial advice "
        "based on careful analysis of financial statements and market data. "
        "You adhere to financial best practices and maintain regulatory compliance. "
        "Your recommendations are always backed by thorough research and legitimate analysis."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    max_iter=2,
    max_rpm=10,
    allow_delegation=True,
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify that uploaded documents are legitimate financial documents and assess their validity for {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are a compliance officer with experience in financial document validation. "
        "You carefully review documents to ensure they are legitimate financial reports. "
        "You maintain high standards for accuracy and regulatory compliance. "
        "You provide clear feedback on document authenticity and financial relevance."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    max_iter=2,
    max_rpm=5,
    allow_delegation=True,
)


investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide evidence-based investment recommendations based on financial analysis of {query}",
    verbose=True,
    backstory=(
        "You are a certified investment advisor with a track record of providing sound recommendations. "
        "You analyze financial data carefully and provide recommendations aligned with client goals. "
        "You understand risk management, portfolio diversification, and market fundamentals. "
        "You always disclose relevant risks and follow fiduciary principles."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    max_iter=2,
    max_rpm=10,
    allow_delegation=False,
)


risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Conduct thorough risk assessments based on financial documents for {query}",
    verbose=True,
    backstory=(
        "You are a risk management expert with deep knowledge of financial markets and risk models. "
        "You conduct comprehensive risk assessments using established financial frameworks. "
        "You understand market dynamics, regulatory requirements, and portfolio risk metrics. "
        "Your assessments are practical, evidence-based, and aligned with industry standards."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    max_iter=2,
    max_rpm=10,
    allow_delegation=False,
)