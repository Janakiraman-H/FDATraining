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

## Reflection

Using Test-Driven Development shaped our architecture by encouraging modular design and custom exceptions that cleanly map domain errors to HTTP status codes in Flask without cluttering routing logic. Red-phase failing tests highlighted subtle edge cases, such as enforcing status validation across query routes and preventing unintended in-place mutation of in-memory storage references when updating order statuses. Additionally, verifying that non-existent order queries safely return empty lists or None ensured predictable API payloads for the frontend table renderer. To prepare the application for production, the primary next step is replacing the volatile in-memory storage layer with a persistent database like PostgreSQL via SQLAlchemy, ensuring data durability across server restarts.
