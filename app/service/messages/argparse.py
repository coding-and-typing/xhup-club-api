# -*- coding: utf-8 -*-


class Argument(object):
    def __init__(self,
                 name,
                 type=None,
                 default=None,
                 choices=tuple(),
                 required=False,
                 help=""):
        self.name = name
        self.type = type
        self.default = default
        self.choices = choices
        self.required = required
        self.help = help

    @property
    def usage(self):
        return f"  {self.name}\t{self.help}"  # 开头缩进两个空格


class ArgumentParser(object):
    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description  # 简短的说明
        self.args_required = []
        self.args_optional = []

    def add_argument(self,
                     name,
                     type=None,
                     default=None,
                     choices=tuple(),
                     required=False,
                     help=""):
        """添加参数"""
        arg = Argument(name, type, default, choices, required, help)

        if required:
            self.args_required.append(arg)
        else:
            self.args_optional.append(arg)

    @property
    def usage(self):
        usage_required = (arg.usage for arg in self.args_required)
        usage_optional = (arg.usage for arg in self.args_optional)

        return "\n\n".join((f"{self.command}：{self.description}",
                            "必要参数：",
                            "\n".join(usage_required),
                            "可选参数：",
                            "\n".join(usage_optional)))

    def parse(self, command):
        """解析命令"""
        pass

    @staticmethod
    def make_args_parser(command, description, args):
        parser = ArgumentParser(command, description=description)
        for arg in args:
            parser.add_argument(**arg)

        return parser

