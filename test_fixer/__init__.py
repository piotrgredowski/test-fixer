import datetime
import json
import pathlib

import dotenv
import openai
from gitignore_parser import parse_gitignore

from test_fixer import communication_model as comm_model

path_to_prompt_file = pathlib.Path(__file__).parent / "prompt.txt"


prompt = open(path_to_prompt_file).read().strip()


example_directory = pathlib.Path("examples")
tests_output_file = pathlib.Path("tests_output.txt")


# tests_output =
def iter_all_files_from_dir():
    return pathlib.Path(example_directory)
    paths = [pathlib.Path(__name__).resolve()]
    print(paths)
    pass


def _should_ignore(path: pathlib.Path):
    matches = parse_gitignore(".gitignore")
    return matches(path)


def _get_command_from_file(
    file_: pathlib.Path, relative_to: pathlib.Path, file_extensions_to_skip: list[str]
):
    if file_.suffix in file_extensions_to_skip:
        return []
    file_content = file_.read_text()

    return comm_model.FixerCommand(
        type=comm_model.CommandType.file,
        content=file_content,
        metadata=comm_model.CommandMetadata(
            path_to_file=str(file_.relative_to(relative_to))
        ),
    )


def _get_commands_for_path(
    file_: pathlib.Path,
    relative_to: pathlib.Path,
    commands: list[comm_model.FixerCommand] | None = None,
    file_extensions_to_skip: list[str] | None = None,
):
    if commands is None:
        commands = []
    if file_extensions_to_skip is None:
        file_extensions_to_skip = []
    if _should_ignore(file_):
        return []

    if file_.is_file():
        return [_get_command_from_file(file_)]

    for f in file_.iterdir():
        if f.is_file():
            commands.append(
                _get_command_from_file(
                    f,
                    relative_to=relative_to,
                    file_extensions_to_skip=file_extensions_to_skip,
                )
            )
        elif f.is_dir():
            commands.extend(
                _get_commands_for_path(
                    f,
                    relative_to=relative_to,
                    file_extensions_to_skip=file_extensions_to_skip,
                )
            )
        else:
            print("OOOOPS")
    return commands


def save_fix_in_file(filename: str, fix: str):
    # add readable timestamp to filename if it already exists
    file_path = pathlib.Path(filename)
    if file_path.exists():
        file_path = (
            file_path.parent
            / f"{file_path.stem}_{datetime.datetime.now().isoformat()}{file_path.suffix}"
        )
    # make parent dir if doesnt exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(fix)


def main():
    openai.api_key = dotenv.get_key(".env", "OPENAI_API_KEY")

    file_extensions_to_skip = [".pyc"]

    messages = [comm_model.Message(role=comm_model.MessageRole.system, content=prompt)]

    test_results = comm_model.FixerCommand(
        type=comm_model.CommandType.test_results,
        content=tests_output_file.read_text(),
    )
    messages.append(
        comm_model.Message(role=comm_model.MessageRole.user, content=test_results)
    )

    commands = _get_commands_for_path(
        example_directory,
        relative_to=example_directory,
        file_extensions_to_skip=file_extensions_to_skip,
    )
    for command in commands:
        if not command or not command.content:
            continue
        message = comm_model.Message(role=comm_model.MessageRole.user, content=command)
        messages.append(message)
    submit_message = comm_model.Message(
        role=comm_model.MessageRole.user,
        content=comm_model.FixerCommand(type=comm_model.CommandType.submit),
    )
    messages.append(submit_message)
    json_messages = [
        json.loads(message.model_dump_json(round_trip=True)) for message in messages
    ]

    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=json_messages)
    # chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=json_messages)

    reply_json = chat.choices[0].message.content
    reply_json = json.loads(reply_json)

    save_fix_in_file(
        pathlib.Path("fixes", "fix.patch"),
        fix=reply_json["content"],
    )
    print(reply_json["content"])
    pass
