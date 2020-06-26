from dataclasses import dataclass, field


@dataclass(frozen=True)
class Core:
    surname: str = field(default="Adios")


@dataclass(frozen=True)
class Extension(Core):
    name: str = field(default="Hola")
