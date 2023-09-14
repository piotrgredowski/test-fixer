import enum
import pathlib

import pydantic


class CommandType(enum.StrEnum):
    test_results = enum.auto()
    file = enum.auto()
    submit = enum.auto()
    ack = enum.auto()
    fix = enum.auto()


class CommandMetadata(pydantic.BaseModel):
    path_to_file: pathlib.Path | str


class FixerCommand(pydantic.BaseModel):
    type: CommandType
    content: dict | str | None = None
    metadata: CommandMetadata | None = None


class MessageRole(enum.StrEnum):
    system = enum.auto()
    user = enum.auto()


class Message(pydantic.BaseModel):
    role: MessageRole
    content: FixerCommand | str

    @pydantic.field_serializer("content")
    def serialize_content(self, v):
        if isinstance(v, FixerCommand):
            return v.model_dump_json()
        return v

    # return content as str containg json
    # def content(self):
    #     return self.content.json()
