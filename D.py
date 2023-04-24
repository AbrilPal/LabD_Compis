import re

# Definición de tokens
tokens_d = {
    'WHITESPACE': r'\s+',
    'ID': r'[A-Za-z][A-Za-z0-9]*',
    'NUMBER': r'\d+(\.\d+)?([Ee][+-]?\d+)?',
    'PLUS': r'\+',
    'MINUS': r'-',
    'TIMES': r'\*',
    'DIV': r'/',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'ASSIGNOP': r':=',
    'EQUALS': r'=',
    'SEMICOLON': r';',
    'LT': r'<',
    'GT': r'>',
}

def merge_tokens(tokens, additional_tokens):
    """
    Función que combina dos diccionarios de tokens y elimina los tokens repetidos según su token_rule y token_name.

    Args:
        tokens (dict): Diccionario original de tokens.
        additional_tokens (dict): Diccionario de tokens adicionales a agregar.

    Returns:
        dict: Diccionario combinado de tokens sin tokens repetidos según su token_rule y token_name.
    """
    merged_tokens = tokens.copy()
    for token_name, token_rule in additional_tokens.items():
        if token_name not in merged_tokens.keys() and token_rule not in merged_tokens.values():
            merged_tokens[token_name] = token_rule
    return merged_tokens

def filter_tokens(tokens, tokens_d):
    """
    Función que filtra los tokens de un diccionario de tokens generados por la función
    extract_tokens_from_yalex_file, 
    Args:
        tokens (dict): Diccionario con los tokens y sus reglas.
        tokens_d (dict): Diccionario con los nombres de los tokens permitidos y sus reglas.
    Returns:
        dict: Diccionario con los tokens procesados.
    """
    filtered_tokens = {}
    for token_name, token_rule in tokens.items():
        if token_name == "id" and "ID" in tokens_d:
            filtered_tokens["ID"] = tokens_d["ID"]
        elif token_name == "number" and "NUMBER" in tokens_d:
            filtered_tokens["NUMBER"] = tokens_d["NUMBER"]
        elif token_name == "ws":
            filtered_tokens["WHITESPACE"] = tokens_d["WHITESPACE"]
        elif token_name in tokens_d and token_rule == tokens_d[token_name]:
            filtered_tokens[token_name] = token_rule
    return filtered_tokens


def extract_tokens_from_yalex_file(file_path, tokens_d):
    """
    Función que extrae los tokens de una gramática en formato yalex desde un archivo,
    y reemplaza los tokens que contienen "return" por los tokens correspondientes en el diccionario.
    Args:
        file_path (str): Ruta del archivo yalex.
        tokens_d (dict): Diccionario con los tokens y sus reglas a reemplazar.
    Returns:
        dict: Diccionario con los tokens y sus reglas.
    """
    tokens = {}

    with open(file_path, 'r') as file:
        contenido = file.read()

    contenido_sin_comentarios = re.sub(r'\(\*.*?\*\)', '', contenido, flags=re.DOTALL)

    with open(file_path, 'w') as file:
        file.write(contenido_sin_comentarios)

    with open(file_path, 'r') as file:
        yalex_text = file.read()

    tokens_def = re.findall(r"let\s+(\w+)\s+=\s+(.+)", yalex_text)

    for token_name, token_rule in tokens_def:
        if "return" in token_rule:
            token_rule = token_rule.replace("'", "").replace("return", "").strip()
            if token_rule in tokens_d:
                tokens[token_name] = tokens_d[token_rule]
                tokens[token_rule] = tokens_d[token_rule] # Agrega el reemplazo del nombre del token
            else:
                if token_name in tokens_d:
                    tokens[token_name] = tokens_d[token_name]
                else:
                    tokens[token_name] = token_rule
        else:
            token_rule = token_rule.replace("'", "")
            if token_rule in tokens_d:
                tokens[token_name] = tokens_d[token_rule]
                tokens[token_rule] = tokens_d[token_rule] # Agrega el reemplazo del nombre del token
            else:
                if token_name in tokens_d:
                    tokens[token_name] = tokens_d[token_name]
                else:
                    tokens[token_name] = token_rule

    rules = re.findall(r"rule\s+tokens\s+=\s+([\s\S]+?)(?=\nrule|\Z)", yalex_text)

    for rule in rules:
        rule_lines = rule.split("\n")
        for line in rule_lines:
            line = line.strip()
            if line:
                tokens_and_rules = line.split("{")
                token_names = tokens_and_rules[0].split("|")
                for token_name in token_names:
                    token_name = token_name.strip()
                    if token_name and token_name not in tokens.keys():
                        if len(tokens_and_rules) > 1:
                            token_rule = tokens_and_rules[1].split("}")[0].strip()
                            if "return" in token_rule:
                                token_rule = token_rule.replace("'", "").replace("return", "").strip()
                                if token_rule in tokens_d:
                                    tokens[token_name] = tokens_d[token_rule]
                                    tokens[token_rule] = tokens_d[token_rule] # Agrega el reemplazo del nombre del token
                                else:
                                    if token_name in tokens_d:
                                        tokens[token_name] = tokens_d[token_name]
                                    else:
                                        tokens[token_name] = token_rule
                            else:
                                if token_rule in tokens_d:
                                    tokens[token_name] = tokens_d[token_rule]
                                    tokens[token_rule] = tokens_d[token_rule] # Agrega el reemplazo del nombre del token

    return tokens

tokens = extract_tokens_from_yalex_file("archivo.yalex", tokens_d)
tokens = filter_tokens(tokens, tokens_d)

# print(tokens)
print("    TOKENS YALEX")
print()

# Imprimir los tokens y sus reglas
for token_name, token_rule in tokens.items():
    print("Token: %s " % (token_name))

print()

print("    ANALIZANDO ")
def lexer(input_str):
    tokens_list = []
    while input_str:
        match = None
        for token_name, token_rule in tokens.items():
            regex = re.compile(r'^' + token_rule)
            match = regex.search(input_str)
            if match:
                token_value = match.group(0)
                if token_name != 'WHITESPACE':
                    tokens_list.append((token_name, token_value))
                else:
                    pass
                input_str = input_str[len(token_value):]
                break
        if not match:
            raise ValueError("Error: No se pudo analizar el siguiente token en la entrada: {}".format(input_str))
    return tokens_list

file_path = 'entrada.txt'
with open(file_path, 'r') as file:
    input_str = file.read()

tokens_list = lexer(input_str)
# input_str = "val7 i i * ( +) "
tokens_list = lexer(input_str)
for token_name, token_value in tokens_list:
    if token_name == 'ID':
        print("ID: {}".format(token_value))
    else:
        print("{} : {}".format(token_name, token_value))

