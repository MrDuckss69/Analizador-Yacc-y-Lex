from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definir los tokens para el lexer
tokens = ['RESERVED', 'FREE']

# Lista de palabras reservadas
reserved = {
    'for': 'RESERVED',
    'while': 'RESERVED',
    'if': 'RESERVED',
    'else': 'RESERVED',
}

# Expresión regular para identificar identificadores (variables, nombres, etc.)
def t_FREE(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'RESERVED' if t.value in reserved else 'FREE')
    return t

# Ignorar espacios y tabs
t_ignore = ' \t'

# Manejar saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Definir el manejador de errores
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Crear el lexer
lexer = lex.lex()

# Reglas gramaticales para el análisis sintáctico
def p_statement_reserved(p):
    '''statement : RESERVED'''
    p[0] = ('reserved', p[1])

def p_statement_free(p):
    '''statement : FREE'''
    p[0] = ('free', p[1])

def p_error(p):
    print("Error sintáctico en '%s'" % p.value)

# Crear el parser
parser = yacc.yacc()

# Función para analizar el texto léxicamente
def lexico(text):
    lexer.input(text)
    
    tokens_list = []
    line_info = []

    for token in lexer:
        tokens_list.append((token.lineno, token.type, token.value))  # Guardar línea, tipo y valor del token
        tipo_palabra = 'Palabra Reservada' if token.type == 'RESERVED' else 'Palabra Libre'
        line_info.append((token.lineno, tipo_palabra, token.value))  # Guardar número de línea, tipo y valor

    return tokens_list, line_info

# Función para el análisis sintáctico usando yacc
def sintactico(tokens_list):
    sintactico_info = []

    for token in tokens_list:
        line_number, token_type, token_value = token
        result = parser.parse(token_value)
        if result:
            token_type, token_value = result
            if token_type == 'reserved':
                sintactico_info.append((line_number, token_value, 'Correcta', ''))  # Correcto
            else:
                sintactico_info.append((line_number, token_value, '', 'Identificador'))  # Incorrecto
        else:
            sintactico_info.append((line_number, token_value, '', 'X'))  # Incorrecto o vacío

    return sintactico_info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        tokens, line_info = lexico(text)
        sintactico_info = sintactico(tokens)
        return render_template('index.html', tokens=tokens, line_info=line_info, sintactico_info=sintactico_info)
    
    return render_template('index.html', tokens=None, line_info=None, sintactico_info=None)

if __name__ == '__main__':
    app.run(debug=True)