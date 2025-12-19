# BridgeIA

[![CI](https://github.com/BridgeIA/BridgeIA/actions/workflows/ci.yml/badge.svg)](https://github.com/BridgeIA/BridgeIA/actions/workflows/ci.yml)
[![Dependency Review](https://github.com/BridgeIA/BridgeIA/actions/workflows/dependency-review.yml/badge.svg)](https://github.com/BridgeIA/BridgeIA/actions/workflows/dependency-review.yml)

BridgeIA is a lightweight Poly Bridge-like prototype built with Pygame and Pymunk.

## Features

- Build bridges by connecting anchor points.
- Budget-aware construction constraints.
- Simple level renderer for quick iteration.

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/)

## Getting started

```bash
poetry install
poetry run python -m bridgeia
```

### Render a screenshot

```bash
poetry run python -m bridgeia --screenshot artifacts/bridgeia.png
```

## Contributing

We welcome contributions! Please read [`CONTRIBUTING.md`](.github/CONTRIBUTING.md) for setup tips,
branching guidance, and how to submit changes.

## Code of Conduct

This project follows the Contributor Covenant. Please read [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md)
for expected behavior.

## Security

Please see [`SECURITY.md`](.github/SECURITY.md) for reporting security issues.

## License

License information will be added soon.
