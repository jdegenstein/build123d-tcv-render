# build123d-tcv-render

Headless automatic rendering of build123d models using `tcv-screenshots` (three-cad-viewer adjacent) -- updates renders on any script changes (pushes) to this repository (or any forks).

### How this repo works:

0. This repo contains GitHub workflows that setup `tcv-screenshots`, Playwright, and `build123d` in a GitHub runner. 
1. On pushes, the GitHub workflow (`render_tcv.yml`) executes a python script (`render_tcv.py`) which searches recursively for python files.
2. The script intelligently finds the latest `build123d` object in your script (or looks for standard variables like `to_export`, `result`, or `part`).
3. Under the hood, the script dynamically wraps your code to interface with `tcv_screenshots` and generates high-quality PNG screenshots directly from the three-cad-viewer rendering engine without requiring you to change your code.
4. Images are saved to the appropriate subfolder with the same name as the python script (e.g. `model.py` -> `model.png`).
5. The GitHub workflow **commits** via `github-actions[bot]` the changed PNG images back to this repo so they can be embedded in your `README.md` files.

### How to use this repo (ALPHA):

1. Fork the repository
2. Add a subfolder containing:
```text
- yourbuild123dscript.py
- README.md (embed the image yourbuild123dscript.png) and any other documentation / info you want to include.
```
