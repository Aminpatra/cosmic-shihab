"""Train FLARE's one model: how a FLEX droplet test ended, from what was set before it started.

    python3 -m pip install -r pipeline/requirements.txt
    python3 pipeline/train_flex_model.py      # writes backend/data/flex_model/results.json

Data: the 274 FLEX tests (PSI-69) in backend/data/runs/PSI-69.json. Target: PSI's "Test end"
(Extinction, Disruption, Completion). Inputs: only what was set before the test (fuel, pressure,
oxygen, CO2, helium, initial droplet diameter). What was measured during the test is left out,
because it would give the answer away.

Method, following CLAUDE.md:
- Split first. A fifth of the test days is held out before anything is fitted; every test of one
  day stays on one side, because a day's tests share a chamber fill.
- A majority-class baseline, a logistic regression and a random forest are compared by macro-F1
  in grouped cross-validation on the training days only (5 folds x REPEATS shuffles). The best is
  refitted on all training days and scored once on the held-out days, beside the baseline.
- Missing values (12 droplet diameters, one pressure of 0 mmHg read as missing) are filled with
  the training median inside each fit. Fixed seed; library versions are stored with the results.
- A chance check retrains the chosen model on shuffled labels (SHUFFLES times).
- SHAP explains the chosen model's predictions on the held-out tests.

This is a pattern in NASA's FLEX experiments, not a prediction of a real fire.

AI use: written with Claude Code (Claude Opus 5.5), reviewed by the team.
"""

from __future__ import annotations

import json
import math
import os
import platform
import re
import sys
from datetime import date

import numpy as np
import shap
import sklearn
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psi_client as psi  # noqa: E402  (save_atomic)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "backend", "data", "runs", "PSI-69.json")
OUT = os.path.join(ROOT, "backend", "data", "flex_model", "results.json")
SEED = 20261114
REPEATS = 5
SHUFFLES = 40  # for the chance check; the smallest p it can show is 1/41
CLASSES = ("Extinction", "Disruption", "Completion")
NOTICE = ("A pattern in NASA's FLEX droplet-combustion tests aboard the International Space "
          "Station. It is not a prediction of a real fire.")

# (feature, unit, PSI column it is read from)
FEATURES = (
    ("fuel_heptane", "1 = heptane, 0 = methanol", "Fuel"),
    ("pressure", "atm", "Ambient pressure; mmHg"),
    ("oxygen", "mole fraction", "O initial ambient composition; mole fraction"),
    ("co2", "mole fraction", "CO initial ambient composition; mole fraction"),
    ("helium", "mole fraction", "He initial ambient composition; mole fraction"),
    ("droplet_diameter", "mm", "Droplet initial diameter; mm"),
)
EXCLUDED = (
    ("Visible flame extinction diameter; mm", "measured during the test (an outcome)"),
    ("Burning rate; mm", "measured during the test (an outcome)"),
    ("Burn time; s", "measured during the test (an outcome)"),
    ("N initial ambient composition; mole fraction",
     "the balance gas, 1 minus the other three, so it adds nothing"),
    ("FLEX Test #, FLEX Identifier, Test GMT", "identifiers"),
    ("Test Date", "used only to keep each day's tests on one side of the split"),
)
OUTCOME_COLUMNS = {column for column, reason in EXCLUDED if "outcome" in reason}


def parse_date(text: str) -> str:
    """PSI writes both 3/5/2009 and 11/18/11; return ISO 8601."""
    month, day, year = (int(part) for part in re.fullmatch(r"(\d+)/(\d+)/(\d+)", text.strip()).groups())
    return date(year + 2000 if year < 100 else year, month, day).isoformat()


def _number(row: dict, column: str) -> float:
    cell = row["cells"].get(column, {})
    return float(cell["value"]) if cell.get("kind") == "number" and not cell.get("flags") else math.nan


def load_flex(path: str = RUNS):
    """(X, y, groups, test_numbers, notes). X has NaN where a value is missing."""
    with open(path, encoding="utf-8") as handle:
        rows = json.load(handle)["tables"][0]["rows"]
    X, y, groups, tests, zero_pressure = [], [], [], [], []
    for row in rows:
        fuel = row["cells"]["Fuel"]["raw"].strip().lower()
        if fuel not in ("methanol", "heptane"):
            raise ValueError(f"line {row['line']}: unexpected fuel {fuel!r}")
        pressure = _number(row, "Ambient pressure; mmHg") / 760  # PSI's mmHg, exact conversion
        test = int(_number(row, "FLEX Test #"))
        if pressure <= 0:  # 0 mmHg cannot hold a burning droplet: read as missing
            pressure = math.nan
            zero_pressure.append(test)
        X.append([1.0 if fuel == "heptane" else 0.0, pressure,
                  *(_number(row, column) for _, _, column in FEATURES[2:])])
        y.append(row["cells"]["Test end"]["raw"].strip())
        groups.append(parse_date(row["cells"]["Test Date"]["raw"]))
        tests.append(test)
    if set(y) != set(CLASSES):
        raise ValueError(f"unexpected test ends {sorted(set(y))}")
    notes = {"pressure_zero_read_as_missing": zero_pressure,
             "missing_droplet_diameter": int(sum(math.isnan(r[-1]) for r in X))}
    return np.array(X), np.array(y), np.array(groups), tests, notes


def split_days(y, groups, seed: int = SEED):
    """Hold out about a fifth of the test days, stratified by test end. (train_idx, test_idx)."""
    folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    return next(folds.split(np.zeros(len(y)), y, groups))


def candidates(seed: int = SEED) -> dict:
    return {
        "baseline": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": make_pipeline(
            SimpleImputer(strategy="median"), StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=5000, random_state=seed)),
        "random_forest": make_pipeline(
            SimpleImputer(strategy="median"),
            RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced",
                                   random_state=seed, n_jobs=1)),
    }


def macro_f1(y_true, y_pred) -> float:
    return float(f1_score(y_true, y_pred, labels=list(CLASSES), average="macro", zero_division=0))


def cv_scores(model, X, y, groups, seed: int = SEED, repeats: int = REPEATS) -> list[float]:
    scores = []
    for repeat in range(repeats):
        folds = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed + 1 + repeat)
        for train, test in folds.split(X, y, groups):
            fitted = clone(model).fit(X[train], y[train])
            scores.append(macro_f1(y[test], fitted.predict(X[test])))
    return scores


def held_out_report(y_true, y_pred) -> dict:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=list(CLASSES), zero_division=0)
    return {
        "macro_f1": round(macro_f1(y_true, y_pred), 3),
        "per_class": {c: {"precision": round(float(p), 3), "recall": round(float(r), 3),
                          "f1": round(float(f), 3), "tests": int(s)}
                      for c, p, r, f, s in zip(CLASSES, precision, recall, f1, support)},
        "confusion_matrix": {"rows_are": "actual", "columns_are": "predicted", "labels": list(CLASSES),
                             "matrix": confusion_matrix(y_true, y_pred, labels=list(CLASSES)).tolist()},
    }


def shap_summary(name: str, fitted, X_train, X_test) -> dict:
    """Per test end, each feature's mean |SHAP| on the held-out tests, and whether higher values
    push towards that end (correlation of value and SHAP above 0.3), away (below -0.3) or mixed."""
    prepare, model = fitted[:-1], fitted[-1]
    background, explained = prepare.transform(X_train), prepare.transform(X_test)
    if name == "random_forest":
        values = shap.TreeExplainer(model)(explained).values
    else:
        values = shap.LinearExplainer(model, background)(explained).values
    order = [list(model.classes_).index(c) for c in CLASSES]
    raw = fitted[0].transform(X_test)  # imputed but unscaled, for the direction
    summary = {}
    for k, class_name in zip(order, CLASSES):
        items = []
        for j, (feature, _, _) in enumerate(FEATURES):
            contribution = values[:, j, k]
            spread = np.std(raw[:, j]) * np.std(contribution)
            corr = float(np.corrcoef(raw[:, j], contribution)[0, 1]) if spread > 0 else 0.0
            items.append({"feature": feature, "mean_abs_shap": round(float(np.mean(np.abs(contribution))), 4),
                          "direction": "toward" if corr > 0.3 else "away" if corr < -0.3 else "mixed"})
        summary[class_name] = sorted(items, key=lambda item: -item["mean_abs_shap"])
    return summary


def chance_check(model, X, y, groups, seed: int = SEED, shuffles: int = SHUFFLES) -> dict:
    """Is the model better than chance? Its grouped-CV macro-F1 against the same model trained on
    labels shuffled across all tests (shuffling within days would keep each day's atmosphere
    tied to its labels and flatter chance)."""
    real = float(np.mean(cv_scores(model, X, y, groups, seed, repeats=1)))
    rng = np.random.default_rng(seed)
    null = [float(np.mean(cv_scores(model, X, rng.permutation(y), groups, seed, repeats=1)))
            for _ in range(shuffles)]
    return {"method": "labels shuffled across all tests; same grouped 5-fold split", "on": "training days",
            "shuffles": shuffles, "macro_f1": round(real, 3),
            "shuffled_mean": round(float(np.mean(null)), 3), "shuffled_max": round(float(np.max(null)), 3),
            "p_value": round((1 + sum(n >= real for n in null)) / (1 + shuffles), 3),
            "smallest_possible_p": round(1 / (1 + shuffles), 3)}


def limitations(result: dict) -> list[str]:
    """Caveats written from the numbers, so they change when the results do."""
    chosen, split = result["chosen_model"], result["split"]
    report, cv = result["held_out"], result["cross_validation"]["scores"]
    found = {c: report[chosen]["confusion_matrix"]["matrix"][k][k] for k, c in enumerate(CLASSES)}
    notes = [
        f"Held out: {split['held_out_tests']} tests on {split['held_out_days']} days, so one test "
        f"moves a class score a lot; cross-validation on the training days varies by "
        f"±{cv[chosen]['sd']} macro-F1.",
        f"On the held-out days the {chosen.replace('_', ' ')} found {found['Completion']} of "
        f"{split['held_out_tests_by_end']['Completion']} completions, {found['Disruption']} of "
        f"{split['held_out_tests_by_end']['Disruption']} disruptions and {found['Extinction']} of "
        f"{split['held_out_tests_by_end']['Extinction']} extinctions.",
        "SHAP describes what the model relies on, not what causes a flame to go out.",
        "Methanol and heptane droplets in FLEX's chamber only; nothing here carries over to other "
        "fuels, materials or a spacecraft cabin.",
    ]
    better = [n for n in report if n not in ("baseline", chosen) and report[n]["macro_f1"] > report[chosen]["macro_f1"]]
    if better:
        notes.insert(1, f"{', '.join(b.replace('_', ' ') for b in better)} scored higher on the held-out "
                        f"days; the choice was made beforehand, on cross-validation, and is kept.")
    return notes


def train(seed: int = SEED, repeats: int = REPEATS, path: str = RUNS, shuffles: int = SHUFFLES) -> dict:
    X, y, groups, tests, notes = load_flex(path)
    train_idx, test_idx = split_days(y, groups, seed)
    models = candidates(seed)
    cv = {name: cv_scores(model, X[train_idx], y[train_idx], groups[train_idx], seed, repeats)
          for name, model in models.items()}
    chosen = max((n for n in models if n != "baseline"), key=lambda n: np.mean(cv[n]))
    held_out, fitted_models = {}, {}
    for name, model in models.items():
        fitted_models[name] = clone(model).fit(X[train_idx], y[train_idx])
        held_out[name] = held_out_report(y[test_idx], fitted_models[name].predict(X[test_idx]))
    counts = {c: int((y == c).sum()) for c in CLASSES}
    result = {
        "notice": NOTICE,
        "question": "How did a FLEX droplet test end (Extinction, Disruption, Completion), "
                    "given only what was set before it?",
        "source": {"accession": "PSI-69", "file": "PSI-69_Experimental table_FLEX.csv",
                   "read_from": "backend/data/runs/PSI-69.json"},
        "classes": list(CLASSES),
        "features": [{"name": n, "unit": u, "psi_column": c} for n, u, c in FEATURES],
        "excluded": [{"psi_column": c, "reason": r} for c, r in EXCLUDED],
        "data": {"tests": len(y), "test_days": len(set(groups)), "tests_by_end": counts, **notes},
        "split": {"method": "StratifiedGroupKFold by test day, one fold of five held out",
                  "train_tests": len(train_idx), "held_out_tests": len(test_idx),
                  "train_days": len(set(groups[train_idx])), "held_out_days": len(set(groups[test_idx])),
                  "held_out_tests_by_end": {c: int((y[test_idx] == c).sum()) for c in CLASSES}},
        "cross_validation": {
            "on": "training days only", "folds": 5, "repeats": repeats, "metric": "macro-F1",
            "scores": {n: {"mean": round(float(np.mean(s)), 3), "sd": round(float(np.std(s)), 3),
                           "min": round(float(np.min(s)), 3), "max": round(float(np.max(s)), 3)}
                       for n, s in cv.items()}},
        "chosen_model": chosen,
        "chosen_because": "highest mean cross-validated macro-F1 on the training days",
        "held_out": held_out,
        "chance_check": chance_check(models[chosen], X[train_idx], y[train_idx], groups[train_idx],
                                     seed, shuffles),
        "shap": {"model": chosen, "explained": "held-out tests",
                 "by_end": shap_summary(chosen, fitted_models[chosen], X[train_idx], X[test_idx])},
        "reproduce": {"command": "python3 pipeline/train_flex_model.py", "seed": seed,
                      "python": platform.python_version(), "scikit_learn": sklearn.__version__,
                      "shap": shap.__version__, "numpy": np.__version__},
    }
    result["limitations"] = limitations(result)
    return result


def main() -> None:
    result = train()
    psi.save_atomic(OUT, (json.dumps(result, indent=2) + "\n").encode("utf-8"))
    cv = result["cross_validation"]["scores"]
    print(f"{result['data']['tests']} tests on {result['data']['test_days']} days; "
          f"held out {result['split']['held_out_tests']} tests on {result['split']['held_out_days']} days")
    for name in cv:
        mark = " (chosen)" if name == result["chosen_model"] else ""
        print(f"  {name:20} CV macro-F1 {cv[name]['mean']:.3f} ± {cv[name]['sd']:.3f}   "
              f"held-out macro-F1 {result['held_out'][name]['macro_f1']:.3f}{mark}")
    print(f"wrote {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
