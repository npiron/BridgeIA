# Contributing to BridgeIA

Thank you for taking the time to contribute!

## Development setup

1. Install [Poetry](https://python-poetry.org/).
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the prototype:
   ```bash
   poetry run python -m bridgeia
   ```

## Project structure

- `bridgeia/` - application code
- `levels/` - level JSON files
- `.github/workflows/` - automation pipelines

## Pull requests

- Keep changes focused and scoped to a single goal.
- Make sure the CI workflow passes.
- Describe your changes clearly in the PR summary.

## Reporting issues

Please include:
- clear reproduction steps
- expected vs actual behavior
- logs or screenshots if applicable
