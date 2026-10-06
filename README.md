# AI SQL Analytics Assistant

An AI-powered SQL analytics assistant that converts natural-language questions into SQL queries, executes them against a PostgreSQL database, and presents the results through tables, insights, and visualizations.

## 📌 Project Overview

The AI SQL Analytics Assistant helps users interact with a relational database using natural language instead of manually writing SQL queries.

A user can ask questions such as:

* Which products generated the highest revenue?
* What are the top 10 customers by sales?
* How many orders were placed each month?
* Which category has the highest average profit?

The application processes the question, identifies the required database information, generates or matches the appropriate SQL query, validates the query, executes it, and presents the result in an easy-to-understand format.

## 🎯 Objectives

* Convert natural-language questions into SQL queries.
* Connect an AI assistant with PostgreSQL.
* Validate generated SQL before execution.
* Execute analytical queries safely.
* Provide structured results and insights.
* Generate charts for analytical questions.
* Maintain query history.
* Export analytical results.
* Provide an interactive interface for users.

## 🏗️ Application Workflow

```text
User Question
      ↓
Question Processing
      ↓
Question Matching / Classification
      ↓
SQL Generation
      ↓
SQL Validation
      ↓
PostgreSQL Database
      ↓
Query Execution
      ↓
Result Processing
      ↓
Insights + Visualization + Export
```

## ✨ Key Features

### Natural Language SQL

Users can ask analytical questions using normal English instead of writing SQL manually.

### AI-Powered Query Generation

The application uses an LLM to assist with generating SQL queries from user questions.

### SQL Validation

Generated SQL is validated before execution to reduce unsafe or invalid database operations.

### PostgreSQL Integration

The assistant connects to PostgreSQL and executes analytical queries against the database.

### Question Matching

The project includes a question bank and matching mechanism for recognizing previously defined analytical questions.

### Data Visualization

Query results can be transformed into charts for easier interpretation.

### Business Insights

The application generates useful analytical insights from query results.

### Query History

Previous queries and their results can be tracked for easier reuse and analysis.

### Export

Analytical results can be exported for further use.

### PDF Generation

The application includes functionality for generating PDF-based analytical reports.

## 🛠️ Technologies Used

* Python
* PostgreSQL
* SQL
* Streamlit
* Groq LLM
* SQLAlchemy
* RapidFuzz
* Pandas
* Matplotlib
* Machine Learning / NLP techniques
* HTML / CSS

## 📂 Project Structure

```text
AI_SQL_AnalyticsAssistant/
│
├── app.py
├── chart_generator.py
├── classifier.py
├── config.py
├── database.py
├── executor.py
├── export.py
├── history.py
├── insights.py
├── llm.py
├── matcher.py
├── pdf_generator.py
├── pipeline.py
├── question_bank.py
├── schema.py
├── sql_validator.py
├── utils.py
│
├── .gitignore
└── README.md
```

## 🔑 Core Components

| Component            | Purpose                            |
| -------------------- | ---------------------------------- |
| `app.py`             | Main application interface         |
| `database.py`        | PostgreSQL database connection     |
| `llm.py`             | LLM integration                    |
| `pipeline.py`        | Main processing workflow           |
| `matcher.py`         | Natural-language question matching |
| `classifier.py`      | Question classification            |
| `sql_validator.py`   | SQL validation                     |
| `executor.py`        | SQL execution                      |
| `chart_generator.py` | Chart generation                   |
| `insights.py`        | Analytical insights                |
| `history.py`         | Query history management           |
| `export.py`          | Result export                      |
| `pdf_generator.py`   | PDF report generation              |
| `schema.py`          | Database schema handling           |
| `question_bank.py`   | Analytical question/query bank     |

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/Talluri-Ramesh/ai-sql-analytics-assistant.git
cd ai-sql-analytics-assistant
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

### 3. Activate the virtual environment

```bash
venv\Scripts\activate
```

### 4. Install dependencies

Create a `requirements.txt` file containing the project's required Python packages, then run:

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file locally.

Example:

```env
GROQ_API_KEY=your_groq_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

**Never commit `.env` or API keys to GitHub.**

### 6. Run the application

If the application uses Streamlit:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## 🔐 Security

Sensitive credentials are intentionally excluded from the repository.

The `.gitignore` file prevents files such as:

```text
.env
__pycache__/
venv/
```

from being committed.

## 📊 Example Use Cases

The assistant can support business-analysis questions such as:

* Top-selling products
* Revenue by category
* Monthly sales trends
* Customer purchase analysis
* Employee performance
* Supplier analysis
* Order analysis
* Payment analysis
* Return analysis

## 💡 Why This Project Is Useful

Traditional SQL analytics requires users to understand SQL syntax and database structures.

This project provides a natural-language interface that allows users to ask business questions directly while still using a relational database and SQL-based analytical workflow underneath.

## 🔮 Future Enhancements

* Multi-database support
* Advanced conversational memory
* Automatic dashboard generation
* More sophisticated SQL validation
* Role-based database access
* Query performance optimization
* Cloud deployment
* Advanced natural-language explanations
* Automated analytical report generation

## 👨‍💻 Project

**AI SQL Analytics Assistant**

Built using Python, PostgreSQL, SQL, Streamlit, and LLM-based natural-language processing.

GitHub Repository:

https://github.com/Talluri-Ramesh/ai-sql-analytics-assistant
