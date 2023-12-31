import json
import pathlib
import typing

import dotenv
import openai
import typer
from gitignore_parser import parse_gitignore
from loguru import logger

from test_fixer import communication_model as comm_model
from test_fixer import utils

path_to_prompt_file = pathlib.Path(__file__).parent / "prompt.txt"


prompt = open(path_to_prompt_file).read().strip()


def _should_ignore(path: pathlib.Path, directory: pathlib.Path):
    matches = parse_gitignore(directory / ".gitignore")
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
    if _should_ignore(file_, directory=relative_to):
        return []

    if file_.is_file():
        return [_get_command_from_file(file_)]

    for f in file_.iterdir():
        if f.name == ".gitignore":
            continue
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


def fix_tests(
    directory: typing.Annotated[str, typer.Option()],
    tests_output_file: typing.Annotated[str, typer.Option()],
):
    directory = pathlib.Path(directory)
    tests_output_file = pathlib.Path(tests_output_file)

    openai.api_key = dotenv.get_key(".env", "OPENAI_API_KEY")

    tests_output_file = pathlib.Path(tests_output_file)

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
        directory,
        relative_to=directory,
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
    logger.debug(f"Messages ({len(messages)}) with files prepared")

    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=json_messages)
    logger.debug("Chat completed")

    reply_json = chat.choices[0].message.content
    reply_json = json.loads(reply_json)

    logger.debug(f"Patch received\n{reply_json['patch']}")
    if utils.is_debug_mode_enabled():
        utils.save_fix_in_file(
            pathlib.Path("fixes", "fix.patch"),
            fix=reply_json["patch"],
            overwrite=True,
        )
    utils.apply_patch(reply_json["patch"], directory=pathlib.Path(directory))
