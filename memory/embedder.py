import os
import logging
import threading
from collections import OrderedDict

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger(
    "huggingface_hub"
).setLevel(
    logging.ERROR
)

_model = None
_prewarm_started = False
_prewarm_lock = threading.Lock()

_embedding_cache = OrderedDict()


def _cache_limit():
    try:
        return max(16, min(4096, int(os.environ.get("MEMCODER_EMBED_CACHE_SIZE", "256"))))
    except (TypeError, ValueError):
        return 256


def get_model():

    global _model

    if _model is None:
        from transformers.utils import logging as transformers_logging
        from sentence_transformers import SentenceTransformer

        transformers_logging.set_verbosity_error()

        _model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    return _model


def is_warm():
    return _model is not None


def prewarm_async():
    """Warm semantic retrieval after a persistent host starts, never on its request path."""
    global _prewarm_started
    if os.environ.get("MEMCODER_PREWARM_SEMANTIC", "1").lower() in {"0", "false", "no"}:
        return False
    with _prewarm_lock:
        if _prewarm_started or is_warm():
            return False
        _prewarm_started = True

    def warm():
        try:
            get_model()
        except Exception:
            # Semantic search is optional; lexical retrieval remains available.
            pass

    threading.Thread(target=warm, name="memcoder-semantic-prewarm", daemon=True).start()
    return True


def embed(text):

    global _embedding_cache

    text = text.strip()

    if text in _embedding_cache:
        embedding = _embedding_cache.pop(text)
        _embedding_cache[text] = embedding
        return embedding

    model = get_model()

    embedding = model.encode(

        text,

        normalize_embeddings=True

    ).tolist()

    _embedding_cache[text] = embedding
    while len(_embedding_cache) > _cache_limit():
        _embedding_cache.popitem(last=False)

    return embedding
