# Contributing to netlog-cli

Thank you for your interest in contributing to **netlog-cli**! We welcome bug fixes, documentation improvements, feature additions, and performance enhancements.

---

## 🛠️ Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/mokshithr530/netlog-cli.git
cd netlog-cli
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install in Editable Mode with Dev Dependencies
```bash
make dev
# or: pip install -e ".[dev]"
```

---

## 🧭 Finding an Issue to Work On

If you are new to the codebase, check out issues tagged for newcomers:
- 🟢 **[Good First Issues](https://github.com/mokshithr530/netlog-cli/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)**: Beginner-friendly, well-scoped tasks with clear directions.
- 🟡 **[Help Wanted Issues](https://github.com/mokshithr530/netlog-cli/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)**: Community enhancements looking for contributors.

Feel free to comment on any issue to claim it before you start working!

---

## 🧪 Running Tests & Quality Checks

Before submitting any code changes, ensure all unit tests pass:

```bash
make test
# or: pytest -v
```

To run individual test modules:
```bash
pytest tests/test_metrics.py -v
pytest tests/test_ui.py -v
pytest tests/test_geoip.py -v
```

---

## 📝 Commit Conventions

We strictly follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This ensures clean git history and automated changelog generation:

- `feat(scope): ...` — A new feature
- `fix(scope): ...` — A bug fix
- `docs(scope): ...` — Documentation changes only
- `test(scope): ...` — Adding or modifying unit tests
- `refactor(scope): ...` — Code change that neither fixes a bug nor adds a feature
- `ci: ...` — Changes to CI/CD workflows and scripts
- `chore: ...` — Maintenance tasks, dependency updates

Example:
```bash
git commit -m "feat(ui): add live search query filter with regex matching"
```

---

## 🚀 Submitting a Pull Request

1. **Fork** the repository and create your feature branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Implement** your changes with accompanying unit tests.
3. **Verify** all existing tests pass (`make test`).
4. **Push** your branch:
   ```bash
   git push origin feat/your-feature-name
   ```
5. Open a **Pull Request** targeting the `main` branch with a clear description of the problem solved.

---

## 📜 Code of Conduct

Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all project interactions.
