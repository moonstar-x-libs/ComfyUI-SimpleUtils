# ComfyUI-SimpleUtils

A collection of simple utility nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI).

## Nodes

All nodes live under the **SimpleUtils** category in the node menu.

### Image

| Node | Inputs | Outputs | Description |
| --- | --- | --- | --- |
| **Image > Base64ToImage** | `base64` (`STRING`) | `IMAGE` (`IMAGE`) | Decodes a base64 encoded image string into an image. |
| **Image > ImageToBase64** | `image` (`IMAGE`) | `BASE64` (`STRING`) | Encodes an image into a base64 string (PNG). |

#### Notes

- **Base64ToImage** expects a raw base64 string, without a `data:image/...;base64,` prefix. Any format Pillow can read is accepted. The image is always converted to RGB, so alpha channels are discarded.
- **ImageToBase64** encodes only the **first** image of the incoming batch. The output is a raw PNG base64 string with no data URI prefix.

## Installation

### ComfyUI Manager / Comfy Registry

Search for `ComfyUI-SimpleUtils` in [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager), or install it with the [Comfy CLI](https://github.com/Comfy-Org/comfy-cli):

```bash
comfy node install comfyui-simpleutils
```

### Manual

Clone the repository into your ComfyUI `custom_nodes` directory and restart ComfyUI:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/moonstar-x-libs/ComfyUI-SimpleUtils.git
```

The only dependencies are `numpy`, `pillow` and `torch`, which ComfyUI already ships with.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [Poe the Poet](https://poethepoet.natn.io/) as a task runner. The Python version is pinned in `.python-version`.

```bash
# Install the project along with the dev dependencies
uv sync --all-extras

# Install the pre-commit hooks (ruff + black)
uv run pre-commit install
```

### Tasks

| Command | Description |
| --- | --- |
| `uv run poe lint` | Lint with Ruff. |
| `uv run poe lint-fix` | Lint with Ruff and apply automatic fixes. |
| `uv run poe format` | Check formatting with Black. |
| `uv run poe format-fix` | Format the code with Black. |
| `uv run poe test` | Run the test suite with pytest. |
| `uv run poe test-coverage-run` | Run the test suite with coverage. |
| `uv run poe test-coverage-lcov` | Generate an `lcov.info` coverage report. |

### Project Structure

```text
.
├── __init__.py              # ComfyUI entry point, exports the node mappings
├── src
│   ├── node_mappings.py     # Aggregates the mappings of every node group
│   ├── nodes
│   │   └── image            # Image nodes and their mappings
│   └── utils                # Shared helpers (e.g. tensor <-> base64 conversion)
└── tests                    # pytest suite, mirroring the src layout
```

To add a new node, create its class under `src/nodes/<group>/`, register it in that group's `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`, and make sure the group's mappings are merged in `src/node_mappings.py`.

### CI

GitHub Actions run linting, formatting checks and tests on every push and pull request to `main`, followed by a backwards compatibility check with [node-diff](https://github.com/Comfy-Org/node-diff). Publishing a release runs the same checks and then publishes the node to the [Comfy Registry](https://registry.comfy.org).

## License

This project is licensed under the [MIT License](LICENSE).
