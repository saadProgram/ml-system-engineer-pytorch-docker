from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class InferenceRequest(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, image: _Optional[_Iterable[bytes]] = ...) -> None: ...

class InferenceReply(_message.Message):
    __slots__ = ("pred",)
    PRED_FIELD_NUMBER: _ClassVar[int]
    pred: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, pred: _Optional[_Iterable[int]] = ...) -> None: ...
