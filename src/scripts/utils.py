
def is_number(s: str):
    try:
        int(s)
    except:
        try:
            float(s)
        except:
            return False

    return True
