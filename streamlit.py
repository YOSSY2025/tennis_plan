"""Shim to run the real Streamlit app module without causing
an import name collision with the `streamlit` package.

This file intentionally avoids importing the `streamlit` package
so that running `streamlit run .\streamlit.py` will execute
`tennis_app_calendar.py` as the real app.
"""
import runpy
import os

_HERE = os.path.dirname(__file__)
runpy.run_path(os.path.join(_HERE, "tennis_app_calendar.py"), run_name="__main__")