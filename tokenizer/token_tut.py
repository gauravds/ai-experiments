import tiktoken

encoder = tiktoken.encoding_for_model("gpt-4o")
# encoder = tiktoken.encoding_for_model("gpt-4")
# encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")

print("Vocab size: ", encoder.n_vocab)

text = "Hello, world! this is a test"
# tokens = encoder.encode(text)  # [13225, 11, 2375, 0, 495, 382, 261, 1746]
# print(tokens)

# decoded_text = encoder.decode(tokens)
# print(decoded_text)
