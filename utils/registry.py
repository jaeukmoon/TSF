import importlib
import importlib.util
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"


def load_model(name):
    """models/<name>/predict.py 에서 forecast 함수를 로드."""
    path = MODELS_DIR / name / "predict.py"
    if not path.exists():
        raise FileNotFoundError(f"{path} 없음. models/{name}/predict.py 에 forecast() 구현 필요.")
    spec = importlib.util.spec_from_file_location(f"tsf_models.{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "forecast"):
        raise AttributeError(f"models/{name}/predict.py 에 forecast() 함수 필요.")
    return mod.forecast


def list_models():
    return sorted([p.name for p in MODELS_DIR.iterdir() if (p / "predict.py").exists()])
