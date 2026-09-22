-- PhonePe Pulse Digital Payments Analytics
-- MySQL-compatible analytical queries.

-- 1. Quarterly trend
SELECT year, quarter,
       SUM(transaction_count) AS total_transactions,
       SUM(transaction_amount) AS total_value
FROM aggregated_transactions
GROUP BY year, quarter
ORDER BY year, quarter;

-- 2. Category contribution
SELECT category,
       SUM(transaction_count) AS transactions,
       SUM(transaction_amount) AS value,
       100.0 * SUM(transaction_count) /
       SUM(SUM(transaction_count)) OVER () AS share_pct
FROM aggregated_transactions
GROUP BY category
ORDER BY transactions DESC;

-- 3. Average transaction value
SELECT year, quarter,
       SUM(transaction_amount) / NULLIF(SUM(transaction_count), 0)
       AS average_transaction_value
FROM aggregated_transactions
GROUP BY year, quarter
ORDER BY year, quarter;

-- 4. Top states by transaction volume
SELECT state,
       SUM(transaction_count) AS transactions,
       SUM(transaction_amount) AS value
FROM state_transactions
GROUP BY state
ORDER BY transactions DESC
LIMIT 10;

-- 5. Top states by value
SELECT state,
       SUM(transaction_amount) AS value
FROM state_transactions
GROUP BY state
ORDER BY value DESC
LIMIT 10;

-- 6. QoQ growth using a window function
WITH q AS (
    SELECT year, quarter, SUM(transaction_count) AS transactions
    FROM aggregated_transactions
    GROUP BY year, quarter
)
SELECT year, quarter, transactions,
       LAG(transactions) OVER (ORDER BY year, quarter) AS previous_quarter,
       100.0 * (transactions - LAG(transactions) OVER (ORDER BY year, quarter))
       / NULLIF(LAG(transactions) OVER (ORDER BY year, quarter), 0) AS qoq_growth_pct
FROM q
ORDER BY year, quarter;

-- 7. User trend
SELECT year, quarter, registered_count AS registered_users
FROM users
ORDER BY year, quarter;

-- 8. Merchant trend
SELECT year, quarter, registered_count AS registered_merchants
FROM merchants
ORDER BY year, quarter;
