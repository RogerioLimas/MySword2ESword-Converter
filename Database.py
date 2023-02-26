import sqlite3


class Database:
    """Classe de gerenciamento de banco de dados"""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        """Conecta ao banco de dados e retorna um objeto de conexão

        Returns:
            sqlite3.Connection: Objeto de conexão conectado
        """
        return sqlite3.connect(self.database_path)

    def configure_commentary_database(self, output_commentary_database_path: str) -> None:
      """Configura o banco de dados de saída dos comentários"""

      output_commentary_database = self.connect(
          output_commentary_database_path)

      cursor: sqlite3.Cursor = output_commentary_database.cursor()

      # Cria a tabela de comentários
      cursor.execute(
          "CREATE TABLE VerseCommentary (Book INT, ChapterBegin INT, VerseBegin INT, ChapterEnd INT, VerseEnd INT, Comments TEXT)")

      # Cria a tabela Details
      cursor.execute(
          "CREATE TABLE Details (Title NVARCHAR(255), Abbreviation NVARCHAR(50), Information TEXT, Version INT)")

      # Cría os índices para os campos Book, ChapterBegin e VerseBegin
      cursor.execute(
          "CREATE INDEX BookChapterVerseIndex ON VerseCommentary (Book, ChapterBegin, VerseBegin)")

      # Popula a tabela Details
      configure_output_commentary_details()
