def registry_tokens_typo_match(left_token: str, right_token: str) -> bool:
    """Перевіряє збіг токенів реєстру з допуском однієї опечатки.
    Checks registry token match allowing a single-character typo.
    """

    left = left_token.strip().lower()
    right = right_token.strip().lower()
    if not left or not right:
        return False
    if left == right or left in right or right in left:
        return True
    if len(left) < 4 or len(right) < 4:
        return False
    return _levenshtein_distance_at_most_one(left, right)


def query_tokens_match_registry_name(query_tokens: set[str], name_tokens: set[str]) -> bool:
    """Чи всі токени запиту збігаються з токенами назви (з typo-tolerance).
    Whether all query tokens match name tokens (with typo tolerance).
    """

    if not query_tokens or not name_tokens:
        return False
    return all(
        any(registry_tokens_typo_match(query_token, name_token) for name_token in name_tokens)
        for query_token in query_tokens
    )


def _levenshtein_distance_at_most_one(left: str, right: str) -> bool:
    if left == right:
        return True
    if abs(len(left) - len(right)) > 1:
        return False
    if len(left) > len(right):
        left, right = right, left

    if len(left) == len(right):
        mismatches = sum(1 for left_char, right_char in zip(left, right, strict=True) if left_char != right_char)
        return mismatches <= 1

    index = 0
    skipped = False
    while index < len(left):
        if left[index] != right[index]:
            if skipped:
                return False
            skipped = True
            right = right[:index] + right[index + 1 :]
            continue
        index += 1
    return True
