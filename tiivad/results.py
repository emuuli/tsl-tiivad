import json
from datetime import datetime

from tiivad.version import __version__


class Results(object):
    __instance = None
    pre_evaluate_error = None
    total_points = 0
    passed_points = 0
    tests = []

    def __new__(cls, val):
        if Results.__instance is None:
            Results.__instance = object.__new__(cls)
        if val is not None:
            Results.__instance.tests.append(val)
        return Results.__instance

    def __str__(cls):
        d = {
            "producer": f"tiivad {__version__}",
            "result_type": "OK_V3",
            "finished_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pre_evaluate_error": cls.pre_evaluate_error,
            "points": round(100 * cls.passed_points / cls.total_points) if cls.total_points > 0 else 0,
            "tests": cls.tests
        }
        return json.dumps(d, ensure_ascii=False)

    def clear(cls):
        cls.__instance = None
        cls.total_points = 0
        cls.passed_points = 0
        cls.tests = []
        cls.pre_evaluate_error = None


if __name__ == "__main__":
    Results.passed_points = 2
    Results.total_points = 3
    print(Results(1))
