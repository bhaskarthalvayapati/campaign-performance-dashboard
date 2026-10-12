"""Read CSV data without any Streamlit dependency."""
import pandas as pd


def read_csv(source):
    try:
        return pd.read_csv(source)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError("Upload a nonempty, valid UTF-8 CSV file.") from exc
