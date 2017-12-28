class RPMSpecError(Exception):
    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


def format_tag_line(tag: str, value: str) -> str:
    return tag + ":" + (16 - len(tag) - 1) * " " + value + "\n"
