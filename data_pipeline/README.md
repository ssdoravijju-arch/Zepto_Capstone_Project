# Module 1 - Data Pipeline

## Overview

This module implements an end-to-end data pipeline for books data using web scraping, data cleaning, currency conversion, SQLite database storage, SQL analysis, and pandas validation.

## Data Source

Source website: books.toscrape.com

The pipeline collects book information using Python requests and BeautifulSoup.

The final dataset contains:

- 100 books
- 29 categories
- Book title
- Price in GBP
- Price in INR
- Star rating
- Availability
- Category

## Technologies Used

- Python
- Requests
- BeautifulSoup
- Pandas
- SQLite
- SQL

## Data Cleaning

The following cleaning steps were applied:

1. The currency symbol was removed from the listed book price.
2. price_gbp was converted to a numeric float.
3. Star ratings such as One, Two, Three, Four and Five were converted to integers from 1 to 5.
4. Availability text was converted into a boolean in_stock field.
5. Numeric parsing failures can be handled using median imputation. Unrecoverable critical rows may be dropped when necessary.
6. The final cleaned dataset contains 100 valid rows.

## Currency Conversion

A fixed conversion rate was used:

*1 GBP = 105.50 INR*

The conversion was performed using:

price_inr = price_gbp * 105.50

No live currency API was used.

## Final DataFrame

The final cleaned DataFrame contains 100 rows and 6 columns:

- title
- price_gbp
- price_inr
- rating
- in_stock
- category

## SQLite Database

The cleaned data was stored in a normalized SQLite database.

The database contains two tables:

### categories

- category_id - Primary Key
- category_name - Unique category name

### books

- book_id - Primary Key
- title
- price_gbp
- price_inr
- rating
- in_stock
- category_id - Foreign Key referencing categories

This design separates category information from book records and avoids unnecessary duplication.

## SQL Analysis

The project includes SQL queries demonstrating:

- SELECT
- WHERE
- ORDER BY
- LIMIT
- DISTINCT
- IN
- GROUP BY
- COUNT
- AVG
- JOIN

The database contains 100 book records.

Two SQL query results were also loaded into pandas using pd.read_sql().

## SQL JOIN and Pandas Merge Validation

A SQL JOIN result was reproduced using pandas.merge() on in-memory DataFrames.

The SQL JOIN and pandas merge results were compared and produced an equivalent result.

This validates that the relational JOIN logic can be reproduced correctly using pandas.

## Key Results

- Total books: 100
- Total categories: 29
- Average price: approximately £34.56
- Average price in INR: approximately ₹3,646.15

## Conclusion

The Module 1 data pipeline successfully demonstrates the complete workflow from raw web data to a cleaned dataset, fixed-rate currency conversion, normalized SQLite storage, SQL analysis, and pandas validation.

The pipeline is reproducible and provides a structured foundation for the remaining modules of the Zepto AI Capstone Project.
