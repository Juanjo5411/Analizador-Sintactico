# Palabras reservadas adicionales
RESERVED_WORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", 
    "class", "continue", "def", "del", "elif", "else", "except", "finally", 
    "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", 
    "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
    "match", "case", "type", "finally", "nonlocal", "assert", "global", "del","print"
}


# Operadores y delimitadores adicionales
OPERATORS = {
    "+": "tk_suma", "-": "tk_resta", "*": "tk_multiplicacion", "/": "tk_division",
    "%": "tk_modulo", "=": "tk_asig", "==": "tk_igual", "!=": "tk_distinto",
    "<": "tk_menor", ">": "tk_mayor", "<=": "tk_menor_igual", ">=": "tk_mayor_igual",
    "and": "tk_and", "or": "tk_or", "not": "tk_not",
    "+=": "tk_suma_asig", "-=": "tk_resta_asig", "*=": "tk_mult_asig", "/=": "tk_div_asig", 
    "%=": "tk_mod_asig", "&=": "tk_and_asig", "|=": "tk_or_asig", "^=": "tk_xor_asig", 
    "<<=": "tk_izq_asig", ">>=": "tk_der_asig", "**=": "tk_exp_asig", "//=": "tk_floor_div_asig", 
    "//": "tk_floor_div", "**": "tk_exponente", "@": "tk_arr", 
    "<<": "tk_shift_izq", ">>": "tk_shift_der", "&": "tk_and_bit", "|": "tk_or_bit", 
    "^": "tk_xor_bit", "~": "tk_complemento", ":=": "tk_morsa", "->": "tk_flecha_funcion"
}


DELIMITERS = {
    "(": "tk_par_izq", ")": "tk_par_der", "[": "tk_corchete_izq", "]": "tk_corchete_der",
    "{": "tk_llave_izq", "}": "tk_llave_der", ",": "tk_coma", ":": "tk_dos_puntos",
    ".": "tk_punto", ";": "tk_punto_coma"
}
# Funciones para categorizar tokens
def is_reserved_word(word):
    return word in RESERVED_WORDS 

def is_operator(char):
    return char in OPERATORS

def is_delimiter(char):
    return char in DELIMITERS
