# main.py

from lexer import Lexer
from parser import Parser

def main():
    # Leer archivo de entrada
    input_file = 'codigo_fuente.py'
    with open(input_file, 'r') as file:
        code = file.read()
    
    # Crear el analizador léxico y tokenizar el código
    lexer = Lexer(code)
    lexer.tokenize()  # Los tokens se manejan internamente y se escriben en 'output.txt'

    # Verificar si hubo un error léxico
    if lexer.error_reported:
        print("Se encontró un error léxico. El análisis sintáctico no se realizará.")
        return

    # Crear el parser y realizar el análisis sintáctico
    grammar_file = 'gramatica.txt'  # Asegúrate de que este archivo existe y contiene la gramática
    tokens_file = 'output.txt'      # Archivo generado por el lexer

    parser = Parser(grammar_file, tokens_file)
    parser.parse()

if __name__ == "__main__":
    main()
