from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ServerInfo:
    address: str
    port: int


@dataclass(frozen=True)
class VideoKey:
    name: str
    quality: int


@dataclass(frozen=True)
class VideoDescriptor:
    hash: str
    length: int


@dataclass(frozen=True)
class AvaliabilityResponse:
    avaliable: bool
    location: Optional[str]


@dataclass(frozen=True)
class CoordinatorResponse(ServerInfo):
    location: str
