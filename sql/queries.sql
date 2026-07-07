-- Requêtes analytiques sur la table `orders` chargée par scripts/load_to_postgres.py
-- Colonnes : order_id, customer_id, product_id, product_category, quantity,
--            unit_price, order_date, country, payment_method, total_amount,
--            order_year, order_month

-- 1. Chiffre d'affaires total et nombre de commandes par mois
SELECT
    order_year,
    order_month,
    COUNT(*)            AS nb_orders,
    SUM(total_amount)   AS revenue
FROM orders
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- 2. Top 10 des catégories de produits par chiffre d'affaires
SELECT
    product_category,
    SUM(total_amount) AS revenue,
    COUNT(*)           AS nb_orders
FROM orders
GROUP BY product_category
ORDER BY revenue DESC
LIMIT 10;

-- 3. Chiffre d'affaires mensuel cumulé (running total) par pays, via fonction fenêtre
SELECT
    country,
    order_year,
    order_month,
    SUM(total_amount) AS monthly_revenue,
    SUM(SUM(total_amount)) OVER (
        PARTITION BY country
        ORDER BY order_year, order_month
    ) AS cumulative_revenue
FROM orders
GROUP BY country, order_year, order_month
ORDER BY country, order_year, order_month;

-- 4. Classement des clients par dépense totale (RANK) avec leur nombre de commandes
SELECT
    customer_id,
    COUNT(*)                                                   AS nb_orders,
    SUM(total_amount)                                          AS total_spent,
    RANK() OVER (ORDER BY SUM(total_amount) DESC)              AS spending_rank
FROM orders
GROUP BY customer_id
ORDER BY spending_rank
LIMIT 20;

-- 5. Variation du chiffre d'affaires mensuel par rapport au mois précédent (LAG)
WITH monthly AS (
    SELECT
        order_year,
        order_month,
        SUM(total_amount) AS revenue
    FROM orders
    GROUP BY order_year, order_month
)
SELECT
    order_year,
    order_month,
    revenue,
    LAG(revenue) OVER (ORDER BY order_year, order_month)                          AS previous_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY order_year, order_month)                AS revenue_delta
FROM monthly
ORDER BY order_year, order_month;

-- 6. Panier moyen par méthode de paiement
SELECT
    payment_method,
    ROUND(AVG(total_amount)::numeric, 2) AS avg_order_value,
    COUNT(*)                              AS nb_orders
FROM orders
GROUP BY payment_method
ORDER BY avg_order_value DESC;
