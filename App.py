import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-3.5-flash-lite")
else:
    gemini_model = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Main container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Header */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 17px;
        margin-bottom: 25px;
    }

    /* KPI cards */
    .metric-card {
        background: linear-gradient(
            135deg,
            #1f2937,
            #111827
        );

        border: 1px solid #374151;

        border-radius: 14px;

        padding: 20px;

        margin-bottom: 10px;

        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }

    .metric-title {
        color: #9ca3af;
        font-size: 14px;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 27px;
        font-weight: 700;
        color: white;
    }

    /* Insight box */
    .insight-box {
        background: linear-gradient(
            135deg,
            #172554,
            #111827
        );

        border-left: 4px solid #3b82f6;

        padding: 20px;

        border-radius: 10px;

        margin-top: 10px;

        margin-bottom: 20px;
    }

    .insight-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .insight-text {
        font-size: 16px;
        color: #d1d5db;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
    }

    /* SQL code */
    code {
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

DB_PATH = "retail.db"


@st.cache_resource
def get_connection():

    if not os.path.exists(DB_PATH):
        st.error(
            "❌ retail.db was not found. "
            "Make sure retail.db is in the same folder as App.py."
        )
        st.stop()

    # check_same_thread=False is needed because Streamlit can reuse
    # this cached connection across different internal threads.
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# ============================================================
# CHECK DATABASE
# ============================================================

def check_database():

    try:

        conn = get_connection()

        tables = pd.read_sql(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """,
            conn
        )

        return tables["name"].tolist()

    except Exception:

        return []


# ============================================================
# CONVERSATION MEMORY
# ============================================================

MAX_HISTORY_TURNS = 3


def init_conversation_state():

    if "conversation" not in st.session_state:

        st.session_state.conversation = []


def build_history_context():
    """
    Turns the last few Q&A pairs into a short text block for the
    Gemini prompt, so follow-up questions like "now just for
    Germany" can be resolved against the previous question's SQL.
    """

    recent = st.session_state.conversation[-MAX_HISTORY_TURNS:]

    if not recent:
        return ""

    lines = []

    for turn in recent:

        lines.append(
            f"Q: {turn['question']}\nSQL: {turn['sql'].strip()}"
        )

    return "\n\n".join(lines)


def add_to_conversation(question, sql_query):

    st.session_state.conversation.append(
        {"question": question, "sql": sql_query}
    )

    # Keep it bounded so it never grows unbounded in one long session
    st.session_state.conversation = (
        st.session_state.conversation[-MAX_HISTORY_TURNS:]
    )


tables = check_database()

init_conversation_state()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🧠 AI Business Analyst")

    st.markdown("---")

    st.markdown("### 📌 Example Questions")

    example_questions = [
        "What is the total revenue?",
        "Show monthly revenue",
        "Which month had the highest revenue?",
        "Show revenue by country",
        "What are the top countries?",
        "What are the top products?",
        "Who are the top customers?",
        "Show customer revenue"
    ]

    selected_question = st.selectbox(
        "Try an example:",
        ["Select a question"] + example_questions
    )

    st.markdown("---")

    st.markdown("### 🗄️ Database")

    if "sales" in tables:

        st.success("Database connected")

        st.caption("Table: sales")

    else:

        st.error("Sales table not found")

    st.markdown("---")

    st.markdown("### 🧠 AI Engine")

    if gemini_model:

        st.success("Gemini connected")

    else:

        st.error("GEMINI_API_KEY not found")

        st.caption("Add it to your .env file")

    st.markdown("---")

    st.markdown("### 💬 Conversation Memory")

    if st.session_state.conversation:

        for turn in reversed(st.session_state.conversation):

            st.caption(f"• {turn['question']}")

        if st.button("🗑️ Clear conversation", use_container_width=True):

            st.session_state.conversation = []

            st.rerun()

    else:

        st.caption("No questions yet this session.")

    st.markdown("---")

    st.markdown(
        """
        **Built with**

        🐍 Python  
        🐼 Pandas  
        🗄️ SQLite  
        📊 Matplotlib  
        🎈 Streamlit  
        ✨ Gemini
        """
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📊 AI Business Analyst</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Ask business questions in natural language and get
    SQL queries, data analysis, charts and business insights.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUESTION INPUT
# ============================================================

st.markdown("### 🔎 Ask a Business Question")

if selected_question != "Select a question":

    default_question = selected_question

else:

    default_question = ""


user_question = st.text_input(
    "Enter your question",
    value=default_question,
    placeholder="Example: Which country generated the highest revenue?",
    label_visibility="collapsed"
)


analyze_button = st.button(
    "🚀 Analyze",
    type="primary",
    use_container_width=True
)


# ============================================================
# SQL VALIDATION
# ============================================================

allowed_tables = {"sales"}

allowed_columns = {
    "invoiceno",
    "stockcode",
    "description",
    "quantity",
    "invoicedate",
    "unitprice",
    "customerid",
    "country",
    "revenue"
}


def validate_sql(sql):

    if not sql:

        return False, "SQL query is empty."

    sql_lower = sql.lower()

    # Only a single statement
    if sql_lower.strip().rstrip(";").count(";") > 0:

        return False, "Multiple SQL statements are not allowed."

    # Only SELECT
    if not sql_lower.strip().startswith("select"):

        return False, "Only SELECT queries are allowed."

    # Dangerous keywords
    forbidden = [
        "drop",
        "delete",
        "update",
        "insert",
        "alter",
        "truncate",
        "attach",
        "pragma",
        "create"
    ]

    for word in forbidden:

        if re.search(
            rf"\b{word}\b",
            sql_lower
        ):

            return False, f"Forbidden keyword detected: {word}"

    # Check table
    if "sales" not in sql_lower:

        return False, "Unauthorized table used."

    # NOTE: We deliberately do NOT do identifier-by-identifier
    # whitelisting here. That approach was tried and kept breaking on
    # legitimate SQL (substr(), string literals like 'France', HAVING,
    # JOIN, window functions, etc.) — an unbounded whack-a-mole problem.
    # Since this database has exactly one table (sales) and the checks
    # above already block writes/schema changes, multi-statement
    # injection, and any query not touching "sales", the real attack
    # surface here is small. If you add more tables to retail.db later,
    # revisit this and add an explicit check that FROM/JOIN only ever
    # reference "sales".

    return True, "SQL is valid."


# ============================================================
# QUESTION PREPROCESSING
# ============================================================

def preprocess(question):

    q = question.lower()

    q = q.replace("revenut", "revenue")
    q = q.replace("revanue", "revenue")

    return q


# ============================================================
# DATABASE SCHEMA (given to the LLM)
# ============================================================

SCHEMA_DESCRIPTION = """
Table: sales
Columns:
- InvoiceNo (text)
- StockCode (text)
- Description (text) - product name
- Quantity (integer)
- InvoiceDate (text, format 'YYYY-MM-DD ...') - use substr(InvoiceDate,1,7) for month
- UnitPrice (real)
- CustomerID (integer, may be NULL)
- Country (text)
- Revenue (real) - pre-computed revenue for each row, use SUM(Revenue) for totals
"""


# ============================================================
# SQL GENERATOR (KEYWORD FALLBACK)
# ============================================================
# Kept as a fallback in case Gemini is unavailable or the API call
# fails, so the app degrades gracefully instead of breaking.

def keyword_sql_generator(question):

    q = preprocess(question)

    if (
        ("month" in q or "monthly" in q)
        and "revenue" in q
        and "highest" not in q
    ):

        return """
        SELECT
            substr(InvoiceDate,1,7) AS month,
            SUM(Revenue) AS total_revenue
        FROM sales
        GROUP BY month
        ORDER BY month;
        """

    if (
        ("highest" in q or "top" in q or "maximum" in q)
        and "month" in q
    ):

        return """
        SELECT
            substr(InvoiceDate,1,7) AS month,
            SUM(Revenue) AS total_revenue
        FROM sales
        GROUP BY month
        ORDER BY total_revenue DESC
        LIMIT 1;
        """

    if (
        ("country" in q or "countries" in q)
        and ("top" in q or "best" in q)
    ):

        return """
        SELECT
            Country,
            SUM(Revenue) AS total_revenue
        FROM sales
        GROUP BY Country
        ORDER BY total_revenue DESC
        LIMIT 10;
        """

    if (
        ("country" in q or "countries" in q)
        and "revenue" in q
    ):

        return """
        SELECT
            Country,
            SUM(Revenue) AS total_revenue
        FROM sales
        GROUP BY Country
        ORDER BY total_revenue DESC;
        """

    if (
        ("product" in q or "products" in q)
        and ("top" in q or "best" in q)
    ):

        return """
        SELECT
            Description,
            SUM(Revenue) AS total_revenue
        FROM sales
        GROUP BY Description
        ORDER BY total_revenue DESC
        LIMIT 10;
        """

    if (
        "customer" in q
        and ("top" in q or "best" in q)
    ):

        return """
        SELECT
            CustomerID,
            SUM(Revenue) AS total_revenue
        FROM sales
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
        ORDER BY total_revenue DESC
        LIMIT 10;
        """

    if (
        "customer" in q
        and "revenue" in q
    ):

        return """
        SELECT
            CustomerID,
            SUM(Revenue) AS total_revenue
        FROM sales
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
        ORDER BY total_revenue DESC;
        """

    if (
        "total" in q
        and "revenue" in q
    ):

        return """
        SELECT
            SUM(Revenue) AS total_revenue
        FROM sales;
        """

    return None


# ============================================================
# SQL GENERATOR (GEMINI)
# ============================================================

def clean_sql_response(text):
    """Strip markdown fences and stray text Gemini sometimes adds."""

    text = text.strip()

    text = re.sub(r"^```sql", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    return text


@st.cache_data(show_spinner=False)
def _call_gemini_cached(question, history_context):
    """
    Cached on (question, history_context) together — so the same
    question text asked with different prior context is NOT served
    a stale cached answer. Only successful responses are cached
    (this raises on failure instead of returning an error tuple),
    so a transient API error is never "stuck" in the cache — the
    next attempt will hit the API again.
    """

    if history_context:
        conversation_section = f"""
Recent conversation (most recent last), for resolving follow-up
questions that refer back to a previous one (e.g. "now just for
Germany", "same but by month", "what about last year"):

{history_context}

Use this history ONLY to resolve references, omitted filters, or
follow-up refinements in the new question below. If the new question
is fully self-contained, ignore the history entirely.
"""
    else:
        conversation_section = ""

    prompt = f"""You are a SQL generator for a SQLite database.

Schema:
{SCHEMA_DESCRIPTION}

Rules:
- Return ONLY a single valid SQLite SELECT statement, nothing else.
- No markdown formatting, no explanation, no comments.
- Only query the "sales" table using the columns listed above.
- Never use DROP, DELETE, UPDATE, INSERT, ALTER, ATTACH, or PRAGMA.
- Alias aggregate revenue columns as total_revenue when summing Revenue.
- ALWAYS include at least one numeric metric column in the SELECT
  (e.g. SUM(Revenue), SUM(Quantity), COUNT(*), AVG(...)) alongside
  any label column (Description, Country, CustomerID, month) —
  never return a label by itself with no number attached, even if
  the question only asks for a name (e.g. "least popular product"
  must still return that product's quantity or revenue next to it,
  so the result can be explained and charted).
- When ranking by "popularity" or similar, use SUM(Quantity) as the
  metric unless the question specifies revenue.
- NEVER exclude, filter out, or omit any country, product, or
  customer that the question didn't explicitly ask to exclude. In
  particular, always include the United Kingdom / any dominant
  category in "by country" or similar breakdowns unless the user
  explicitly asks to exclude it (e.g. "excluding the UK", "other
  than the UK"). Do not decide on your own that excluding the
  largest category makes a "better" or "more readable" result —
  return the complete, literal answer to the question asked.
{conversation_section}
Question: {question}

SQL:"""

    response = gemini_model.generate_content(prompt)

    return clean_sql_response(response.text)


def gemini_sql_generator(question, history_context=""):

    if not gemini_model:
        return None, "Gemini API key is not configured."

    try:

        sql = _call_gemini_cached(question, history_context)

        return sql, None

    except Exception as e:

        return None, str(e)


def smart_sql_generator(question, history_context=""):
    """
    Tries Gemini first (with conversation history for follow-up
    questions). Falls back to the keyword-based generator if Gemini
    is unavailable or fails — the fallback has no concept of history,
    since it only pattern-matches the current question in isolation.
    """

    if gemini_model:

        sql, error = gemini_sql_generator(question, history_context)

        if sql:

            return sql, "gemini", None

        # Gemini failed — fall back, but surface the error
        fallback_sql = keyword_sql_generator(question)

        return fallback_sql, "fallback", error

    fallback_sql = keyword_sql_generator(question)

    return fallback_sql, "fallback", None


# ============================================================
# BUSINESS EXPLANATION
# ============================================================

def _is_filtered_result(sql_query):
    """
    Rough check for whether the SQL restricts which rows are included
    (WHERE / HAVING clause present). Used so the insight text doesn't
    imply a filtered result is the overall/global leader when it's
    only the leader within whatever subset the query happened to
    include or exclude.
    """

    if not sql_query:
        return False

    sql_lower = sql_query.lower()

    return "where" in sql_lower or "having" in sql_lower


def generate_explanation(df, sql_query=None):

    cols = df.columns.tolist()

    if df.empty:
        return "The query returned no rows."

    numeric_cols = [
        c for c in cols
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    value_col = "total_revenue" if "total_revenue" in cols else (
        numeric_cols[0] if numeric_cols else None
    )

    label = "revenue" if value_col == "total_revenue" else (
        value_col.replace("_", " ") if value_col else None
    )

    filtered = _is_filtered_result(sql_query)
    scope_note = " among these results" if filtered else ""

    if "month" in cols and value_col:

        max_row = df.loc[df[value_col].idxmax()]

        return (
            f"{label.capitalize()} peaked in {max_row['month']} "
            f"at {max_row[value_col]:,.2f}{scope_note}."
        )

    elif "Country" in cols and value_col:

        top = df.loc[df[value_col].idxmax()]

        return (
            f"{top['Country']} leads on {label}{scope_note} "
            f"with {top[value_col]:,.2f}."
        )

    elif "Description" in cols and value_col:

        top = df.loc[df[value_col].idxmax()]

        return (
            f"The top result{scope_note} is {top['Description']} "
            f"with {label} of {top[value_col]:,.2f}."
        )

    elif "CustomerID" in cols and value_col:

        top = df.loc[df[value_col].idxmax()]

        return (
            f"Customer {top['CustomerID']} leads on {label}{scope_note} "
            f"with {top[value_col]:,.2f}."
        )

    elif value_col and len(df) == 1:

        return f"{label.capitalize()} is {df[value_col].iloc[0]:,.2f}."

    elif len(df) == 1:

        # No numeric column at all — describe the single row directly
        # instead of giving up.
        row = df.iloc[0]
        parts = [f"{col}: {row[col]}" for col in cols]
        return "Result — " + ", ".join(parts) + "."

    elif not numeric_cols and len(df) > 1:

        return (
            f"The query returned {len(df)} rows with no numeric "
            f"metric to summarize — see the table above for details."
        )

    return "See the table above for the full result."


# ============================================================
# QUERY EXECUTION
# ============================================================

@st.cache_data(show_spinner=False)
def run_query(sql_query):
    """
    Cached by the exact SQL text. If the same question (and therefore
    the same generated SQL) is asked again, this returns instantly
    from cache instead of hitting SQLite again.
    """
    conn = get_connection()
    return pd.read_sql(sql_query, conn)


def run_query_and_plot(sql_query):

    try:

        df = run_query(sql_query)

    except Exception as e:

        st.error(
            f"❌ Database Error: {e}"
        )

        return

    # ========================================================
    # QUERY RESULT
    # ========================================================

    st.markdown("### 📋 Query Result")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # KPI SECTION
    # ========================================================

    if "total_revenue" in df.columns:

        total = df["total_revenue"].sum()

        average = df["total_revenue"].mean()

        highest = df["total_revenue"].max()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">
                        💰 Total Revenue
                    </div>
                    <div class="metric-value">
                        £{total:,.0f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">
                        📊 Average
                    </div>
                    <div class="metric-value">
                        £{average:,.0f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">
                        🏆 Highest
                    </div>
                    <div class="metric-value">
                        £{highest:,.0f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ========================================================
    # CHART SECTION
    # ========================================================

    st.markdown("### 📈 Visualization")

    # Find a numeric column to plot against, since Gemini-generated
    # queries won't always name it "total_revenue" (could be a count,
    # an average, etc). Prefer "total_revenue" if present, otherwise
    # fall back to the first numeric column found.
    numeric_cols = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    if "total_revenue" in df.columns:
        value_col = "total_revenue"
    elif numeric_cols:
        value_col = numeric_cols[0]
    else:
        value_col = None

    if "month" in df.columns and value_col:

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(
            df["month"],
            df[value_col],
            marker="o",
            linewidth=2
        )

        ax.set_title("Monthly Trend", fontsize=18, fontweight="bold")
        ax.set_xlabel("Month")
        ax.set_ylabel(value_col.replace("_", " ").title())
        ax.tick_params(axis="x", rotation=45)
        ax.grid(alpha=0.2)

        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)

    elif "Country" in df.columns and value_col:

        chart_df = df.nlargest(15, value_col).copy()
        chart_df = chart_df.sort_values(value_col)

        fig, ax = plt.subplots(figsize=(12, 7))

        ax.barh(chart_df["Country"], chart_df[value_col])

        ax.set_title("By Country", fontsize=18, fontweight="bold")
        ax.set_xlabel(value_col.replace("_", " ").title())
        ax.set_ylabel("Country")

        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)

    elif "CustomerID" in df.columns and value_col:

        chart_df = df.nlargest(10, value_col).copy()
        chart_df = chart_df.sort_values(value_col)

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.barh(chart_df["CustomerID"].astype(str), chart_df[value_col])

        ax.set_title("By Customer", fontsize=18, fontweight="bold")
        ax.set_xlabel(value_col.replace("_", " ").title())
        ax.set_ylabel("Customer ID")

        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)

    elif "Description" in df.columns and value_col:

        chart_df = df.nlargest(10, value_col).copy()
        chart_df = chart_df.sort_values(value_col)

        chart_df["Description"] = (
            chart_df["Description"].astype(str).str[:35]
        )

        fig, ax = plt.subplots(figsize=(12, 7))

        ax.barh(chart_df["Description"], chart_df[value_col])

        ax.set_title("By Product", fontsize=18, fontweight="bold")
        ax.set_xlabel(value_col.replace("_", " ").title())
        ax.set_ylabel("Product")

        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)

    else:

        st.caption(
            "No chart available for this result shape — "
            "showing the table above only."
        )

    # ========================================================
    # BUSINESS INSIGHT
    # ========================================================

    explanation = generate_explanation(df, sql_query)

    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">💡 Business Insight</div>
            <div class="insight-text">{explanation}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN ANALYSIS
# ============================================================

if analyze_button:

    if not user_question.strip():

        st.warning("⚠️ Please enter a business question.")

    else:

        history_context = build_history_context()

        with st.spinner("🧠 Analyzing your question..."):

            sql_query, source, gen_error = smart_sql_generator(
                user_question, history_context
            )

        # ====================================================
        # SQL NOT UNDERSTOOD / GENERATION FAILED
        # ====================================================

        if not sql_query:

            st.warning("🤔 I couldn't understand that question yet.")

            if gen_error:

                st.caption(f"AI engine error: {gen_error}")

            st.info("Try one of the example questions from the sidebar.")

        else:

            # =================================================
            # SOURCE INDICATOR
            # =================================================

            if source == "gemini":

                st.caption("✨ SQL generated by Gemini")

                if history_context:

                    st.caption("🧠 Used earlier conversation as context")

            else:

                st.caption("🔤 SQL generated by keyword fallback")

                if gen_error:

                    st.caption(f"(Gemini unavailable: {gen_error})")

            # =================================================
            # GENERATED SQL
            # =================================================

            with st.expander("🧠 View Generated SQL", expanded=False):

                st.code(sql_query, language="sql")

            # =================================================
            # VALIDATE
            # =================================================

            is_valid, message = validate_sql(sql_query)

            if is_valid:

                st.success("✅ SQL validation passed")

                run_query_and_plot(sql_query)

                # Only remember turns that actually produced valid,
                # runnable SQL — a failed/blocked question shouldn't
                # pollute the context for the next question.
                add_to_conversation(user_question, sql_query)

            else:

                st.error(f"❌ Query blocked: {message}")


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#6b7280;">
        AI Business Analyst • Python • Gemini • SQLite • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)