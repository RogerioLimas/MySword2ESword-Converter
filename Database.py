import sqlite3


class Database:
    """Classe de gerenciamento de banco de dados"""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def connect(self) -> None:
        """Conecta ao banco de dados"""

        self.connection: sqlite3.Connection = sqlite3.connect(self.database_path)
    

    def execute(self, sql: str) -> sqlite3.Cursor:
      """Executa uma instrução no banco de dados e retorna o cursor com o resultado

      Args:
          sql (str): Instrução SQL a ser executada

      Returns:
          sqlite3.Cursor: Retorna o cursor com o resultado da execução
      """

      return self.connection.execute(sql)

    def create_commentary_tables(self) -> None:
      """Configura o banco de dados de saída dos comentários"""

      cursor: sqlite3.Cursor = self.connection.cursor()

      cursor.executescript("""
      --Criação das tabelas
      CREATE TABLE BookCommentary (Book	INT, Comments	TEXT);
      CREATE TABLE ChapterCommentary (Book INT, Chapter INT, Comments TEXT);
      CREATE TABLE VerseCommentary (Book INT, ChapterBegin INT, VerseBegin INT, ChapterEnd INT, VerseEnd INT, Comments TEXT);
      CREATE TABLE data(rowid INTEGER primary key autoincrement, id TEXT collate nocase, filename TEXT, content BLOB);
      CREATE TABLE Details (Title NVARCHAR(255), Abbreviation NVARCHAR(50), Information TEXT, Version INT, customcss TEXT);

      --Criação dos índices
      CREATE INDEX BookChapterIndex ON ChapterCommentary (Book, Chapter);
      CREATE INDEX BookChapterVerseIndex ON VerseCommentary (Book, ChapterBegin, VerseBegin);
      CREATE INDEX BookIndex ON BookCommentary (Book);
      CREATE UNIQUE INDEX idx_data_id on data(id);
      """)

      cursor.close()


    def configure_commentary_details(self, input_database: 'Database') -> None:
      """Configura o banco de dados de saída dos comentários"""

      sql_get_details: str = "SELECT * FROM Details LIMIT 1"

      input_cursor: sqlite3.Cursor = input_database.execute(sql_get_details)
      output_cursor: sqlite3.Cursor = self.connection.cursor()

      result = input_cursor.fetchone()

      data = dict(zip([column[0].lower()
                  for column in input_cursor.description], result))

      title = data.get("title", data.get("abbreviation", ""))
      abbreviation = data.get("abbreviation", "")

      description = data.get("description", "")
      comments = data.get("comments", "")
      information = "\n<hr />\n".join(filter(None, [description, comments]))
      
      version = 4

      details = {
          'title': title,
          'abbreviation': abbreviation,
          'information': information,
          'version': version,
          'customcss': ''
      }

      output_sql = "INSERT INTO Details VALUES (:title, :abbreviation, :information, :version, :customcss)"

      output_cursor.execute(output_sql, details)

      if output_cursor.connection.in_transaction:
          output_cursor.execute("COMMIT")

      input_cursor.close()
      output_cursor.close()
