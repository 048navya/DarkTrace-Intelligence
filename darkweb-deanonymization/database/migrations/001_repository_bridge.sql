-- Additive migration. Existing corpus, actors and blockchain records are retained.
CREATE TABLE IF NOT EXISTS wallets (
 wallet_id SERIAL PRIMARY KEY,
 actor_id INTEGER REFERENCES actors(actor_id) ON DELETE SET NULL,
 wallet_address TEXT NOT NULL,
 UNIQUE(actor_id,wallet_address)
);
CREATE TABLE IF NOT EXISTS repository_reviews (
 id SERIAL PRIMARY KEY,
 relationship_id INTEGER REFERENCES persona_relationships(relationship_id) ON DELETE CASCADE,
 decision TEXT NOT NULL CHECK(decision IN ('accepted','rejected','pending')),
 reason TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
