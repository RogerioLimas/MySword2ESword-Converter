import re
from constants import ABBREVIATIONS


def convert_tags(text: str) -> str:
    """Converte tags de do padrão específico da MySword para HTML comum.
    Exemplo: <TS>Título<Ts>
    Conversão: <h1>Título</h1>

    Exemplo: <FI>Adição<Fi>
    Conversão: <font color="#gray"><i>Adição</i></font>

    Args:
        text (str): Texto a ser convertido

    Returns:
        str: Texto com as tags convertidas
    """
    converted_text = re.sub(r'<TS>(.*?)<Ts>', r'<h1>\1</h1>', text)
    converted_text = re.sub(r'<TS(\d+)>(.*?)<Ts>',
                            r'<h\1>\2</h\1', converted_text)

    converted_text = converted_text.replace('<CM>', '<p>')
    converted_text = converted_text.replace('<CI>', '<br>')
    converted_text = converted_text.replace('<CL>', '<br>')

    converted_text = re.sub(r'<FI>(.*?)<Fi>',
                            r'<font color="#gray"><i>\1</i></font>', converted_text)
    converted_text = re.sub(r'<FO>(.*?)<Fo>',
                            r'<font color="#gray"><i>\1</i></font>', converted_text)
    converted_text = re.sub(r'<FR>(.*?)<Fr>',
                            r'<font color="#red">\1</font>', converted_text)
    converted_text = re.sub(r'<FU>(.*?)<Fu>', r'<u>\1</u>', converted_text)

    return converted_text


def convert_strong_references(text: str) -> str:
    """Converte as tags de número strong do padrão MySword para o padrão e-Sword HD

    Args:
        text (str): Texto a ser convertido

    Returns:
        str: Texto convertido
    """
    converted_text = re.sub(r'<W([HG]\d+)>', r'<num>\1</num>', text)
    converted_text = re.sub(r'\b([HG]\d+)\b', r'<num>\1</num>', converted_text)
    converted_text = re.sub(r'<WT([^>]*)>', r'<tvm>\1<tvm>', converted_text)

    return converted_text


def remove_centralization(text: str) -> str:
    """Remove tags de centralização de texto

    Args:
        text (str): Texto a ser tratado

    Returns:
        str: Texto tratado
    """
    text = re.sub(r'<p align=.?center.?>', '', text)

    return text


def remove_empty_tags(text: str) -> str:
    """Remove tags vazias no texto

    Args:
        text (str): Texto a ser tratado

    Returns:
        str: Texto tratado
    """

    text = re.sub(r'<h1>(\s+)?</h1>', '', text)
    text = re.sub(r'<sup>(\s+)?</sup>', '', text)

    return text


def get_pure_text(text: str) -> str:
    """Remove o texto que vem antes do início do comentário

    Args:
        text (str): Texto a ser trato

    Returns:
        str: Texto tratado
    """
    text = re.sub(r'<RF.*?<Rf>', '', text)

    return text


def get_commentaries(text: str) -> str:
    """Retorna somente o comentário dentro das tags <RF><Rf>
    E separa cada ocorrência com uma linha <hr> entre parágrafos

    Args:
        text (str): Texto a ser tratado

    Returns:
        str: Comentário puro separado por tags <p><hr><p>
    """
    text = "<p><hr><p>".join(re.findall(r"<RF.*?>(.*?)<Rf>", text))

    text = re.sub(r'class=.bible. ', r'', text)
    text = re.sub(r'(href=.)#(b)', r'\1\2', text)
    text = re.sub(r'<a href=.b([A-Z]\w+|[123][A-ZÀ-Ü]\w+) [\d:-]*.>([A-Z]\w+|[123][A-ZÀ-Ü]\w+)( [\d:\-]*)</a>',
                  r'<ref>\2\3</ref>', text)
    text = re.sub(
        r'<a href=.b[\d.-]*.>([A-ZÀ-Ü]\w+|[123][A-ZÀ-Ü]\w+)( [\d:\-]*)</a>', r'<ref>\1\2</ref>', text)
    text = re.sub(r'<a href=.b[\d.-]*.>([A-ZÀ-Ü]\w+\.|[123][A-ZÀ-Ü]\w+\.)( [\d:\-]*)</a>', r'<ref>\1\2</ref>',
                  text)
    text = re.sub(
        r' ([A-ZÀ-Ü]\w+ [\d:-]+| [123][A-ZÀ-Ü]\w+ [\d:-]+)', r' <ref>\1</ref>', text)

    return text


def convert_bible_references(text: str) -> str:
    """Converte as referências da bíblia MySword para as referências usadas no padrão da e-Sword

    Args:
        text (str): Texto contendo as referências

    Returns:
        str: A referência convertida
    """

    # Expressão regular para extrair as informações da referência
    regex = r"<a href=.b(\d+)\.(\d+)\.(\d+)(?:-(\d+))?.>.*?</a>"

    def replace_references(match):
        book_num = match.group(1)
        chapter_num = match.group(2)
        verse_start = match.group(3)
        verse_end = match.group(4)

        # Converter o número do livro para a sua abreviação correspondente
        book_abbr = ABBREVIATIONS[str(book_num)]

        # Formatar a referência no formato desejado
        if verse_end:
            reference = f'{book_abbr} {chapter_num}.{verse_start}-{verse_end}'
        else:
            reference = f'{book_abbr} {chapter_num}.{verse_start}'

        # Retornar a referência formatada

        return rf'<ref>{reference}</ref>'

    return re.sub(regex, replace_references, text)
