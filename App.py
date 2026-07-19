import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import re


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 AI Business Analyst")
st.write("Ask a business question about your retail sales data.")


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_NAME = "retail.db"

allowed_tables = {
    "sales"
}

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


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql: str):

    sql_lower = sql.lower()

    # 1️⃣ Only SELECT allowed
    if not sql_lower.strip().startswith("select"):

        return False, "Only SELECT queries are allowed."


    # 2️⃣ Block dangerous keywords
    forbidden = [
        "drop",
        "delete",
        "update",
        "insert",
        "alter",
        "truncate"
    ]

    for word in forbidden:

        if re.search(rf"\b{word}\b", sql_lower):

            return False, f"Forbidden keyword detected: {word}"


    # 3️⃣ Validate table name
    from_match = re.search(
        r"\bfrom\s+([a-z_][a-z0-9_]*)",
        sql_lower
    )

    if not from_match:

        return False, "No FROM clause found."


    table = from_match.group(1)

    if table not in allowed_tables:

        return False, f"Table '{table}' is not allowed."


    # 4️⃣ Extract tokens
    tokens = re.findall(
        r"\b[a-z_][a-z0-9_]*\b",
        sql_lower
    )


    sql_keywords = {

        "select",
        "from",
        "where",
        "group",
        "by",
        "order",
        "limit",

        "sum",
        "count",
        "avg",
        "min",
        "max",

        "as",
        "and",
        "or",

        "strftime",
        "substr",
        "date",

        "desc",
        "asc",

        "is",
        "not",
        "null"

    }


    for token in tokens:

        if (

            token in sql_keywords
            or token in allowed_columns
            or token in allowed_tables
            or token.isdigit()

        ):

            continue


        # Ignore aliases
        if re.search(
            rf"\bas\s+{token}\b",
            sql_lower
        ):

            continue


        return False, f"Column '{token}' is not allowed."


    return True, "SQL is valid"


# ============================================================
# QUESTION PREPROCESSING
# ============================================================

def preprocess(question):

    q = question.lower()


    # Fix common spelling mistakes
    q = q.replace("revenut", "revenue")
    q = q.replace("revanue", "revenue")
    q = q.replace("revnue", "revenue")


    return q


# ============================================================
# RULE-BASED SQL GENERATOR
# ============================================================

def smart_sql_generator(question):

    q = preprocess(question)


    # ========================================================
    # 1️⃣ MONTHLY REVENUE TREND
    # ========================================================

    if (

        ("month" in q or "monthly" in q)
        and "revenue" in q
        and "highest" not in q

    ):

        return """

        SELECT

            substr(InvoiceDate, 1, 7) AS month,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY month

        ORDER BY month;

        """


    # ========================================================
    # 2️⃣ HIGHEST REVENUE MONTH
    # ========================================================

    if (

        (
            "highest" in q
            or "top" in q
            or "maximum" in q
            or "max" in q
        )

        and "month" in q

    ):

        return """

        SELECT

            substr(InvoiceDate, 1, 7) AS month,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY month

        ORDER BY total_revenue DESC

        LIMIT 1;

        """


    # ========================================================
    # 3️⃣ REVENUE BY COUNTRY
    # ========================================================

    if (

        ("country" in q or "countries" in q)

        and "revenue" in q

        and "top" not in q

        and "best" not in q

    ):

        return """

        SELECT

            Country,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY Country

        ORDER BY total_revenue DESC;

        """


    # ========================================================
    # 4️⃣ TOP COUNTRIES
    # ========================================================

    if (

        ("country" in q or "countries" in q)

        and (

            "top" in q
            or "best" in q

        )

    ):

        return """

        SELECT

            Country,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY Country

        ORDER BY total_revenue DESC

        LIMIT 5;

        """


    # ========================================================
    # 5️⃣ TOP PRODUCTS
    # ========================================================

    if (

        ("product" in q or "products" in q)

        and (

            "top" in q
            or "best" in q

        )

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


    # ========================================================
    # 6️⃣ REVENUE BY PRODUCT
    # ========================================================

    if (

        ("product" in q or "products" in q)

        and "revenue" in q

    ):

        return """

        SELECT

            Description,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY Description

        ORDER BY total_revenue DESC;

        """


    # ========================================================
    # 7️⃣ TOP CUSTOMERS
    # ========================================================

    if (

        "customer" in q

        and (

            "top" in q
            or "best" in q

        )

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


    # ========================================================
    # 8️⃣ REVENUE BY CUSTOMER
    # ========================================================

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


    # ========================================================
    # 9️⃣ TOTAL REVENUE
    # ========================================================

    if (

        "total" in q

        and "revenue" in q

    ):

        return """

        SELECT

            SUM(Revenue) AS total_revenue

        FROM sales;

        """


    # ========================================================
    # 🔟 DAILY REVENUE TREND
    # ========================================================

    if (

        ("daily" in q or "date" in q)

        and "revenue" in q

    ):

        return """

        SELECT

            DATE(InvoiceDate) AS date,

            SUM(Revenue) AS total_revenue

        FROM sales

        GROUP BY date

        ORDER BY date;

        """


    return None


# ============================================================
# BUSINESS EXPLANATION
# ============================================================

def generate_explanation(df):

    cols = df.columns.tolist()


    # Monthly trend
    if "month" in cols:

        max_row = df.loc[
            df["total_revenue"].idxmax()
        ]

        return (

            f"Revenue peaked in "

            f"{max_row['month']} "

            f"with total revenue of "

            f"{round(max_row['total_revenue'], 2)}."

        )


    # Country analysis
    elif "Country" in cols:

        top_country = df.iloc[0]

        return (

            f"{top_country['Country']} "

            f"generated the highest revenue of "

            f"{round(top_country['total_revenue'], 2)}."

        )


    # Product analysis
    elif "Description" in cols:

        top_product = df.iloc[0]

        return (

            f"The top-performing product is "

            f"'{top_product['Description']}' "

            f"with revenue of "

            f"{round(top_product['total_revenue'], 2)}."

        )


    # Customer analysis
    elif "CustomerID" in cols:

        top_customer = df.iloc[0]

        return (

            f"Customer ID "

            f"{int(top_customer['CustomerID'])} "

            f"generated the highest revenue of "

            f"{round(top_customer['total_revenue'], 2)}."

        )


    # Total revenue
    elif (

        "total_revenue" in cols

        and len(df) == 1

    ):

        return (

            f"Total revenue is "

            f"{round(df['total_revenue'].iloc[0], 2)}."

        )


    return "No significant insights found."


# ============================================================
# QUERY EXECUTION AND CHART
# ============================================================

def run_query_and_plot(sql_query):

    conn = sqlite3.connect(DB_NAME)


    df = pd.read_sql(

        sql_query,

        conn

    )


    conn.close()


    # Show result table
    st.subheader("📋 Query Result")

    st.dataframe(df)


    # ========================================================
    # MONTHLY REVENUE
    # ========================================================

    if "month" in df.columns:

        st.subheader("📈 Monthly Revenue")


        fig, ax = plt.subplots(
            figsize=(10, 5)
        )


        ax.plot(

            df["month"],

            df["total_revenue"]

        )


        ax.set_xlabel("Month")

        ax.set_ylabel("Revenue")

        ax.set_title("Monthly Revenue")


        plt.xticks(
            rotation=45
        )


        st.pyplot(fig)


    # ========================================================
    # COUNTRY REVENUE
    # ========================================================

    elif "Country" in df.columns:

        st.subheader("🌍 Revenue by Country")


        fig, ax = plt.subplots(
            figsize=(10, 5)
        )


        ax.barh(

            df["Country"],

            df["total_revenue"]

        )


        ax.set_xlabel("Revenue")

        ax.set_ylabel("Country")

        ax.set_title("Revenue by Country")


        ax.invert_yaxis()


        st.pyplot(fig)


    # ========================================================
    # CUSTOMER REVENUE
    # ========================================================

    elif "CustomerID" in df.columns:

        st.subheader("👥 Top Customers")


        fig, ax = plt.subplots(
            figsize=(10, 5)
        )


        ax.barh(

            df["CustomerID"].astype(str),

            df["total_revenue"]

        )


        ax.set_xlabel("Revenue")

        ax.set_ylabel("Customer ID")

        ax.set_title("Top Customers")


        ax.invert_yaxis()


        st.pyplot(fig)


    # ========================================================
    # PRODUCT REVENUE
    # ========================================================

    elif "Description" in df.columns:

        st.subheader("🛍️ Top Products")


        fig, ax = plt.subplots(
            figsize=(10, 5)
        )


        ax.barh(

            df["Description"],

            df["total_revenue"]

        )


        ax.set_xlabel("Revenue")

        ax.set_ylabel("Product")

        ax.set_title("Top Products")


        ax.invert_yaxis()


        st.pyplot(fig)


    # ========================================================
    # BUSINESS INSIGHT
    # ========================================================

    explanation = generate_explanation(df)


    st.subheader("💡 Business Insight")


    st.success(explanation)


# ============================================================
# STREAMLIT USER INTERFACE
# ============================================================

user_question = st.text_input(

    "💬 Ask a business question:",

    placeholder="Example: Which month has highest revenue?"

)


if st.button("🔍 Analyze"):


    if not user_question:

        st.warning(

            "Please enter a business question."

        )


    else:

        # Generate SQL
        sql_query = smart_sql_generator(
            user_question
        )


        if not sql_query:

            st.error(

                "Sorry, I couldn't understand the question."

            )


        else:

            # Show SQL
            st.subheader("🧠 Generated SQL")


            st.code(

                sql_query,

                language="sql"

            )


            # Validate SQL
            is_valid, message = validate_sql(
                sql_query
            )


            if is_valid:

                st.success(

                    f"Validation: {message}"

                )


                # Execute query and plot
                run_query_and_plot(
                    sql_query
                )


            else:

                st.error(

                    f"Query blocked: {message}"

                )