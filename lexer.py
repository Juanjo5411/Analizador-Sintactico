from tokens import is_reserved_word, is_operator, is_delimiter, DELIMITERS, OPERATORS, RESERVED_WORDS

class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.error_reported = False
        self.error_message = ""
        self.indent_stack = [0]  # Pila para manejar los niveles de indentación

        # Reiniciar el archivo de salida al inicio
        open('output.txt', 'w').close()  # Vacía el archivo al iniciar

    def advance(self):
        """Avanza el puntero de posición y ajusta columna y línea."""
        if self.position < len(self.code):
            if self.code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def peek(self, offset=0):
        """Retorna el carácter en la posición actual + offset sin avanzar."""
        pos = self.position + offset
        if pos < len(self.code):
            return self.code[pos]
        return None

    def tokenize(self):
        """Realiza el análisis léxico del código fuente, soportando unión de líneas con barra invertida."""
        at_line_start = True  # Indica si estamos al inicio de una línea
        while True:
            if self.error_reported:
                break  # Detener si ya se ha reportado un error

            char = self.peek()
            if char is None:
                break  # Fin del archivo

            # Manejar nuevas líneas
            if char == '\n':
                # Verificar si la línea termina con una barra invertida
                if self.position > 0 and self.code[self.position - 1] == '\\':
                    self.advance()  # Saltar el '\n'
                    at_line_start = True
                    continue
                else:
                    self.advance()
                    self.tokens.append(('tk_newline', self.line, self.column))
                    at_line_start = True
                    continue

            # Manejar indentación al inicio de una línea
            if at_line_start:
                self.handle_indentation()
                at_line_start = False
                continue

            # Ignorar espacios en blanco (excepto para la indentación)
            if char == ' ' or char == '\t':
                self.advance()
                continue

            # Procesar comentarios de una línea
            if char == '#':
                self.tokenize_comment()
                continue

            # Detectar comentarios multilínea
            if char in {'"', "'"}:
                if self.peek(1) == char and self.peek(2) == char:
                    self.tokenize_multiline_comment()
                    continue
                else:
                    self.tokenize_string()
                    continue

            # Tokenizar identificadores y palabras reservadas
            if char.isalpha() or char == '_':
                self.tokenize_identifier()
                continue

            # Tokenizar números
            if char.isdigit():
                self.tokenize_number()
                continue

            # Tokenizar operadores
            if is_operator(char):
                self.tokenize_operator()
                continue

            # Tokenizar delimitadores
            if is_delimiter(char):
                self.tokenize_delimiter()
                continue

            # Si no coincide con nada, es un error léxico
            self.report_error()
            break

        # Inserta un tk_newline si el último token no es un tk_newline
        if self.tokens and self.tokens[-1][0] != 'tk_newline':
            self.tokens.append(('tk_newline', self.line, self.column))

        # Manejar dedentaciones al final del archivo
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(('DEDENT', self.line, self.column))

        # Escribir los tokens generados en el archivo de salida
        self.write_output()
        return self.tokens

    def handle_indentation(self):
        """Maneja la sangría con tabulaciones y espacios, generando tokens INDENT y DEDENT con reglas de sangría."""
        current_indent = 0
        pos = self.position
        spaces = 0
        has_tabs = False
        has_spaces = False

        # Procesa la sangría al inicio de cada línea
        while pos < len(self.code) and self.code[pos] in (' ', '\t', '\f'):
            if self.code[pos] == ' ':
                spaces += 1
                has_spaces = True
            elif self.code[pos] == '\t':
                current_indent += (8 - (current_indent % 8))  # Múltiplo de 8
                has_tabs = True
            elif self.code[pos] == '\f':  # Ignora formfeed
                pass
            pos += 1

        # Verificar mezcla de espacios y tabulaciones
        if has_tabs and has_spaces:
            raise TabError(f"Inconsistent use of tabs and spaces for indentation at line {self.line}")

        # Calcular el total de espacios resultantes para la indentación actual
        current_indent += spaces
        self.position = pos
        self.column = current_indent + 1

        # Obtener el nivel de indentación actual y anterior
        previous_indent = self.indent_stack[-1]

        if current_indent > previous_indent:
            # Aumentar la sangría: agregar `INDENT` y actualizar la pila
            self.indent_stack.append(current_indent)
            self.tokens.append(('INDENT', self.line, self.column))

        elif current_indent < previous_indent:
            # Disminuir la sangría: generar `DEDENT` hasta alcanzar el nivel actual
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > current_indent:
                self.indent_stack.pop()
                self.tokens.append(('DEDENT', self.line, self.column))

    def report_error(self, message="Error léxico"):
        """Almacena un mensaje de error léxico sin escribirlo inmediatamente."""
        if not self.error_reported:
            self.error_message = f">>> {message}(linea:{self.line},columna:{self.column})\n"
            print(f"{message} reportado: linea:{self.line}, columna:{self.column}")  # Para depuración
            self.error_reported = True

    def write_output(self):
        """Muestra los tokens y el mensaje de error (si existe) en pantalla y archivo."""
        with open('output.txt', 'a') as output_file:
            for token in self.tokens:
                if isinstance(token, tuple):
                    if len(token) == 4:
                        token_str = f"<{token[0]},{token[1]},{token[2]},{token[3]}>"
                    elif len(token) == 3:
                        token_str = f"<{token[0]},{token[1]},{token[2]}>"
                    output_file.write(token_str + '\n')
                    print(token_str)
            if self.error_message:
                output_file.write(self.error_message)
                print(self.error_message)

    def tokenize_identifier(self):
        """Tokeniza identificadores y palabras reservadas."""
        start_pos = self.position
        start_column = self.column
        while True:
            char = self.peek()
            if char is not None and (char.isalnum() or char == '_'):
                self.advance()
            else:
                break
        identifier = self.code[start_pos:self.position]
        if is_reserved_word(identifier):
            self.tokens.append((identifier, self.line, start_column))
        else:
            self.tokens.append(("id", identifier, self.line, start_column))

    def tokenize_number(self):
        """Tokeniza números enteros y maneja errores léxicos si un número es seguido por caracteres inválidos."""
        start_pos = self.position
        start_column = self.column
        while True:
            char = self.peek()
            if char is not None and char.isdigit():
                self.advance()
            else:
                break
        number = self.code[start_pos:self.position]
        self.tokens.append(("tk_entero", number, self.line, start_column))

        # Después de tokenizar el número, verificar si hay caracteres no válidos
        char = self.peek()
        if char is not None and (char.isalpha() or char == '_'):
            self.report_error()

    def tokenize_operator(self):
        """Tokeniza operadores de uno, dos o tres caracteres."""
        start_column = self.column
        char = self.peek()

        # Verifica si hay uno o dos caracteres después del operador actual
        next_char = self.peek(1)
        next_next_char = self.peek(2)

        # Combinaciones de tres caracteres para operadores triples (e.g. //=, **=, etc.)
        combined_three = char + (next_char or '') + (next_next_char or '')
        if combined_three in OPERATORS:
            token_name = OPERATORS[combined_three]
            self.tokens.append((token_name, self.line, start_column))
            self.advance()
            self.advance()
            self.advance()
            return

        # Combinaciones de dos caracteres para operadores dobles (e.g. +=, ==, etc.)
        combined_two = char + (next_char or '')
        if combined_two in OPERATORS:
            token_name = OPERATORS[combined_two]
            self.tokens.append((token_name, self.line, start_column))
            self.advance()
            self.advance()
            return

        # Operador de un solo carácter
        if char in OPERATORS:
            token_name = OPERATORS[char]
            self.tokens.append((token_name, self.line, start_column))
            self.advance()
        else:
            self.report_error()

    def tokenize_delimiter(self):
        """Tokeniza delimitadores sin manejar el balanceo de símbolos."""
        start_column = self.column
        char = self.peek()
        token_name = DELIMITERS.get(char, None)
        if token_name:
            self.tokens.append((token_name, self.line, start_column))
            self.advance()
        else:
            self.report_error()

    def tokenize_string(self):
        """Tokeniza cadenas de texto."""
        start_line = self.line
        start_column = self.column
        quote_char = self.peek()
        self.advance()
        string_content = ""
        while True:
            current_char = self.peek()
            if current_char is None:
                # Si llegamos al final del archivo sin cerrar la cadena
                self.line = start_line
                self.column = start_column
                self.report_error("Error en cadena de texto")
                return
            if current_char == quote_char:
                self.advance()
                self.tokens.append(("tk_string", string_content, start_line, start_column))
                return
            if current_char == '\n':
                self.advance()
                self.line += 1
                self.column = 1
                string_content += '\n'
            else:
                string_content += current_char
                self.advance()
                self.column += 1

    def tokenize_comment(self):
        """Ignora los comentarios de una línea."""
        while True:
            char = self.peek()
            if char is None or char == '\n':
                break
            self.advance()

    def tokenize_multiline_comment(self):
        """Ignora comentarios multilínea."""
        start_line = self.line
        start_column = self.column
        quote_char = self.peek()
        self.advance()
        self.advance()
        self.advance()
        while True:
            current_char = self.peek()
            if current_char is None:
                self.line = start_line
                self.column = start_column
                self.report_error("Error en comentario multilínea")
                return
            if current_char == quote_char and self.peek(1) == quote_char and self.peek(2) == quote_char:
                self.advance()
                self.advance()
                self.advance()
                return
            else:
                if current_char == '\n':
                    self.advance()
                    self.line += 1
                    self.column = 1
                else:
                    self.advance()
                    self.column += 1
