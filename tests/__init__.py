def normalize_spaces(input):
    if isinstance(input, str):
        return ' '.join(input.split())
    return normalize_spaces(' '.join(item.text for item in input))
