from Tracker import db
import pytest
import contextlib


@pytest.fixture(scope="function", autouse=True)
def do_something(request):
    meta = db.metadata

    with contextlib.closing(db.engine.connect()) as con:
        trans = con.begin()
        for table in reversed(meta.sorted_tables):
            con.execute(table.delete())
        trans.commit()
    print("flushed")
