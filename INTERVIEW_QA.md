# multi-model-inference-platform — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does multi-model-inference-platform address, and what can you demonstrate?

Register a second model and promote it without rolling a cluster.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/multimodel/main.py`](src/multimodel/main.py): Implementation or supporting configuration.
- [`src/multimodel/registry.py`](src/multimodel/registry.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/multimodel/__init__.py`](src/multimodel/__init__.py): Implementation or supporting configuration.
- [`tests/test_registry.py`](tests/test_registry.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `promote` and explain the decision it makes?

The main walkthrough here is `promote(name)` in [`src/multimodel/registry.py`](src/multimodel/registry.py#L16).

```python
def promote(name):
    if name not in MODELS:
        raise InputError("unknown model")
    global CHAMPION
    CHAMPION = name
    return {"champion": CHAMPION, "applied": False}
```

The implementation calls `InputError`. In an interview, trace those calls in execution order using a fixture input.

## 4. What responsibility does `register` have?

`register(name, version, metrics)` is defined in [`src/multimodel/registry.py`](src/multimodel/registry.py#L9).

Its return expressions include:

- `{'name': name, **MODELS[name]}`

It uses `InputError`, `isinstance`. This is the code path I would compare against the caller to explain responsibility boundaries.

## 5. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/multimodel/main.py`](src/multimodel/main.py#L22).
- `HTTPException(status_code=422, detail=str(exc))` in [`src/multimodel/main.py`](src/multimodel/main.py#L30).
- `InputError('name is required')` in [`src/multimodel/registry.py`](src/multimodel/registry.py#L11).
- `InputError('unknown model')` in [`src/multimodel/registry.py`](src/multimodel/registry.py#L18).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 6. Which test would you use to demonstrate correctness?

[`tests/test_registry.py`](tests/test_registry.py#L12) contains `test_promote`:

```python
def test_promote():
    client.post("/models", json={"name": "fraud", "version": "2", "metrics": {"auc": 0.9}})
    payload = client.post("/promote", json={"name": "fraud"}).json()
    assert payload["champion"] == "fraud"
    assert payload["applied"] is False
    assert client.get("/champion").json()["champion"] == "fraud"
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 7. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/multimodel/main.py`](src/multimodel/main.py#L8).
- `GET /champion` → `get_champion` in [`src/multimodel/main.py`](src/multimodel/main.py#L13).
- `POST /models` → `post_model` in [`src/multimodel/main.py`](src/multimodel/main.py#L18).
- `POST /promote` → `post_promote` in [`src/multimodel/main.py`](src/multimodel/main.py#L26).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 8. Where does state live, and what happens with multiple workers?

Module-level containers include `MODELS` in [`src/multimodel/registry.py`](src/multimodel/registry.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 9. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 10. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 11. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 12. What is the input-to-output contract of `promote`?

In [`src/multimodel/registry.py`](src/multimodel/registry.py#L16), `promote(name)` receives the inputs. The function computes these intermediate values:

- `CHAMPION = name`

Its result is defined by:

- `{'champion': CHAMPION, 'applied': False}`

## 13. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/multimodel/registry.py`](src/multimodel/registry.py#L16) branches on:

- `name not in MODELS`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
