import importlib
import pkgutil
import inspect
import traceback

from inspect import getmembers, isclass

from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

class Reflection:
    @staticmethod
    def get_all_subclasses_in_module(root_module, base_cls):
        results = []
            
        for _, module_path, is_pkg in pkgutil.walk_packages(root_module.__path__, f"{root_module.__name__}."):
            try:
                if is_pkg:
                    continue

                module = importlib.import_module(module_path)
                results.extend([cls for (_, cls) in getmembers(module) if isclass(cls) and issubclass(cls, base_cls)])
            except Exception as e:
                logger.error(f"{str(e)}, {traceback.print_exc()} module:{module_path}.")
        
        return results
    
    def get_cls(root_module, base_cls, name):
        all_limiter_cls = Reflection.get_all_subclasses_in_module(root_module, base_cls)
    
        for cls in all_limiter_cls:
            if name == cls.__name__:
                return cls
        return None
    
    @staticmethod
    def load_class_from_file(file_path, class_name):
        spec = importlib.util.spec_from_file_location("runtime_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        cls = getattr(module, class_name)
        return cls
    
    def load_subclasses_from_file(file_path, base_class):
        module_name = file_path.rstrip(".py").replace("/", "_")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        subclasses = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, base_class) and obj is not base_class:
                subclasses.append(obj)
        return subclasses