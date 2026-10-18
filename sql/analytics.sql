-- Monthly revenue
SELECT order_month, SUM(revenue) AS total_revenue, COUNT(*) AS orders
FROM fact_sales
GROUP BY order_month
ORDER BY order_month;

-- Top 5 cities by revenue
SELECT city, SUM(revenue) AS total_revenue
FROM fact_sales
GROUP BY city
ORDER BY total_revenue DESC
LIMIT 5;

-- Best-selling products by units
SELECT product, SUM(quantity) AS units_sold, SUM(revenue) AS total_revenue
FROM fact_sales
GROUP BY product
ORDER BY units_sold DESC;

-- Top 10 customers by lifetime spend
SELECT customer_id, COUNT(*) AS orders, SUM(revenue) AS lifetime_value
FROM fact_sales
GROUP BY customer_id
ORDER BY lifetime_value DESC
LIMIT 10;
