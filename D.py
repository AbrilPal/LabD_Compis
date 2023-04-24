import re

# Definición de tokens
tokens = {
    'WHITESPACE': r'\s+',
    'ID': r'[A-Za-z][A-Za-z0-9]*',
    'NUMBER': r'\d+(\.\d+)?([Ee][+-]?\d+)?',
    'PLUS': r'\+',
    'MINUS': r'-',
    'TIMES': r'\*',
    'DIV': r'/',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
}

def extract_tokens_from_yalex_file(file_path):
    """
    Función que extrae los tokens de una gramática en formato yalex desde un archivo.

    Args:
        file_path (str): Ruta del archivo yalex.

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
        token_rule = token_rule.replace("'", "")
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
                    if token_name:
                        if len(tokens_and_rules) > 1:
                            token_rule = tokens_and_rules[1].split("}")[0].strip()
                        else:
                            raise ValueError("Error: No se pudo obtener la regla de token en la línea: {}".format(line))
                        tokens[token_name] = token_rule

    return tokens

# Ejemplo de uso:
tokens = extract_tokens_from_yalex_file("archivo.yalex")

print(tokens)

# Imprimir los tokens y sus reglas
for token_name, token_rule in tokens.items():
    print("Token: %s : %s" % (token_name, token_rule))

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
                input_str = input_str[len(token_value):]
                break
        if not match:
            raise ValueError("Error: No se pudo analizar el siguiente token en la entrada: {}".format(input_str))
    return tokens_list

# Ejemplo de uso
input_str = "3 i i "
tokens_list = lexer(input_str)
for token_name, token_value in tokens_list:
    if token_name == 'ID':
        print("ID: {}".format(token_value))
    else:
        print("Token: {} : {}".format(token_name, token_value))

