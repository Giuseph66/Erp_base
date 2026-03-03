-- Seed initial admin user (password: admin123 - hash for demo purposes)
-- In production, use proper password hashing
INSERT INTO users (email, password_hash, name, role)
VALUES (
    'admin@neo.local',
    '$2b$10$example.hash.replace.in.production',
    'Administrator',
    'admin'
)
ON CONFLICT (email) DO NOTHING;

-- Seed sample users
INSERT INTO users (email, password_hash, name, role)
VALUES 
    ('user1@neo.local', '$2b$10$example.hash.replace.in.production', 'Test User 1', 'user'),
    ('user2@neo.local', '$2b$10$example.hash.replace.in.production', 'Test User 2', 'user')
ON CONFLICT (email) DO NOTHING;
