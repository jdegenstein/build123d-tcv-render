import os
import subprocess
from pathlib import Path

def render_with_tcv(file_path):
    print(f"Processing {file_path}...")
    
    module_name = file_path.stem
    dir_path = file_path.parent.absolute()
    
    # We create a temporary script in the same directory as the user's script.
    # This temp script acts as a bridge between the user's plain build123d code 
    # and the specific main() structure required by tcv_screenshots.
    temp_script_path = dir_path / f"_temp_render_{module_name}.py"
    
    wrapper_code = f"""
import sys
sys.path.insert(0, r"{dir_path}")
import {module_name} as user_module
from build123d import Shape, Sketch, Part, Curve

def get_renderable_object(module):
    # 1. Check for explicit overrides first
    for name in ['to_export', 'result', 'part', 'assembly']:
        if hasattr(module, name):
            candidate = getattr(module, name)
            if isinstance(candidate, (Shape, Part, Sketch, Curve)):
                return candidate

    # 2. Dynamic Discovery: Scan all variables in the module
    candidates = []
    for name, obj in vars(module).items():
        if name.startswith("_"):
            continue
        if isinstance(obj, (Shape, Sketch, Part, Curve)):
            candidates.append(obj)
            
    if candidates:
        return candidates[-1]
    return None

def main():
    from tcv_screenshots import save_model, get_saved_models
    
    render_target = get_renderable_object(user_module)
    if not render_target:
        print("  [!] No 3D shape found in script.")
        return []
        
    config = {{
        "cadWidth": 1024, 
        "height": 768,
        "ambientIntensity": 1.0,
        "directIntensity": 1.1,
        "render_edges": True
    }}
    
    # Save model using the same base filename
    save_model(render_target, "{module_name}", config)
    
    return get_saved_models()
"""

    try:
        # Write the wrapper
        with open(temp_script_path, "w") as f:
            f.write(wrapper_code)
            
        # Run tcv_screenshots on the wrapper
        cmd = [
            "python", "-m", "tcv_screenshots", 
            "-f", str(temp_script_path), 
            "-o", str(dir_path)
        ]
        
        # We use subprocess here to invoke the tcv_screenshots CLI headless module
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"  [+] Saved render for {file_path.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"  [!] Render failed for {file_path.name}: {e}")
    except Exception as e:
        print(f"  [!] Error processing {file_path.name}: {e}")
    finally:
        # Clean up the temporary wrapper script
        if temp_script_path.exists():
            temp_script_path.unlink()

def main():
    repo_root = Path(".")
    ignored_dirs = {'.git', '.github', '.venv', 'venv', '__pycache__'}

    for root, dirs, files in os.walk(repo_root):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            # Look for python scripts, excluding our own wrappers or setup files
            if file.endswith(".py") and not file.startswith("_temp_render_") and file != "setup.py":
                render_with_tcv(Path(root) / file)

if __name__ == "__main__":
    main()
