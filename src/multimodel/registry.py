MODELS = {"prices": {'version': '1', 'metrics': {'rmse': 12}}, "churn": {'version': '1', 'metrics': {'auc': 0.8}}}
CHAMPION = "prices"


class InputError(ValueError):
    pass


def register(name, version, metrics):
    if not isinstance(name, str) or not name:
        raise InputError("name is required")
    MODELS[name] = {"version": version, "metrics": metrics or {}}
    return {"name": name, **MODELS[name]}


def promote(name):
    if name not in MODELS:
        raise InputError("unknown model")
    global CHAMPION
    CHAMPION = name
    return {"champion": CHAMPION, "applied": False}


def champion():
    return {"champion": CHAMPION, "model": MODELS[CHAMPION]}
