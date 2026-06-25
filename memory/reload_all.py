import importlib
import pkgutil
import memory


def reload_all():

    count = 0

    for _, module_name, _ in pkgutil.iter_modules(memory.__path__):

        if module_name == "reload_all":
            continue

        module = importlib.import_module(
            f"memory.{module_name}"
        )

        importlib.reload(module)

        count += 1

    print(f"Reloaded {count} modules.")