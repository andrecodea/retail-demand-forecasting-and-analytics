# Sales Dashboard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Plotly](https://img.shields.io/badge/Plotly%20-%20white?style=for-the-badge&logo=Plotly&labelColor=black&color=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit%20-%20white%20?style=for-the-badge&logo=Streamlit&color=white)

![Demo](sales-dash-demo.gif)

In this project, I used libraries Streamlit, Pandas, and Plotly Express.
The goal of the project is to obtain a structured view of certain data and display it into charts, which includes:

Monthly revenue by branch;
Revenue by product type;
Performance of payment methods;
Total revenue;
Average branch ratings.

## Development Process
1. Import the "supermarket_sales" dataset, read and display this CSV file using the Pandas library.
   - This can be done with the `pd.read_csv()` function.
3. Format and sort the data for better readability.
   - We need to format the data type of the "Date" table from `dtype object`to the `dtype datetime`
5. Create filters for displaying the established objectives using Pandas.
   - We can create filters using a combination of the DataFrames and lambda functions.
7. Create the visual interface elements with streamlit, including columns, checkboxes, and the page structure.
   - We can do this by creating columns with the streamlit `col1, col2 = st.columns(2)` and a checkbox at the sidebar with the `st.sidebar.selectbox()`.
9. Create DataFrames, group the data, and display it through charts.
    - We can group data using the `.groupby()`, and the `sum()` methods.
11. Display bar and pie charts with the grouped data.
    - We can display the charts by using the `px.bar`, `px.pie` and `plotly.chart`

