import os
from pathlib import Path
from typing import Literal, Optional
import libsql_experimental as libsql


class Database():
    def __init__(self):
        data_home = Path(os.environ.get('XDG_DATA_HOME', '~/.local/share')).expanduser()
        
        app_data_dir = data_home / 'vectorchat'
        
        app_data_dir.mkdir(parents=True, exist_ok=True)
      
        db_path = app_data_dir / 'imo.db'
        
        self.conn = libsql.connect(str(db_path))
        self.init_db()

    def init_db(self):
        self.conn.execute("""
          CREATE TABLE IF NOT EXISTS
            files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT UNIQUE NOT NULL,
                    file_type TEXT NOT NULL,
                    flag BOOLEAN NOT NULL
                  );
        """)

        self.conn.execute("""
          CREATE TABLE IF NOT EXISTS
            vectors (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      external_id INTEGER NOT NULL,
                      slug TEXT UNIQUE NOT NULL,
                      embedding F32_BLOB(768) NOT NULL,
                      FOREIGN KEY(external_id) REFERENCES files(id)
                    );
        """)

        self.conn.execute("""
          CREATE TABLE IF NOT EXISTS
            history (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      role TEXT NOT NULL,
                      external_id INTEGER,
                      message TEXT NOT NULL,
                      FOREIGN KEY(external_id) REFERENCES files(id)
                    );
        """)

        self.conn.execute("""
          CREATE INDEX IF NOT EXISTS vector_idx ON vectors (libsql_vector_idx(embedding));
        """)

    def save_file(self, file_name: str, file_type: Literal["text", "image"], flag: bool):
        self.conn.execute("""
          INSERT INTO
            files (file_name, file_type, flag)
              VALUES (?, ?, ?)
            ON CONFLICT (file_name) DO UPDATE
              SET flag = excluded.flag;
        """, (file_name, file_type, flag))

        self.conn.commit()

        result = self.conn.execute("""
          SELECT id, file_name, file_type, flag
            FROM files
            WHERE files.file_name = ? LIMIT 1;
        """, (file_name,)).fetchone()

        return {
            "id": result[0],
            "file_name": result[1],
            "file_type": result[2],
            "flag": result[3],
        }

    def update_file(self, file_name: str, flag: bool):
        self.conn.execute("""
          UPDATE files
            SET flag = ?
            WHERE file_name = ?
        """, (flag, file_name))

        self.conn.commit()

    def get_files(self):
        result = self.conn.execute("""
          SELECT id, file_name, file_type, flag
            FROM files;
        """).fetchall()

        return [
            {
                "id": r[0],
                "file_name": r[1],
                "file_type": r[2],
                "flag": r[3],
            } for r in result]

    def get_file_by_id(self, file_id: int):
        result = self.conn.execute("""
          SELECT file_name, file_type
            FROM files
            WHERE id = ? AND flag = 1;
        """, (str(file_id),)).fetchone()

        return {
            "file_name": result[0],
            "file_type": result[1],
        }

    def get_file_by_name(self, file_name: str):
        result = self.conn.execute("""
          SELECT id, file_name, file_type
            FROM files
            WHERE file_name = ? AND flag = 1;
        """, (file_name,)).fetchone()

        return {
            "file_id": result[0],
            "file_name": result[1],
            "file_type": result[2],
        }

    def save_history(self, role: str, message: str, external_id: Optional[int] = None):
        self.conn.execute("""
          INSERT INTO 
            history (role, external_id, message)
              VALUES (?, ?, ?);
        """, (role, external_id, message))

        self.conn.commit()

    def get_history(self):
        result = self.conn.execute("""
          SELECT id, role, external_id, message
            FROM history ORDER BY id;
        """).fetchall()

        return [
            {
                "id": r[0],
                "role": r[1],
                "external_id": r[2],
                "message": r[3],
            } for r in result]

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

    def delete_vector_by_file_name(self, file_name: str):
        result = self.conn.execute("""
          SELECT id
            FROM files
            WHERE file_name = ?;
        """, (file_name,)).fetchone()

        self.conn.execute("""
          DELETE FROM vectors
            WHERE get_file_by_name
        """, (str(result[0]),))

        self.conn.commit()
