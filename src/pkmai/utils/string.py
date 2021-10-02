import re

to_snake_case_re = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)(?<!_)[A-Z](?=[a-z]))")
to_id_re = re.compile(r"\W+")


def to_snake_case(camel: str) -> str:
    return to_snake_case_re.sub(r"_\1", camel).lower()


def to_camel_case(snake: str) -> str:
    components = snake.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_id(name: str) -> str:
    return to_id_re.sub("", name).lower()
