# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## How to Run

```bash
# From the starter/ directory
pip install -r backend/requirements.txt
pytest                 # runs the unit and API tests
python -m backend.app  # starts the server at http://127.0.0.1:5000/
```

## Reflection on the TDD Process

### How I Worked

I implemented `OrderTracker` in six Red → Green → Refactor cycles, with one commit per cycle
(`Ciclo 1` through `Ciclo 6` in the git history). In each cycle I wrote the test first,
ran it to watch it fail, and then wrote the minimum code needed to make it pass:

1. `add_order` saves a new order with a default status of `pending`.
2. `add_order` rejects duplicate IDs with a `ValueError`.
3. `get_order_by_id` returns the order, or `None` if it does not exist.
4. `update_order_status` changes the status and fails if the order does not exist.
5. `list_all_orders` returns every order as a list.
6. `list_orders_by_status` filters by status and returns an empty list when nothing matches.

Once the logic was covered, I moved on to the API layer: I ran `tests/test_api.py`, watched
the integration tests fail, and implemented the endpoints in `app.py` until they passed.

### How TDD Shaped the Design

- **Separation of concerns.** Because the unit tests use a `Mock` instead of the real
  storage, `OrderTracker` had to receive its storage through dependency injection and could
  not depend on Flask. That kept the business logic isolated in `order_tracker.py`, and the
  routes in `app.py` became a thin layer that only translates between HTTP and the tracker
  (for example, turning a `ValueError` into a 400 or 404).
- **Minimal code.** Writing only what each test required kept me from adding functionality
  nobody asked for. For example, `list_orders_by_status` reuses `list_all_orders` instead of
  duplicating the storage access.
- **Explicit edge cases.** Having to write the test first forced me to decide what happens in
  the error cases (missing order, duplicate ID, filter with no matches) before writing the
  code, instead of discovering them afterwards.

### What I Learned

- **A passing test is not the same as a useful test.** My first `add_order` test only checked
  that `save_order` had been called. It would have kept passing even if the order were saved
  with wrong data or a different status. I strengthened it with `assert_called_once_with(...)`
  to verify the ID and the full dictionary, including the default `pending` status. The
  lesson: besides checking that something happened, you have to check what happened.
- **Mocks and integration tests complement each other.** Mock-based unit tests are fast and
  point to exactly which method fails, but they do not prove the pieces work together. The API
  tests, which use the real `InMemoryStorage`, cover that part. `InMemoryStorage` copies
  dictionaries on read and on write, so modifying a returned order does not accidentally change
  the stored data. That kind of bug only shows up in an integration test.

### Challenges

- At first it was hard to write a test for a method that did not exist yet and to decide how
  much code counted as "the minimum". It became more natural as the cycles went on.
- Configuring the mock (the `return_value` of `get_order` and `get_all_orders`) to simulate
  each scenario requires thinking about the storage state before writing the test.

### Changes After Review

The project review pointed out two robustness gaps in the API. I fixed both with the same
Red → Green cycle: first new tests that failed, then the code to make them pass.

- **Malformed request bodies returned 500.** The POST and PUT routes indexed the JSON body
  directly, so a missing `order_id` or `new_status` raised a `KeyError`, and a non-JSON body
  failed as well. Both routes now validate the body first and respond with a `400` that names
  the missing fields.
- **Invalid statuses were accepted, and every error became a 404.** `OrderTracker` now only
  accepts the statuses the frontend offers (`pending`, `processing`, `shipped`) and raises a
  `ValueError` for any other value, both in `add_order` and in `update_order_status`. A missing
  order raises `OrderNotFoundError`, a subclass of `ValueError`, so the PUT route can tell the
  two apart: missing order → `404`, invalid status → `400`.

The new unit tests live in `tests/test_order_tracker.py`. The new API tests live in
`tests/test_api_validation.py`, so the provided `tests/test_api.py` stays untouched.

This review taught me that TDD only drives the cases you think of when you write the tests. My
first suite covered the happy paths and the obvious business errors, but not what happens when
a client sends bad input to the HTTP layer.

### What I Would Improve

- Validate the values of the fields in `add_order` (for example, a positive integer quantity),
  not only their presence.
- Return `409 Conflict` instead of `400` for duplicate order IDs.
- Add unit tests for `InMemoryStorage`.
