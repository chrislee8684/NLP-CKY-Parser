def read_grammar(file_name):
    grammar = {'nonterminals': {}, 'terminals': {}}
    with open(file_name, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                parts = line.strip().split(' --> ')
                left = parts[0]
                right = tuple(parts[1].split(' '))
                if len(right) == 1:  # Terminal rule
                    if right not in grammar['terminals']:
                        grammar['terminals'][right] = []
                    grammar['terminals'][right].append(left)
                else:  # Nonterminal rule
                    if right not in grammar['nonterminals']:
                        grammar['nonterminals'][right] = []
                    grammar['nonterminals'][right].append(left)
    return grammar

def preprocess_sentence(sentence):
    import string
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))
    return sentence.lower()

def cky_parse(sentence, grammar):
    words = sentence.split()
    n = len(words)
    table = [[set() for _ in range(n + 1)] for _ in range(n)]

    # Fill in table for single words with terminal rules
    for i, word in enumerate(words):
        if (word,) in grammar['terminals']:
            table[i][i + 1].update(grammar['terminals'][(word,)])

    # Apply nonterminal rules
    for length in range(2, n + 1):
        for start in range(n - length + 1):
            end = start + length
            for mid in range(start + 1, end):
                for A in table[start][mid]:
                    for B in table[mid][end]:
                        if (A, B) in grammar['nonterminals']:
                            table[start][end].update(grammar['nonterminals'][(A, B)])

    # Reconstruct parses
    def reconstruct(start, end, symbol, current_parse):
        if end - start == 1:  # Base case for terminals
            return [f'[{symbol} {words[start]}]']
        parses = []
        for mid in range(start + 1, end):
            for A in table[start][mid]:
                for B in table[mid][end]:
                    if (A, B) in grammar['nonterminals'] and symbol in grammar['nonterminals'][(A, B)]:
                        left_parses = reconstruct(start, mid, A, current_parse)
                        right_parses = reconstruct(mid, end, B, current_parse)
                        for lp in left_parses:
                            for rp in right_parses:
                                parses.append(f'[{symbol} {lp} {rp}]')
        return parses

    # Start reconstruction from the 'S' symbol
    final_parses = reconstruct(0, n, 'S', '')
    return final_parses if final_parses else ["NO VALID PARSES"]

def format_tree(tree_string):
    indent_level = 0
    formatted_string = ""
    for i, char in enumerate(tree_string):
        if char == '[':
            if indent_level > 0:  # Add newline and indent before opening, if not the first bracket
                formatted_string += "\n" + "  " * indent_level
            indent_level += 1
        elif char == ']':
            indent_level -= 1
            if tree_string[i-1] != ']':  # If the last character is not a closing bracket, don't indent
                pass
            else:
                formatted_string += "\n" + "  " * indent_level
        formatted_string += char
    return formatted_string.strip()

def main():
    cfg_file = input("Enter the name of the CFG file in CNF: ")
    grammar = read_grammar(cfg_file)
    print("Loading grammar...")

    display_trees = input("Do you want textual parse trees to be displayed (y/n)?: ").lower() == 'y'

    while True:
        sentence = input("Enter a sentence: ")
        if sentence.lower() == "quit":
            print("Goodbye!")
            break
        preprocessed_sentence = preprocess_sentence(sentence)
        valid_parses = cky_parse(preprocessed_sentence, grammar)
        if valid_parses == ["NO VALID PARSES"]:
            print("NO VALID PARSES")
        else:
            print("VALID SENTENCE" + "\n")
            for i, parse in enumerate(valid_parses, start=1):
                print(f"Valid parse #{i}:\n{parse}")
                if display_trees:
                    tree = format_tree(parse)
                    print("\n" + tree)
            print("\n"+f"Number of valid parses: {len(valid_parses)}"+"\n")

if __name__ == "__main__":
    main()