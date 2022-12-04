def make_errors(errors):
    return [
        {
            "key": i,
            "error": errors[i][0],
        }
        for i in errors]
