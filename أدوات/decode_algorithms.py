import io
import re
import os
import sys
import zlib
import codecs
import base64
import marshal
import zipfile
import importlib

sys.path.insert(0, os.environ["VIRTUAL_ENV"] + "/lib")
sys.path.insert(0, os.environ["VIRTUAL_ENV"] + "/tools/decode")

from typing import List
from uncompyle6 import PYTHON_VERSION
from uncompyle6.main import decompile
from rich.console import Console
from search_algorithms import CodeSearchAlgorithms

DEBUG_MODE = False
console = Console()

MAGIC_NUMBER: bytes = importlib.util.MAGIC_NUMBER
MAGIC_NUMBERS: List[bytes] = [
    b'U\r\r\n',
    b'a\r\r\n'
]
ZIP_MAGIC_NUMBER: bytes = b'PK\x03\x04'
CONFIG = __import__("config").Config
ENCODEING: str = "utf-8"
OLD_EXEC = exec
OLD_EVAL = eval
OLD_COMPILE = compile
ALGORITHOMS: List[str] = [
    "eval-filter",
    "zlib",
    "zlib-base64",
    "codecs-bz2_codec",
    "base16",
    "base32",
    "base64",
    "base85",
    "marshal",
    "machine-code",
    "zip-code",
    "exec-function",
    "eval-function",
]
COPYRIGHT: str = """
# Decoded by HackerModePro tool...
# Copyright: PSH-TEAM
# Follow us on telegram ( @psh_team )
""".lstrip()


class DecodingAlgorithms:
    def __init__(self, file_data, save_file, hash_type: dict):
        self.file_data = file_data
        self.hash_type = hash_type
        self.custom_data = None
        self._custom_eval_data = None

        if CONFIG.get('actions', 'DEBUG', cast=bool, default=False):
            sys.__dict__['EXIT'.lower()]()

        print("Finding the best algorithm:")
        for algogithom in ALGORITHOMS:
            try:
                self.file_data = self.__getattribute__(algogithom.replace("-", "_"))()

                print(f"# \033[1;32m{algogithom} ✓\033[0m", end="\r")
                if self.hash_type.get(algogithom):
                    self.hash_type[algogithom] = self.hash_type[algogithom] + 1
                else:
                    self.hash_type[algogithom] = 1

            except Exception as err:
                if DEBUG_MODE:
                    if len(str(err)) > 1000:
                        console.log(f"ERROR  length {len(str(err))}")
                        print(str(err)[:200] + str(err)[len(str(err)) - 200:])
                    else:
                        print(err)
                print(f"# \033[1;31m{algogithom}\033[0m")
                continue

            if "filter" in algogithom:
                print("")
                continue

            layers: int = 0
            while True:
                try:
                    self.file_data = self.__getattribute__(algogithom)()
                    self.hash_type[algogithom] = self.hash_type[algogithom] + 1
                    layers += 1
                    print(f"# \033[1;32m{algogithom} layers {layers} ✓\033[0m", end="\r")
                    if not self.file_data.strip():
                        raise Exception()
                except Exception:
                    print(f"\n# \033[1;32mDONE ✓\033[0m")
                    break
            break
        try:
            with open(save_file, "w") as file:
                if not COPYRIGHT in self.file_data:
                    file.write(f"# encoding: {ENCODEING}\n" + COPYRIGHT + self.file_data)
                else:
                    file.write(self.file_data)
        except Exception as e:
            print("# \033[1;31mFailed to decode the file!\033[0m")

    def eval_filter(self) -> str:
        def root_search(all_eval_functions):
            for func in all_eval_functions:
                if not func.strip():
                    all_eval_functions.remove(func)

            exceptions = 0
            for eval_f in all_eval_functions:
                try:
                    eval_body = re.findall(r"\((.+)\)", eval_f)[0]
                    bad_functions = ["eval", "exec"]
                    is_in = False
                    for function in bad_functions:
                        if function in eval_body:
                            is_in = True
                    if is_in:
                        root_search(list(set(list(CodeSearchAlgorithms.function(eval_body, "eval")))))
                        exceptions += 1
                        continue
                except IndexError:
                    continue

                try:
                    try:
                        eval_data = eval(f"b{eval_body}").decode(ENCODEING)
                    except Exception:
                        eval_data = eval(eval_body)
                    self.file_data = self.file_data.replace(eval_f, eval_data)
                except Exception:
                    exceptions += 1
            if exceptions == len(all_eval_functions):
                raise Exception(
                    f"Exception: exceptions:{exceptions} == len(all_eval_functions):{len(all_eval_functions)}")

        root_search(list(set(list(CodeSearchAlgorithms.function(self.file_data, "eval")))))
        return self.file_data

    def zlib(self) -> str:
        return zlib.decompress(
            CodeSearchAlgorithms.object(self.file_data, bytes)
        ).decode(ENCODEING)

    def zlib_base64(self) -> str:
        return zlib.decompress(
            base64.b64decode(
                CodeSearchAlgorithms.object(self.file_data, str)
            )
        ).decode(ENCODEING)

    def codecs_bz2_codec(self) -> str:
        return codecs.decode(
            CodeSearchAlgorithms.object(self.file_data, bytes),
            "bz2_codec",
        ).decode(ENCODEING)

    def base16(self) -> str:
        return base64.b16decode(
            CodeSearchAlgorithms.object(self.file_data, bytes)
        ).decode(ENCODEING)

    def base32(self) -> str:
        return base64.b32decode(
            CodeSearchAlgorithms.object(self.file_data, bytes)
        ).decode(ENCODEING)

    def base64(self) -> str:
        try:
            return to_string(base64.b64decode(
                CodeSearchAlgorithms.object(self.file_data, bytes)
            ))
        except:
            return to_string(base64.b64decode(
                CodeSearchAlgorithms.object(self.file_data, str)
            ))

    def base85(self) -> str:
        return base64.b85decode(
            CodeSearchAlgorithms.object(self.file_data, bytes)
        ).decode(ENCODEING)

    def marshal(self) -> str:
        bytecode = marshal.loads(CodeSearchAlgorithms.object(self.file_data, bytes))
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return "\n".join(out.getvalue().split("\n")[4:]) + '\n'

    def machine_code(self) -> str:
        bytecode = marshal.loads(self.file_data[16:])
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        data = out.getvalue() + '\n'
        if self.file_data == data:
            raise Exception()
        return data

    def zip_code(self) -> str:
        with zipfile.ZipFile(self.file_data, "r") as zip_ref:
            for file in zip_ref.infolist():
                if file.filename == "__main__.py":
                    zip_ref.extract(file, ".")
                    with open(file.filename, "r") as f:
                        output = f.read()
                    os.remove(file.filename)
                    break
        return output

    def exec_function(self) -> str:
        def exec(*args):
            if args[0]:
                if type(args[0]) == str:
                    bytecode = OLD_COMPILE(args[0], "string", "exec")
                    commands = bytecode.co_consts
                    if len(commands) > 1:
                        self.custom_data = args[0]
                elif type(args[0]) == bytes:
                    bytecode = OLD_COMPILE(args[0], "string", "exec")
                    commands = bytecode.co_consts
                    if len(commands) > 1:
                        self.custom_data = to_string(args[0])
                elif hasattr(args[0], "co_code"):
                    self.custom_data = args[0]
            return args[0]

        def compile(*args):
            data = args[0]
            if type(data) == bytes:
                data = data.decode()
            return data

        def print(*args):
            pass

        def input(*args):
            return "text"

        try:
            OLD_EXEC(self.file_data)
        except Exception:
            pass

        if type(self.custom_data) == bytes:
            return self.custom_data.decode(ENCODEING)
        elif type(self.custom_data) == str:
            return self.custom_data

        bytecode = self.custom_data
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return "\n".join(out.getvalue().split("\n")[4:]) + '\n'

    def eval_function(self) -> str:
        def eval(*args):
            if args[0]:
                if type(args[0]) == str:
                    bytecode = OLD_COMPILE(args[0], "string", "exec")
                    commands = bytecode.co_consts
                    if len(commands) > 1:
                        self.custom_data = args[0]
                elif type(args[0]) == bytes:
                    bytecode = OLD_COMPILE(args[0], "string", "exec")
                    commands = bytecode.co_consts
                    if len(commands) > 1:
                        self.custom_data = to_string(args[0])
                elif hasattr(args[0], "co_code"):
                    self.custom_data = args[0]
            return args[0]

        def compile(*args):
            data = args[0]
            if type(data) == bytes:
                data = data.decode()
            return data

        def print(*args):
            pass

        def input(*args):
            return "text"

        try:
            OLD_EXEC(self.file_data)
        except Exception:
            pass

        if type(self.custom_data) == bytes:
            return self.custom_data.decode(ENCODEING)
        elif type(self.custom_data) == str:
            return self.custom_data

        bytecode = self.custom_data
        out = io.StringIO()
        version = PYTHON_VERSION if PYTHON_VERSION < 3.9 else 3.8
        decompile(version, bytecode, out, showast=False)
        return "\n".join(out.getvalue().split("\n")[4:]) + '\n'


def to_string(data) -> str:
    if type(data) == bytes:
        return data.decode(ENCODEING)
    else:
        return data