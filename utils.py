def is_integer(arg) -> bool:
    try:
        int(arg)
        return True
    except ValueError:
        return False
