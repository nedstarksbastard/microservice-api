CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY,
  user_id TEXT NOT NULL,
  customer_fullname TEXT NOT NULL,
  product_code TEXT NOT NULL,
  product_name TEXT NOT NULL,
  total_amount FLOAT NOT NULL,
  created_at TEXT NOT NULL
);
