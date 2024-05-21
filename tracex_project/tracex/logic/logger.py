"""
Provide decorators to log the execution time and OPENAI API key tokens used by a function.

The .log files are appended each time with the execution of a decorated function. The logged information contains
parameters with the execution time and tokens used by the function depending on the logger. Each log entry contains
a timestamp of the invocation and a JSON object with the logged information. The following information is logged:
calling function name, calling file, calling line and depending on the logger, either execution time or tokens used,
input tokens used and output tokens used.

Functions:
log_execution_time -- Decorator to log the execution time of a function.
log_tokens_used -- Decorator to log the tokens used in an API call to the OPENAI API.
"""
import ast
import time
import functools
import inspect
from logging import getLogger, INFO, FileHandler, Formatter

import pandas as pd


def log_execution_time(log_file_path):
    """
    Decorate a function to log the execution time.

    Create a .log file and reference it in the decorator to log the execution time of the decorated function.

    Positional Arguments:
    log_file_path -- Path to a .log file. An error occurs if the file does not exist when calling a decorated function.
    """
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
    """
    Decorate a function to log the OPENAI API key tokens used.

    Create a .log file and reference it in the decorator to log the OPENAI API key tokens of the decorated function.

    Positional Arguments:
    log_file_path -- Path to a .log file. An error occurs if the file does not exist when calling a decorated function.
    """
    logger = setup_logger("token_logger", log_file_path, "%(asctime)s - %(message)s")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)

            tokens_used = response.usage.total_tokens
            input_tokens_used = response.usage.prompt_tokens
            output_tokens_used = response.usage.completion_tokens
            parent_calling_frame = inspect.stack()[2]
            log_entry = {
                "calling_function_name": parent_calling_frame[3],
                "calling_file": parent_calling_frame[1],
                "calling_line": parent_calling_frame[2],
                "tokens_used": tokens_used,
                "input_tokens_used": input_tokens_used,
                "output_tokens_used": output_tokens_used,
            }
            logger.info(log_entry)

            return response

        return wrapper

    return decorator


def setup_logger(logger_name, log_file_path, log_format):
    """Set up a logger at specified file path and format."""
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
