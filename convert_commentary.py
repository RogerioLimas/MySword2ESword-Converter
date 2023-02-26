import os
import sys
import sqlite3

from Database import Database

import text_utils
from Utils import Utils
from models import CommentaryRow

output_directory: str = "./output"
"""Diretório onde ficarão armazenados os banco de dados resultantes da conversão"""

input_database: sqlite3.Connection
"""Objeto de conexão com o banco de dados de origem"""

output_database: sqlite3.Connection
"""O banco de dados de saída dos comentários"""

output_database_path: str
"""O caminho do banco de dados de saída dos comentários """

commentaries: list[CommentaryRow] = []
"""Array com todos os registros dos comentários"""


def connect_to_database(database_path: str) -> sqlite3.Connection:
    """Abre a conexão com o banco de dados (se o banco não existir, o cria)

    Args:
        database_path (string): Caminho do banco de dados

    Returns:
        sqlite3.Connection: O objeto de conexão aberto
    """
    return Database(database_path).connect()


def configure_commentary_details() -> None:
    """Configura a tabela Details do banco de dados de comentários"""

    global input_database, output_database

    sql_get_details: str = "SELECT * FROM Details LIMIT 1"

    input_cursor: sqlite3.Cursor = input_database.execute(sql_get_details)
    output_cursor: sqlite3.Cursor = output_database.cursor()

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


def configure_commentary_database() -> None:
    """Configura o banco de dados de saída dos comentários"""

    global output_database, output_database_path

    output_database = connect_to_database(
        output_database_path)

    with output_database:
      cursor: sqlite3.Cursor = output_database.cursor()

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

    # Popula a tabela Details
    configure_commentary_details()


def convert_commentary() -> None:
    """Gerencia a conversão do comentário"""

    global input_database, input_database_path
    global output_database, output_database_path

    output_database = connect_to_database(output_database_path)

    input_database = connect_to_database(input_database_path)
    with input_database:
        configure_commentary_database()

        cursor: sqlite3.Cursor = input_database.cursor()

        cursor.execute(
            "SELECT * FROM Commentary ORDER BY id ASC LIMIT 10")
        
        row: CommentaryRow = CommentaryRow(*cursor.fetchone())


if len(sys.argv) < 2:
    print(
        f"Use:\n\tpython {os.path.basename(__file__)} <Caminho do comentário MyBible>")
    sys.exit(-1)

input_database_path = sys.argv[1]
if not os.path.exists(input_database_path):
    print(f"O arquivo '{input_database_path}' não foi encontrado")
    sys.exit(-1)

output_directory = Utils.create_output_directory()

filename = os.path.splitext(input_database_path)[0].split('.')[0]
if not filename:
    print("O nome do arquivo não possui a extensão .bbl.mybible")
    sys.exit(-1)

output_database_path = os.path.join(
    output_directory, f"{filename}.cmti")

convert_commentary()
# print(f"Os arquivos convertidos estão na pasta {output_directory}")
