import datetime
import os
import pathlib
import subprocess
import tempfile


def save_fix_in_file(filename: str, fix: str, overwrite: bool = False):
    file_path = pathlib.Path(filename)
    if file_path.exists() and not overwrite:
        file_path = (
            file_path.parent
            / f"{file_path.stem}_{datetime.datetime.now().isoformat()}{file_path.suffix}"
        )
    # make parent dir if doesnt exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(fix)


def apply_patch(patch: str, directory: pathlib.Path):
    with tempfile.NamedTemporaryFile(
        dir=directory.parent, suffix=".patch", delete=False
    ) as temp_file:
        # save_fix_in_file(temp_file.name, patch, overwrite=True)

        temp_file.write(patch.encode())

    cmd = (
        # f"cd {directory.parent}; "
        # f"git apply {temp_file.name} -v"
        f"git apply {temp_file.name} -v --directory={directory.name}"
    ).strip()
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=directory.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(result)
    pass


def is_debug_mode_enabled():
    return str(os.environ.get("DEBUG", 0)) == "1"
