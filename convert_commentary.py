import os
import sys
import sqlite3

from Database import Database

import text_utils
from Utils import Utils
from models import CommentaryRow

output_directory: str = "./output"
"""Diretório onde ficarão armazenados os banco de dados resultantes da conversão"""

input_database: Database
"""O banco de dados de origem dos comentários"""

output_database: Database
"""O banco de dados de saída dos comentários"""

output_database_path: str
"""Caminho do banco de dados de saída"""

commentaries: list[CommentaryRow] = []
"""Array com todos os registros dos comentários"""


def connect_to_databases() -> None:
    """Conecta aos bancos de dados de entrada e saída"""

    global input_database, input_database_path
    global output_database, output_database_path

    input_database = Database(input_database_path)
    input_database.connect()

    output_database = Database(output_database_path)
    output_database.connect()


def configure_output_database() -> None:
    """Configura o banco de dados de saída dos comentários"""

    global input_database, output_database

    output_database.create_commentary_tables()
    output_database.configure_commentary_details(input_database)


def convert_commentary(commentary: str) -> str:
  """Faz a conversão do formato do comentário para o padrão da e-Sword HD

  Args:
      commentary (str): Conteúdo do comentário

  Returns:
      str: Retorna o comentário convertido
  """

  text: str = ""
  
  return text


def convert_commentary() -> None:
    """Gerencia a conversão do comentário"""

    global input_database, output_database

    connect_to_databases()
    configure_output_database()

    cursor: sqlite3.Cursor = input_database.execute(
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
