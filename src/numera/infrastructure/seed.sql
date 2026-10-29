-- West March revenue is 1500.00 + 250.50 = 1750.50.
INSERT INTO warehouse.legal_entity (code, name) VALUES
    ('NORTH', 'North desk'),
    ('WEST', 'West desk');

INSERT INTO warehouse.account (code, name, category) VALUES
    ('1000', 'Cash', 'asset'),
    ('2100', 'Accrual', 'liability'),
    ('4000', 'Revenue', 'income'),
    ('6100', 'Payroll', 'expense');

INSERT INTO warehouse.fiscal_period (code, starts_on, ends_on) VALUES
    ('2026-02', DATE '2026-02-01', DATE '2026-02-28'),
    ('2026-03', DATE '2026-03-01', DATE '2026-03-31');

INSERT INTO warehouse.journal_line (line_id, entity_code, account_code, period_code, amount, memo) VALUES
    (1, 'WEST', '4000', '2026-03', 1500.00, 'March revenue'),
    (2, 'WEST', '4000', '2026-03', 250.50, 'March revenue adjustment'),
    (3, 'NORTH', '4000', '2026-03', 800.00, 'March revenue'),
    (4, 'WEST', '6100', '2026-03', -320.00, 'March payroll'),
    (5, 'NORTH', '2100', '2026-03', -100.00, 'March accrual'),
    (6, 'WEST', '1000', '2026-02', 50.00, 'February cash'),
    (7, 'NORTH', '4000', '2026-02', 0.00, 'February revenue tie-out');
