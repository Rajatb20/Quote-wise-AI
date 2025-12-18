# QuoteWise AI 🚀

> **Intelligent Quotation System powered by Azure AI & CrewAI**

QuoteWise AI is a refined, production-grade application designed to automate the generation of professional business quotations. Leveraging the power of multi-agent systems, it analyzes customer requests, scouts for market events, calculates strategic pricing, and generates polished PDF documents—all through a modern Streamlit interface.

## 🌟 Key Features

- **Multi-Agent Orchestration**: Powered by CrewAI to handle complex tasks like data fetching, pricing, and risk assessment.
- **Smart Pricing Engine**: Dynamic pricing logic that adapts to market trends and upcoming events.
- **Professional PDF Generation**: Automated creation of branded, compliant quotation documents.
- **Interactive UI**: A sleek, responsive dashboard built with Streamlit.
- **Analytics & Logging**: Comprehensive logging and analytics for tracking system performance and business metrics.

## 🛠️ Architecture

The system is built on a modular architecture:

- **Frontend**: Streamlit (Python)
- **AI Orchestration**: CrewAI with Azure OpenAI / Google Gemini
- **Backend Components**:
  - `src/components`: UI rendering and Analytics
  - `src/crew.py`: Agent definitions and task workflows
  - `src/tools`: Custom tools for product search, PDF creation, and pricing
  - `src/utils`: Configuration, Caching, and Logging utilities

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Azure OpenAI or Google Gemini API Keys
- Serper API Key (for search capabilities)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-org/quotewise-ai.git
    cd quotewise-ai
    ```

2. **Set up the environment:**

    ```bash
    # Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables:**
    Copy `.env.example` to `.env` and fill in your API keys:

    ```bash
    cp env.example .env
    ```

### Running the Application

To start the QuoteWise AI dashboard:

```bash
streamlit run src/main.py
```

## 🐳 Docker Deployment

Building and running with Docker is recommended for production:

```bash
# Build the image
docker build -t quotewise-ai .

# Run the container
docker run -p 8501:8501 --env-file .env quotewise-ai
```

## 🧪 Testing

Run the test suite to verify system integrity:

```bash
python tests/test_app.py
```

## 📄 License

This project is licensed under the MIT License.
