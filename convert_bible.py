import os
import sys
import sqlite3

import text_utils
from models import Row


output_directory: str = "./output"
"""Diretório onde ficarão armazenados os banco de dados resultantes da conversão"""

input_database: sqlite3.Connection
"""Objeto de conexão com o banco de dados de origem"""

output_bible_database: sqlite3.Connection
"""O banco de dados de saída da bíblia"""

output_bible_database_path: str
"""O caminho do banco de dados de saída da bíblia"""

output_commentary_database: sqlite3.Connection
"""O banco de dados de saída dos comentários"""

output_commentary_database_path: str
"""O caminho do banco de dados de saída dos comentários """

pure_bible: list[Row] = []
"""Array com todos os registros da bíblia pura"""

commentaries: list[Row] = []
"""Array com todos os registros dos comentários"""


def print_separator() -> None:
    print("#" * 80)


def connect_to_database(database_path: str) -> sqlite3.Connection:
    """Abre a conexão com o banco de dados (se o banco não existir, o cria)

    Args:
        database_path (string): Caminho do banco de dados

    Returns:
        sqlite3.Connection: O objeto de conexão aberto
    """
    return sqlite3.connect(database_path)


def configure_output_bible_database() -> None:
    """Configura o banco de dados de saída da bíblia"""

    global output_bible_database, output_bible_database_path

    output_bible_database = connect_to_database(output_bible_database_path)

    cursor: sqlite3.Cursor = output_bible_database.cursor()

    # Cria a tabela Bible
    cursor.execute(
        "CREATE TABLE Bible (Book INT, Chapter INT, Verse INT, Scripture BLOB_TEXT)")

    # Cria a tabela Details
    cursor.execute(
        "CREATE TABLE Details(Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL, RightToLeft BOOL)")

    # Cría os índices para os campos Book, Chapter e Verse
    cursor.execute(
        "CREATE INDEX BookChapterVerseIndex ON Bible (Book, Chapter, Verse)")

    # Popula a tabela Details
    configure_output_bible_details()

    cursor.close()


def configure_commentary_database() -> None:
    """Configura o banco de dados de saída dos comentários"""

    global output_commentary_database, output_commentary_database_path

    output_commentary_database = connect_to_database(
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


def configure_output_bible_details() -> None:
    """Configura a tabela Details do banco de dados da bíblia"""

    global input_database, output_bible_database

    sql_get_details = "SELECT * FROM Details LIMIT 1"

    input_cursor: sqlite3.Cursor = input_database.execute(sql_get_details)
    output_cursor: sqlite3.Cursor = output_bible_database.cursor()

    result = input_cursor.fetchone()

    data = dict(zip([column[0].lower()
                     for column in input_cursor.description], result))

    title = data.get("description", data.get("comments", ""))
    abbreviation = data.get("abbreviation", "")
    information = data.get("comments", data.get("description", ""))
    oldtestament = data.get("ot", False)
    newtestament = data.get("nt", False)
    strongs = data.get("strong", False)
    version = 4
    apocrypha = 0
    righttoleft = data.get("righttoleft", False)

    details = {
        'title': title,
        'abbreviation': abbreviation,
        'information': information,
        'version': version,
        'oldtestament': oldtestament,
        'newtestament': newtestament,
        'apocrypha': apocrypha,
        'strongs': strongs,
        'righttoleft': righttoleft
    }

    output_sql = "INSERT INTO Details VALUES (:title, :abbreviation, :information, :version, :oldtestament, :newtestament, :apocrypha, :strongs, :righttoleft)"

    output_cursor.execute(output_sql, details)

    if output_cursor.connection.in_transaction:
        output_cursor.execute("COMMIT")

    input_cursor.close()
    output_cursor.close()


def configure_output_commentary_details() -> None:
    """Configura a tabela Details do banco de dados de comentários"""

    global input_database, output_commentary_database

    sql_get_details: str = "SELECT * FROM Details LIMIT 1"

    input_cursor: sqlite3.Cursor = input_database.execute(sql_get_details)
    output_cursor: sqlite3.Cursor = output_commentary_database.cursor()

    result = input_cursor.fetchone()

    data = dict(zip([column[0].lower()
                for column in input_cursor.description], result))

    title = data.get("description", data.get("comments", ""))
    abbreviation = data.get("abbreviation", "")
    information = data.get("comments", data.get("description", ""))
    version = 4

    details = {
        'title': title,
        'abbreviation': abbreviation,
        'information': information,
        'version': version,
    }

    output_sql = "INSERT INTO Details VALUES (:title, :abbreviation, :information, :version)"

    output_cursor.execute(output_sql, details)

    if output_cursor.connection.in_transaction:
        output_cursor.execute("COMMIT")

    input_cursor.close()
    output_cursor.close()


def create_output_directory() -> None:
    """Cria o diretório de saída para os módulos"""
    global output_directory

    temporary_directory = output_directory
    i = 2

    while os.path.exists(temporary_directory):
        temporary_directory = output_directory + str(i)
        i += 1

    os.makedirs(temporary_directory)
    output_directory = temporary_directory


def is_study_bible(cursor: sqlite3.Cursor) -> bool:
    """Checa se a bíblia é de estudos

    Args:
        cursor (sqlite3.Cursor): O cursor que será usado para a verificação

    Returns:
        bool: Verdadeiro ou falso
    """
    cursor.execute(
        "SELECT True FROM Bible WHERE Scripture LIKE '%<RF%' LIMIT 1")

    return cursor.fetchone() is not None


def process_raw_database() -> None:
    """Faz a conversão pura do banco de dados de origem para o destino"""

    global input_database, output_bible_database

    reading_cursor: sqlite3.Cursor = input_database.cursor()

    reading_cursor.execute(
        "SELECT * FROM Bible ORDER BY Book, Chapter, Verse, Scripture")

    row = reading_cursor.fetchone()

    while row is not None:
        record = Row(*row)

        text = record.scripture

        text = text_utils.convert_tags(text)
        text = text_utils.remove_centralization(text)
        text = text_utils.convert_strong_references(text)
        text = text_utils.remove_empty_tags(text)

        record.scripture = text

        pure_bible.append(record)
        row = reading_cursor.fetchone()


def save_pure_bible() -> None:
    """Salva os versículos na bíblia de saída"""

    writing_cursor: sqlite3.Cursor = output_bible_database.cursor()

    if not writing_cursor.connection.in_transaction:
        writing_cursor.execute("BEGIN")

    for record in pure_bible:
        writing_cursor.execute("INSERT INTO Bible (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)",
                               (record.book, record.chapter, record.verse, record.scripture))

    if writing_cursor.connection.in_transaction:
        writing_cursor.execute("COMMIT")

    writing_cursor.execute("VACUUM")
    writing_cursor.close()


def save_commentaries() -> None:
    """Salva os comentários"""

    writing_cursor: sqlite3.Cursor = output_commentary_database.cursor()

    if not writing_cursor.connection.in_transaction:
        writing_cursor.execute("BEGIN")

    for record in commentaries:
        writing_cursor.execute("""INSERT INTO VerseCommentary (Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd, Comments) VALUES (?, ?, ?, ?, ?, ?)""",
                               (record.book, record.chapter, record.verse, record.chapter, record.verse, record.scripture))

    if writing_cursor.connection.in_transaction:
        writing_cursor.execute("COMMIT")

    writing_cursor.execute("VACUUM")
    writing_cursor.close()


def extract_pure_text(record: Row) -> None:
    """Extrai o texto puro e o adiciona ao array 'pure_text'

    Args:
        record (Record): O registro trazido do banco de origem
    """

    global pure_bible

    text = record.scripture

    text = text_utils.get_pure_text(text)
    text = text_utils.remove_centralization(text)
    text = text_utils.convert_tags(text)
    text = text_utils.convert_strong_references(text)
    text = text_utils.remove_empty_tags(text)

    record.scripture = text
    pure_bible.append(record)


def extract_commentaries(record: Row) -> None:
    """Extrai somente o comentário do versículo

    Args:
        record (Record): O registro trazido do banco de origem
    """
    global commentaries

    text = record.scripture

    if '<RF' not in text:
        return

    text = text_utils.get_commentaries(text)
    text = text_utils.convert_strong_references(text)
    text = text_utils.convert_bible_references(text)

    record.scripture = text

    commentaries.append(record)


def convert_bible() -> None:
    """Gerencia a conversão da bíblia"""
    global input_database_path, input_database, output_bible_database

    with connect_to_database(input_database_path) as input_database:
        cursor: sqlite3.Cursor = input_database.cursor()

        process_commentaries: bool = is_study_bible(cursor)

        cursor.execute(
            "SELECT * FROM Bible ORDER BY Book, Chapter, Verse, Scripture")

        configure_output_bible_database()

        if not process_commentaries:
            """Só irá processar os comentários se for uma bíblia de estudos"""
            print("Não é uma bíblia de estudos - extraindo somente o texto tratado.")
            process_raw_database()
            save_pure_bible()
            return

        configure_commentary_database()
        print_separator()
        print("""
Esta é uma bíblia de estudos.
O aplicativo e-Sword HD não aceita bíblia de estudos, então:
- Os versículos serão tratados e exportados para um arquivo com extensão .bbli (extensão de bíblias no padrão e-Sword HD);
- Os comentários serão tratados e exportados para um arquivo com extensão .cmti (extensão de comentários no padrão e-Sword HD).\n""")
        print_separator()
        print()

        row = cursor.fetchone()
        print("Extraindo versículos e comentários...")

        while row is not None:

            extract_pure_text(Row(*row))
            extract_commentaries(Row(*row))

            row = cursor.fetchone()

        print("Feito!\n")
        save_pure_bible()
        save_commentaries()


if len(sys.argv) < 2:
    print(
        f"Use:\n\tpython {os.path.basename(__file__)} <Caminho da bíblia MyBible>")
    sys.exit(-1)

input_database_path = sys.argv[1]
if not os.path.exists(input_database_path):
    print(f"O arquivo '{input_database_path}' não foi encontrado")
    sys.exit(-1)

create_output_directory()
filename = os.path.splitext(input_database_path)[0].split('.')[0]
if not filename:
    print("O nome do arquivo não possui a extensão .bbl.mybible")
    sys.exit(-1)

output_bible_database_path = os.path.join(output_directory, f"{filename}.bbli")
output_commentary_database_path = os.path.join(
    output_directory, f"{filename}.cmti")

convert_bible()
print(f"Os arquivos convertidos estão na pasta {output_directory}")
