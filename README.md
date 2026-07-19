# 📊 AI Business Analyst

An interactive **AI Business Analyst application** built with Python, SQL, and Streamlit.

This project allows users to ask business questions about retail sales data in natural language. The system converts business questions into SQL queries, validates the queries, executes them on a SQLite database, generates visualizations, and provides business insights.

---

## 🚀 Live Demo

🔗 Coming soon

---

## 📌 Project Overview

Business users often need to ask questions such as:

- Which month generated the highest revenue?
- What are the top countries by revenue?
- Who are the best customers?
- What are the top-selling products?

Instead of manually writing SQL queries, users can ask questions using a simple interface.

The application automatically:

1. Understands the business question
2. Generates the appropriate SQL query
3. Validates the SQL query
4. Executes the query
5. Displays the results
6. Generates a visualization
7. Provides a business insight

---

## 🛠️ Technologies Used

- **Python**
- **Pandas**
- **SQLite**
- **SQL**
- **Streamlit**
- **Matplotlib**
- **Regular Expressions**

---

## 📂 Dataset

The project uses the **Online Retail Dataset**.

The dataset contains retail transaction data with information about:

- Invoice number
- Product code
- Product description
- Quantity
- Invoice date
- Unit price
- Customer ID
- Country

---

## 🧹 Data Cleaning

The following data cleaning steps were performed:

- Removed missing product descriptions
- Removed missing customer IDs
- Removed duplicate records
- Removed invalid quantities
- Removed zero and negative prices
- Cleaned product descriptions
- Removed unwanted characters
- Created a new `Revenue` column

### Revenue Calculation

```text
Revenue = Quantity × UnitPrice