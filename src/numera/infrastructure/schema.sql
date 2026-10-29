DROP SCHEMA IF EXISTS warehouse CASCADE;
CREATE SCHEMA warehouse;

CREATE TABLE warehouse.legal_entity (
    code text PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE warehouse.account (
    code text PRIMARY KEY,
    name text NOT NULL,
    category text NOT NULL CHECK (category IN ('asset', 'liability', 'equity', 'income', 'expense'))
);

CREATE TABLE warehouse.fiscal_period (
    code text PRIMARY KEY,
    starts_on date NOT NULL,
    ends_on date NOT NULL
);

CREATE TABLE warehouse.journal_line (
    line_id integer PRIMARY KEY,
    entity_code text NOT NULL REFERENCES warehouse.legal_entity (code),
    account_code text NOT NULL REFERENCES warehouse.account (code),
    period_code text NOT NULL REFERENCES warehouse.fiscal_period (code),
    amount numeric(18, 2) NOT NULL,
    memo text NOT NULL
);
