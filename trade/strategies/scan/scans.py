from typing import TypeVar, Dict, Any
from pathlib import Path
import sys
import inspect
import importlib.util as import_util


CURR_DIR = Path(__file__).parent
T = TypeVar("T")


class ScanStocks:

    @classmethod
    def execute_scans(cls, strategy: str, data, top: int = None):

        scan_obj = cls(strategy)
        return scan_obj.execute_modules(data, top)

    def __init__(self, strategy: str):

        self.strategy_path = self.check_curr_strategies(strategy)

    def check_curr_strategies(self, strategy) -> Path:
        strategy_path = CURR_DIR / Path(strategy)
        if strategy_path.exists():
            return strategy_path

        raise ValueError("Invalid Strategy name.")

    def get_modules(self):

        python_files = [f for f in self.strategy_path.iterdir()
                        if f.suffix == ".py"]
        modules_ = []
        for file in python_files:
            module_name = file.stem
            file_path = file

            spec = import_util.spec_from_file_location(module_name, file_path)
            module = import_util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name:
                    if obj.ENABLED:
                        modules_.append(obj)

        return modules_

    def instantiate_scans(self, data, top: int) -> Dict[str, Any]:
        modules = self.get_modules()
        return {i.__name__: i(data, top) for i in modules}

    def execute_modules(self, data, top: int = None):
        modules = self.instantiate_scans(data, top)
        return {name: mod.strategy_output() for name, mod in modules.items()}
