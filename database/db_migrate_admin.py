"""
Database Migration Script for Admin Dashboard
Adds admin tables, columns, and default admin user.
Run: venv/Scripts/python.exe database/db_migrate_admin.py
"""

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="job_market_db",
    user="postgres",
    password="shruti65"
)

cur = conn.cursor()

# ==========================================
# 1. Add is_banned, banned_at, ban_reason
#    to applicants table
# ==========================================

cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='applicants'
            AND column_name='is_banned'
        ) THEN
            ALTER TABLE applicants
            ADD COLUMN is_banned BOOLEAN DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='applicants'
            AND column_name='banned_at'
        ) THEN
            ALTER TABLE applicants
            ADD COLUMN banned_at TIMESTAMP;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='applicants'
            AND column_name='ban_reason'
        ) THEN
            ALTER TABLE applicants
            ADD COLUMN ban_reason TEXT;
        END IF;
    END $$;
""")

print("[OK] applicants table updated")

# ==========================================
# 2. Add is_released to jobs table
# ==========================================

cur.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='jobs'
            AND column_name='is_released'
        ) THEN
            ALTER TABLE jobs
            ADD COLUMN is_released BOOLEAN DEFAULT FALSE;
        END IF;
    END $$;
""")

print("[OK] jobs table updated")

# ==========================================
# 3. Create admin_users table
# ==========================================

cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

print("[OK] admin_users table created")

# ==========================================
# 4. Create login_history table
# ==========================================

cur.execute("""
    CREATE TABLE IF NOT EXISTS login_history (
        id SERIAL PRIMARY KEY,
        applicant_id INTEGER,
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(50),
        status VARCHAR(20) DEFAULT 'success'
    );
""")

print("[OK] login_history table created")

# ==========================================
# 5. Create admin_activity_log table
# ==========================================

cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_activity_log (
        id SERIAL PRIMARY KEY,
        admin_username VARCHAR(100),
        action TEXT,
        target_user_id INTEGER,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

print("[OK] admin_activity_log table created")

# ==========================================
# 6. Insert default admin user
# ==========================================

cur.execute("""
    INSERT INTO admin_users (username, password, email)
    VALUES ('shrutijujar321@gmail.com', '$hruti65B', 'shrutijujar321@gmail.com')
    ON CONFLICT (username) DO UPDATE
    SET password = EXCLUDED.password,
        email = EXCLUDED.email;
""")

print("[OK] Admin user created/updated in DB (shrutijujar321@gmail.com)")

# ==========================================
# COMMIT
# ==========================================

conn.commit()

cur.close()
conn.close()

print("\n" + "=" * 50)
print("MIGRATION COMPLETE")
print("=" * 50)
