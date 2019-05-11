# -*- coding: utf-8 -*-
import re
from typing import Optional, Dict, List


kwarg_pattern = re.compile(r"(?P<name>\S+)=(?P<value>\S+)")


class Argument(object):
    def __init__(self,
                 name,
                 type=None,
                 default=None,
                 choices=tuple(),
                 help=""):
        self.name = name
        self.type = type
        self.default = default
        self.choices = choices
        self.help = help

    @property
    def usage(self):
        return f"  {self.name}\t{self.help}"  # 开头缩进两个空格

    def parse(self, value):
        if self.type:
            try:
                value = self.type(value)
            except ValueError:
                return False, f"参数 {self.name} 的格式不正确：{value}"

            if self.choices and value not in self.choices:
                return False, f"{self.name}：不存在该选项"

            return True, value


class ArgumentParser(object):
    """
    命令格式：command option1=xxx [option3=xxx] [option4=xxx] target
    """
    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description  # 简短的说明

        self.arg_primary: Optional[Argument] = None
        self.kwargs_required: Dict[str, Argument] = dict()  # 必要选项
        self.kwargs_optional: Dict[str, Argument] = dict()  # 可选参数

    def set_arg_primary(self,
                        name,
                        type=None,
                        default=None,
                        choices=tuple(),
                        help=""):
        """设置命令的目标参数"""
        self.arg_primary = Argument(name, type, default, choices, help)

    def add_kwarg(self,
                  name,
                  type=None,
                  default=None,
                  choices=tuple(),
                  required=False,
                  help=""):
        """添加关键字参数"""
        argument = Argument(name, type, default, choices, help)

        if required:
            self.kwargs_required[name] = argument
        else:
            self.kwargs_optional[name] = argument

    @property
    def usage(self):
        usages_required = [arg.usage for arg in self.kwargs_required.values()]
        usages_optional = [arg.usage for arg in self.kwargs_optional.values()]
        usage_head = f"{self.command}：{self.description}"
        if self.arg_primary:
            usage_head += "\n" + self.arg_primary.usage

        usage1 = ("必要参数：\n" + "\n".join(usages_required)) if usages_required else ""
        usage2 = ("可选参数：\n" + "\n".join(usages_optional)) if usages_optional else ""

        return "\n\n".join((usage_head, usage1, usage2)).strip()

    def is_required(self, arg_name):
        return arg_name in self.kwargs_required

    def parse(self, command):
        """解析命令"""
        res = {
            "primary": None,
            "options": dict(),
        }

        options_required = {arg.name: 1 for arg in self.kwargs_required.values()}
        parts = re.split(r"\s+", command)[1:]

        for p in parts:
            matcher = kwarg_pattern.match(p)
            if matcher:  # 关键字参数
                groupdict = matcher.groupdict()
                name = groupdict['name']
                if self.is_required(name):
                    options_required[name] -= 1
                    argument = self.kwargs_required[name]
                else:
                    argument = self.kwargs_optional[name]

                match, value = argument.parse(groupdict['value'])
                if match:
                    res['options'][name] = value
                else:
                    return False, {"message": value}  # 此时 value 是错误信息
            elif self.arg_primary:  # 主参数
                if not res['primary']:
                    res['primary'] = p
                else:
                    return False, {"message": "请提供正确的参数"}

            if options_required:
                return False, {"message": f"参数缺失：{options_required}"}

        return True, res

    @staticmethod
    def make_args_parser(command, description, arg, options):
        parser = ArgumentParser(command, description=description)
        if arg:
            parser.set_arg_primary(**arg)

        for opt in options:
            parser.add_kwarg(**opt)

        return parser

