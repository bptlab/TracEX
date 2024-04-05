"""Module providing logging decorators for analytic purposes."""
import ast
import time
import functools
import inspect
from logging import getLogger, INFO, FileHandler, Formatter

import pandas as pd


def log_execution_time(log_file_path):
    """Decorator to log the execution time of a function."""
    logger = setup_logger(
        "execution_time_logger", log_file_path, "%(asctime)s - %(message)s"
    )

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            file = inspect.getsourcefile(func)
            log_entry = {
                "function_name": func.__name__,
                "calling_file": file,
                "execution_time": f"{execution_time:.5f} seconds",
            }
            logger.info(log_entry)

            return result

        return wrapper

    return decorator


def log_tokens_used(log_file_path):
    """Decorator to log the tokens used in an API call to openAI."""
    logger = setup_logger("token_logger", log_file_path, "%(asctime)s - %(message)s")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)

            tokens_used = response.usage.total_tokens
            parent_calling_frame = inspect.stack()[2]
            log_entry = {
                "calling_function_name": parent_calling_frame[3],
                "calling_file": parent_calling_frame[1],
                "calling_line": parent_calling_frame[2],
                "tokens_used": tokens_used,
            }
            logger.info(log_entry)

            return response

        return wrapper

    return decorator


def setup_logger(logger_name, log_file_path, log_format):
    """Set up a logger with the given path and format."""
    logger = getLogger(logger_name)
    logger.setLevel(INFO)

    file_handler = FileHandler(log_file_path)
    formatter = Formatter(log_format)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger


def calculate_tokens_sum(log_file_path):
    """Calculate the sum of tokens used for each function in the given log file."""
    df = pd.read_csv(
        log_file_path,
        sep=" - ",
        engine="python",
        header=None,
        names=["timestamp", "message"],
    )
    df["message"] = df["message"].apply(ast.literal_eval)

    df["calling_function_name"] = df["message"].apply(
        lambda x: x.get("calling_function_name")
    )
    df["calling_file"] = df["message"].apply(lambda x: x.get("calling_file"))
    df["tokens_used"] = df["message"].apply(lambda x: x.get("tokens_used", 0))

    result_df = (
        df.groupby(["calling_function_name", "calling_file"])["tokens_used"]
        .sum()
        .reset_index()
    )

    return result_df
