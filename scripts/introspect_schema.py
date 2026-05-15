import psycopg2
import os

# Credentials provided by user
DB_URL = "postgresql://agent_discovery:agent_discovery_vault_77@db.kxfkfeuhkdopgmkpdimo.supabase.co:5432/postgres?sslmode=require"

def introspect():
    try:
        print(f"Connecting to {DB_URL.split('@')[1]}...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        output = []
        output.append("-- SCHEMA INTROSPECTION DUMP (Enterprise Alignment Check)")
        output.append(f"-- Generated: 2026-05-14")
        output.append("")

        # Get all tables in public schema using pg_class
        cur.execute("SELECT relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relkind = 'r' ORDER BY relname")
        tables = [row[0] for row in cur.fetchall()]
        print(f"Found tables: {tables}")

        for table in tables:
            output.append(f"-- Table: {table}")
            output.append(f"CREATE TABLE public.{table} (")
            
            # Get columns from pg_attribute
            cur.execute(f"""
                SELECT a.attname, format_type(a.atttypid, a.atttypmod), 
                       pg_get_expr(d.adbin, d.adrelid), a.attnotnull
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON a.attrelid = d.adrelid AND a.attnum = d.adnum
                WHERE a.attrelid = 'public.{table}'::regclass
                  AND a.attnum > 0
                  AND NOT a.attisdropped
                ORDER BY a.attnum
            """)
            cols = cur.fetchall()
            col_lines = []
            for col in cols:
                name, dtype, default, notnull = col
                line = f"    {name} {dtype}"
                if default:
                    line += f" DEFAULT {default}"
                if notnull:
                    line += " NOT NULL"
                col_lines.append(line)
            
            # Get Constraints
            cur.execute(f"""
                SELECT conname, pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                JOIN pg_class cl ON cl.oid = c.conrelid
                WHERE n.nspname = 'public' AND cl.relname = '{table}'
            """)
            constraints = cur.fetchall()
            for con in constraints:
                col_lines.append(f"    CONSTRAINT {con[0]} {con[1]}")
                
            output.append(",\n".join(col_lines))
            output.append(");")
            output.append("")

        os.makedirs("supabase/migrations", exist_ok=True)
        with open("supabase/migrations/schema_dump.sql", "w") as f:
            f.write("\n".join(output))
            
        print("Done. Saved to supabase/migrations/schema_dump.sql")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    introspect()
