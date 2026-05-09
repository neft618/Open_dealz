-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. All ENUMs (add 'shared' to initiated_by enum)
CREATE TYPE user_role AS ENUM ('customer', 'executor', 'admin');
CREATE TYPE specialization AS ENUM ('web_development', 'mobile_development', 'data_science', 'design', 'marketing', 'other');
CREATE TYPE order_status AS ENUM ('open', 'in_progress', 'closed', 'cancelled');
CREATE TYPE application_status AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE contract_status AS ENUM ('draft', 'signed', 'in_progress', 'completed', 'disputed', 'cancelled');
CREATE TYPE payment_type AS ENUM ('fixed', 'hourly', 'milestone');
CREATE TYPE clause_type AS ENUM ('subject_description', 'timeline', 'payment_terms', 'termination_conditions', 'result_review_period', 'refund_policy', 'platform_commission', 'ip_rights', 'confidentiality');
CREATE TYPE milestone_status AS ENUM ('pending', 'in_progress', 'approved', 'rejected');
CREATE TYPE escrow_transaction_type AS ENUM ('lock', 'release', 'refund', 'fee');
CREATE TYPE escrow_transaction_status AS ENUM ('pending', 'confirmed', 'failed');
CREATE TYPE initiated_by AS ENUM ('customer', 'executor', 'system', 'shared');
CREATE TYPE dispute_status AS ENUM ('open', 'under_review', 'resolved');
CREATE TYPE dispute_resolution AS ENUM ('executor', 'customer', 'shared');
CREATE TYPE notification_type AS ENUM ('contract', 'payment', 'dispute', 'system');

-- 3. users (add wallet_address VARCHAR(42))
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    role user_role DEFAULT 'customer',
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    wallet_address VARCHAR(42)
);

-- 4. profiles (remove contracts_count, remove rating)
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    skills TEXT,
    specialization specialization
);

-- 5. profile_skills (id, profile_id FK, skill VARCHAR NOT NULL)
CREATE TABLE profile_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    skill VARCHAR NOT NULL
);

-- 6. portfolios (with ON DELETE CASCADE)
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    description TEXT,
    file_url VARCHAR NOT NULL
);

-- 7. orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    status order_status DEFAULT 'open',
    budget NUMERIC(12, 2) NOT NULL,
    deadline DATE NOT NULL,
    customer_id UUID REFERENCES users(id),
    executor_id UUID REFERENCES users(id)
);

-- 8. applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    executor_id UUID REFERENCES users(id),
    cover_letter TEXT NOT NULL,
    proposed_price NUMERIC(12, 2) NOT NULL,
    status application_status DEFAULT 'pending',
    CHECK (proposed_price > 0)
);

-- 9. contracts
CREATE TABLE contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    order_id UUID UNIQUE REFERENCES orders(id),
    customer_id UUID REFERENCES users(id),
    executor_id UUID REFERENCES users(id),
    status contract_status DEFAULT 'draft',
    total_amount NUMERIC(12, 2) NOT NULL,
    platform_fee NUMERIC(12, 2) DEFAULT 0,
    payment_type payment_type NOT NULL,
    signed_at TIMESTAMP WITH TIME ZONE,
    customer_signed_at TIMESTAMP WITH TIME ZONE,
    executor_signed_at TIMESTAMP WITH TIME ZONE
);

-- 10. contract_clauses (with ON DELETE CASCADE)
CREATE TABLE contract_clauses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    clause_type clause_type NOT NULL,
    content TEXT NOT NULL,
    position INTEGER NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE
);

-- 11. milestones (with ON DELETE CASCADE)
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    title VARCHAR NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    deadline DATE NOT NULL,
    status milestone_status DEFAULT 'pending',
    position INTEGER NOT NULL
);

-- 12. deliverables (with ON DELETE CASCADE)
CREATE TABLE deliverables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    milestone_id UUID REFERENCES milestones(id),
    file_url VARCHAR NOT NULL,
    file_name VARCHAR NOT NULL,
    file_size INTEGER NOT NULL,
    description TEXT NOT NULL,
    submitted_by_id UUID REFERENCES users(id),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. escrow_transactions (with ON DELETE CASCADE)
CREATE TABLE escrow_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    type escrow_transaction_type NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    status escrow_transaction_status DEFAULT 'pending',
    initiated_by initiated_by NOT NULL,
    tx_hash VARCHAR UNIQUE NOT NULL,
    metadata_ JSONB
);

-- 14. disputes (remove UNIQUE on contract_id)
CREATE TABLE disputes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id),
    initiated_by_id UUID REFERENCES users(id),
    status dispute_status DEFAULT 'open',
    resolution dispute_resolution,
    resolution_comment TEXT,
    resolved_by_id UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- 15. dispute_messages (with ON DELETE CASCADE)
CREATE TABLE dispute_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    dispute_id UUID REFERENCES disputes(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    file_url VARCHAR
);

-- 16. reviews (NEW: id, contract_id FK, author_id FK, recipient_id FK, rating SMALLINT CHECK 1-5, comment TEXT, created_at; UNIQUE(contract_id, author_id))
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    recipient_id UUID REFERENCES users(id),
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    UNIQUE (contract_id, author_id)
);

-- 17. notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    type notification_type NOT NULL,
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    related_entity_type VARCHAR,
    related_entity_id UUID
);

-- 18. audit_log (NEW: id UUID PK, created_at TIMESTAMPTZ, entity_type VARCHAR NOT NULL, entity_id UUID NOT NULL, action VARCHAR NOT NULL, user_id UUID REFERENCES users(id) ON DELETE SET NULL, payload JSONB, tx_hash VARCHAR(64) UNIQUE NOT NULL)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    entity_type VARCHAR NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    payload JSONB,
    tx_hash VARCHAR(64) UNIQUE NOT NULL
);

-- 19. All indexes (FK indexes + query indexes listed above)
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_portfolios_profile_id ON portfolios(profile_id);
CREATE INDEX idx_profile_skills_profile_id ON profile_skills(profile_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_executor_id ON orders(executor_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_applications_order_id ON applications(order_id);
CREATE INDEX idx_applications_executor_id ON applications(executor_id);
CREATE INDEX idx_contracts_order_id ON contracts(order_id);
CREATE INDEX idx_contracts_customer_id ON contracts(customer_id);
CREATE INDEX idx_contracts_executor_id ON contracts(executor_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contract_clauses_contract_id ON contract_clauses(contract_id);
CREATE INDEX idx_milestones_contract_id ON milestones(contract_id);
CREATE INDEX idx_deliverables_contract_id ON deliverables(contract_id);
CREATE INDEX idx_deliverables_milestone_id ON deliverables(milestone_id);
CREATE INDEX idx_deliverables_submitted_by_id ON deliverables(submitted_by_id);
CREATE INDEX idx_escrow_transactions_contract_id ON escrow_transactions(contract_id);
CREATE INDEX idx_escrow_transactions_tx_hash ON escrow_transactions(tx_hash);
CREATE INDEX idx_disputes_contract_id ON disputes(contract_id);
CREATE INDEX idx_disputes_initiated_by_id ON disputes(initiated_by_id);
CREATE INDEX idx_disputes_resolved_by_id ON disputes(resolved_by_id);
CREATE INDEX idx_disputes_status ON disputes(status);
CREATE INDEX idx_dispute_messages_dispute_id ON dispute_messages(dispute_id);
CREATE INDEX idx_dispute_messages_author_id ON dispute_messages(author_id);
CREATE INDEX idx_reviews_contract_id ON reviews(contract_id);
CREATE INDEX idx_reviews_author_id ON reviews(author_id);
CREATE INDEX idx_reviews_recipient_id ON reviews(recipient_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read_user_id ON notifications(is_read, user_id);
CREATE INDEX idx_audit_log_entity_type_entity_id ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_tx_hash ON audit_log(tx_hash);

-- 20. updated_at trigger function + apply to all tables that have updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profile_skills_updated_at BEFORE UPDATE ON profile_skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contract_clauses_updated_at BEFORE UPDATE ON contract_clauses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_milestones_updated_at BEFORE UPDATE ON milestones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deliverables_updated_at BEFORE UPDATE ON deliverables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_escrow_transactions_updated_at BEFORE UPDATE ON escrow_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_disputes_updated_at BEFORE UPDATE ON disputes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dispute_messages_updated_at BEFORE UPDATE ON dispute_messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON notifications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();