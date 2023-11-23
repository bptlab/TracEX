"""Module providing a function to access and query prompts of a database."""

import sqlite3


def get_prompt(prompt, prompt_mode):
    """Opens the database."""
    # Connect to database
    conn = sqlite3.connect("tracex.db")
    cur = conn.cursor()

    data = cur.execute(
        "SELECT prompt_content FROM prompts WHERE prompt_key = '"
        + prompt
        + "_"
        + prompt_mode
        + "';"
    ).fetchone()[0]

    # Close database
    cur.close()
    conn.close()
    return data
