def safe_div(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
