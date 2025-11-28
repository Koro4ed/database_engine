import time
from functools import wraps
from typing import Any, Callable

from database_engine.constants import ERROR_MESSAGES


def handle_db_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return f"Error: {ERROR_MESSAGES['table_not_exists']}"
        except KeyError as e:
            return f"Error: Column {e} not found"
        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    return wrapper


def confirm_action(action: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            confirmation = input(f"Are you sure you want to {action}? (y/N): ")
            if confirmation.lower() != "y":
                return "Action cancelled"
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time:.4f} seconds")
        return result

    return wrapper


def cache_results(func: Callable) -> Callable:
    cache = {}

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
