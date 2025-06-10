import libsql_experimental as libsql


class Database():
    def __init__(self):
        self.conn = libsql.connect("imo.db")
        self.init_db()

    def init_db(self):
        self.conn.execute("""
          CREATE TABLE IF NOT EXISTS 
            vectors ( 
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      external_id INTEGER,
                      slug TEXT UNIQUE,
                      embedding F32_BLOB(1024)
                    );
        """)

        self.conn.execute("""
          CREATE INDEX IF NOT EXISTS vector_idx ON vectors (libsql_vector_idx(embedding));
        """)

        print(self.conn.execute("SELECT COUNT(*) FROM vectors;").fetchall())

    def save_vector(self, id, slug, embedding):
        self.conn.execute("""
          INSERT INTO 
            vectors (external_id, slug, embedding)
              VALUES (?, ?, vector32(?))
            ON CONFLICT (slug) DO UPDATE 
              SET embedding = excluded.embedding;
        """, (id, slug, str(embedding)))

        self.conn.commit()

    def search_vector(self, embedding):
        result = self.conn.execute("""
          SELECT vectors.external_id, vectors.slug
          FROM vector_top_k('vector_idx', (?), 5) as vector
          JOIN vectors ON vectors.id = vector.id;
        """, (str(embedding),)).fetchall()

        return [{"id": r[0], "slug": r[1]} for r in result]
