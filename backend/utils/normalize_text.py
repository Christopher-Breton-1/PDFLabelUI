def normalize_text(text):
    print("\n\n", text,"\n\n")
    text = text.lower()
    valid_chars = "1234567890qwertyuiopasdfghjklzxcvbnm"
    return "".join(c for c in text if c in valid_chars)
