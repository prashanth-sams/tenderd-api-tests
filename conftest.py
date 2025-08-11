# conftest.py
import time

def pytest_sessionstart(session):
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if tr is not None and not hasattr(tr, "_sessionstarttime"):
        tr._sessionstarttime = time.time()
