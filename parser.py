# parser.py

import sys

class Grammar:
    def __init__(self, grammar_file):
        self.rules = {}
        self.terminals = set()
        self.non_terminals = []
        self.first_sets = {}
        self.follow_sets = {}
        self.prediction_sets = {}
        self.parse_table = {}
        self.start_symbol = None
        self.read_grammar(grammar_file)
        self.compute_first_sets()
        self.compute_follow_sets()
        self.compute_prediction_sets()
        self.build_parse_table()

    def read_grammar(self, filename):
        """Lee la gramática desde un archivo y la almacena en estructuras de datos."""
        try:
            with open(filename, 'r') as f:
                current_lhs = None
                current_rhs = []
                accumulating = False

                for line in f:
                    # Eliminar espacios en blanco y comentarios
                    line = line.split('#', 1)[0].strip()
                    
                    if not line:
                        continue  # Ignorar líneas vacías
                    
                    # Detectar si se inicia una nueva regla
                    if '->' in line:
                        # Si se está acumulando una producción previa, guardarla
                        if accumulating and current_lhs:
                            if current_lhs not in self.rules:
                                self.rules[current_lhs] = []
                            # Filtrar producciones vacías
                            self.rules[current_lhs].extend([prod for prod in current_rhs if prod])
                            current_rhs = []
                            accumulating = False

                        # Dividir la línea en LHS y RHS usando split con máximo una división
                        lhs, rhs = line.split('->', 1)
                        lhs = lhs.strip()
                        rhs = rhs.strip()
                        
                        # Agregar LHS al conjunto de no terminales y actualizar el símbolo inicial
                        if lhs not in self.non_terminals:
                            self.non_terminals.append(lhs)
                        if self.start_symbol is None:
                            self.start_symbol = lhs
                        current_lhs = lhs  # Actualizar LHS en curso

                        # Agregar producciones al RHS inicial
                        current_rhs.extend([prod.strip().split() for prod in rhs.split('|')])
                        accumulating = True

                    else:
                        # Continuar acumulando el RHS de la producción anterior
                        if accumulating:
                            current_rhs.extend([prod.strip().split() for prod in line.split('|')])

                # Guardar la última regla acumulada al finalizar el archivo
                if accumulating and current_lhs:
                    if current_lhs not in self.rules:
                        self.rules[current_lhs] = []
                    # Filtrar producciones vacías
                    self.rules[current_lhs].extend([prod for prod in current_rhs if prod])
                
                # Identificar terminales y no terminales
                for lhs, productions in self.rules.items():
                    for prod in productions:
                        for symbol in prod:
                            if symbol.isupper():
                                continue  # Es un no terminal
                            elif symbol == 'ε':
                                continue  # Epsilon
                            else:
                                self.terminals.add(symbol)
                
                self.terminals.add('$')  # Añadir el símbolo de fin de entrada

        except FileNotFoundError:
            print(f"Error: El archivo de gramática '{filename}' no se encontró.")
            sys.exit(1)




    def compute_first_sets(self):
        """Calcula los conjuntos PRIMERO para cada no terminal."""
        for nt in self.non_terminals:
            self.first_sets[nt] = set()
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.rules[nt]:
                    before = len(self.first_sets[nt])
                    if production[0] == 'ε':
                        self.first_sets[nt].add('ε')
                    else:
                        for symbol in production:
                            if symbol in self.terminals:
                                self.first_sets[nt].add(symbol)
                                break
                            elif symbol in self.non_terminals:
                                self.first_sets[nt].update(self.first_sets[symbol] - {'ε'})
                                if 'ε' not in self.first_sets[symbol]:
                                    break
                            else:
                                self.first_sets[nt].add(symbol)
                                break
                        else:
                            self.first_sets[nt].add('ε')
                    after = len(self.first_sets[nt])
                    if after > before:
                        changed = True

    def compute_follow_sets(self):
        """Calcula los conjuntos SIGUIENTE para cada no terminal."""
        for nt in self.non_terminals:
            self.follow_sets[nt] = set()
        self.follow_sets[self.start_symbol].add('$')
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.rules[nt]:
                    trailer = self.follow_sets[nt].copy()
                    for symbol in reversed(production):
                        if symbol in self.non_terminals:
                            before = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(trailer)
                            if 'ε' in self.first_sets[symbol]:
                                trailer.update(self.first_sets[symbol] - {'ε'})
                            else:
                                trailer = self.first_sets[symbol]
                            after = len(self.follow_sets[symbol])
                            if after > before:
                                changed = True
                        elif symbol in self.terminals:
                            trailer = {symbol}
                        else:
                            trailer = set()

    def compute_prediction_sets(self):
        """Calcula los conjuntos de PREDICCIÓN para cada producción."""
        for nt in self.non_terminals:
            self.prediction_sets[nt] = []
            for production in self.rules[nt]:
                prediction_set = set()
                if production[0] == 'ε':
                    prediction_set.update(self.follow_sets[nt])
                else:
                    for symbol in production:
                        if symbol in self.terminals:
                            prediction_set.add(symbol)
                            break
                        elif symbol in self.non_terminals:
                            prediction_set.update(self.first_sets[symbol] - {'ε'})
                            if 'ε' not in self.first_sets[symbol]:
                                break
                        else:
                            prediction_set.add(symbol)
                            break
                    else:
                        prediction_set.update(self.follow_sets[nt])
                self.prediction_sets[nt].append((production, prediction_set))

    def build_parse_table(self):
        """Construye la tabla de análisis sintáctico LL(1)."""
        for nt in self.non_terminals:
            for idx, (production, prediction_set) in enumerate(self.prediction_sets[nt]):
                for terminal in prediction_set:
                    key = (nt, terminal)
                    if key in self.parse_table:
                        print(f"Error: Gramática no es LL(1), conflicto en M[{nt}, {terminal}]")
                        sys.exit(1)
                    self.parse_table[key] = production

    def print_sets(self):
        """Imprime los conjuntos PRIMERO y SIGUIENTE (opcional)."""
        print("Conjuntos PRIMERO:")
        for nt, first in self.first_sets.items():
            print(f"PRIM({nt}) = {{ {', '.join(first)} }}")
        print("\nConjuntos SIGUIENTE:")
        for nt, follow in self.follow_sets.items():
            print(f"SIG({nt}) = {{ {', '.join(follow)} }}")
        print("\nTabla de Parsing:")
        for key, production in self.parse_table.items():
            print(f"M[{key[0]}, {key[1]}] = {production}")

class Parser:
    def __init__(self, grammar_file, tokens_file):
        self.grammar = Grammar(grammar_file)
        self.tokens = self.tokenize_from_file(tokens_file)
        self.position = 0
        self.current_token = self.tokens[self.position] if self.tokens else None
        self.stack = ['$']
        self.stack.append(self.grammar.start_symbol)
        self.error_reported = False
        self.current_rule = None  # Almacena la regla en evaluación

    def advance(self):
        """Avanza al siguiente token."""
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = ('$', '$', self.current_token[2], self.current_token[3])

    def parse(self):
        """Realiza el análisis sintáctico."""
        while self.stack:
            top = self.stack.pop()
            token_name = self.current_token[0]
            lexeme = self.current_token[1]

            if top == 'ε':
                continue
            elif top in self.grammar.terminals:
                if top == token_name or top == lexeme:
                    self.advance()
                else:
                    self.report_syntax_error([top], current_rule=self.current_rule)
                    break
            elif top in self.grammar.non_terminals:
                # Actualizar la regla en evaluación
                self.current_rule = top

                # Utiliza la tabla de parsing para decidir la producción
                key = (top, token_name)
                if key not in self.grammar.parse_table:
                    key = (top, lexeme)
                if key in self.grammar.parse_table:
                    production = self.grammar.parse_table[key]
                    for symbol in reversed(production):
                        self.stack.append(symbol)
                else:
                    # Si no se puede decidir, reportar error
                    expected = self.expected_tokens(top)
                    self.report_syntax_error(expected, current_rule=self.current_rule)
                    break
            else:
                self.report_syntax_error([top], current_rule=self.current_rule)
                break

        if not self.error_reported:
            print("El análisis sintáctico ha finalizado exitosamente.")

    def expected_tokens(self, non_terminal):
        """Obtiene la lista de tokens esperados en un punto dado."""
        expected = []
        for (nt, terminal), production in self.grammar.parse_table.items():
            if nt == non_terminal:
                expected.append(terminal)
        return expected

    def report_syntax_error(self, expected_tokens, current_rule):
        """Reporte de error sintáctico incluyendo la regla en evaluación."""
        if not self.error_reported:
            line = self.current_token[2]
            column = self.current_token[3]
            found_lexeme = self.current_token[1]
            expected = ', '.join(f'"{et}"' for et in expected_tokens)
            error_message = (f"<{line},{column}> Error sintáctico en la regla '{current_rule}': "
                             f"se encontró \"{found_lexeme}\"; se esperaba: {expected}.")
            print(error_message)
            self.error_reported = True

    def tokenize_from_file(self, filename):
        """Lee los tokens desde un archivo y los devuelve en una lista."""
        tokens = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Elimina los caracteres '<' y '>' y divide por comas
                    parts = line.strip('<>').split(',')
                    if not parts:
                        continue
                    token_name = parts[0].strip()
                    if len(parts) == 4:
                        # Formato: <token_name, lexeme, line, column>
                        lexeme = parts[1].strip()
                        line_num = int(parts[2].strip())
                        column = int(parts[3].strip())
                    elif len(parts) == 3:
                        # Formato: <token_name, line, column>
                        lexeme = token_name  # Usamos el nombre del token como lexema
                        line_num = int(parts[1].strip())
                        column = int(parts[2].strip())
                    else:
                        print(f"Formato de token inválido: {line}")
                        sys.exit(1)
                    tokens.append((token_name, lexeme, line_num, column))
                # Añadir el token de fin de entrada
                if tokens:
                    tokens.append(('$', '$', tokens[-1][2], tokens[-1][3]))
                else:
                    tokens.append(('$', '$', 0, 0))
                return tokens
        except FileNotFoundError:
            print(f"Error: El archivo '{filename}' no se encontró.")
            sys.exit(1)

