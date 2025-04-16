import os


def load_words(file_path):
    words = []

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return words

    # Read words from file
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            word = line.strip()
            if word:  # Skip empty lines
                words.append(word)

    return words


def create_hash_table(words):
    hash_table = {}
    i = 0
    for word in words:
        hash_table[word] = i
        i += 1
    return hash_table


my_words = load_words("mywords.txt")
hash_table = create_hash_table(my_words)


def decoder(text):
    user_words = text.lower().split()

    tokens = []
    for word in user_words:
        if word in hash_table:
            tokens.append(hash_table[word])
        else:
            tokens.append(-1)
    return tokens


def encoder(tokens):
    encoded_words = []
    for token in tokens:
        if token == -1:
            encoded_words.append("N/A")
        else:
            encoded_words.append(my_words[token])
    return " ".join(encoded_words)


if __name__ == "__main__":
    decoded = decoder("This is a test with Gaurav Sharma नमन फल")
    print(decoded)
    encoded = encoder(decoded)
    print(encoded)
