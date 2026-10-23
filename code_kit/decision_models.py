"""Karar modelleri: ortak arayüz `DecisionModel.predict(contexts) -> list[Dist]`.
Üç uygulama: LLMPersonaModel (async), RuleModel (kural/utility), MLModel (sklearn).
Dist = {seçenek: olasılık}, toplamı 1. Context = {"persona": dict, "stimulus": str, "options": [str], ...}"""
from __future__ import annotations
import abc, asyncio, hashlib, json, math, os, random, re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

Dist = dict[str, float]
Context = dict


def normalize(d: Dist, options: list[str], eps: float = 1e-9) -> Dist:
    v = np.array([max(float(d.get(o, 0.0)), 0.0) for o in options]) + eps
    v = v / v.sum()
    return {o: float(p) for o, p in zip(options, v)}


class DecisionModel(abc.ABC):
    name = "base"

    @abc.abstractmethod
    async def apredict(self, contexts: list[Context]) -> list[Dist]: ...

    def predict(self, contexts: list[Context]) -> list[Dist]:
        return asyncio.run(self.apredict(contexts))


def load_env(path: str | None = None) -> None:
    """Proje kökündeki .env'i (KEY=VALUE) os.environ'a yükler; mevcut değişkenlerin üzerine yazmaz."""
    p = Path(path) if path else next((d / ".env" for d in Path(__file__).resolve().parents if (d / ".env").exists()), None)
    if not p or not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------------------------------------------------------------- sağlayıcılar
@dataclass
class Completion:
    text: str
    logprobs: list[dict[str, float]] | None = None  # ilk token için {token: logprob}; yoksa None


class LLMProvider(abc.ABC):
    name = "provider"
    supports_logprobs = False  # DESTEĞİ VARSAYMA; sağlayıcı açıkça True yapar

    @abc.abstractmethod
    async def complete(self, prompt: str, *, temperature: float = 1.0, max_tokens: int = 200,
                       logprobs: bool = False) -> Completion: ...


class MockProvider(LLMProvider):
    """Deterministik sahte LLM. Fiyat/yaş ipuçlarına duyarlı + gürültü; `fail_rate` ile hata enjekte edilir.
    Amaç: boru hattını ve test/demo'yu API'siz çalıştırmak. Çıktılar GERÇEK DAVRANIŞ DEĞİLDİR."""
    name = "mock"
    supports_logprobs = True

    def __init__(self, fail_rate: float = 0.0, latency: float = 0.0, seed: int = 0, mode_collapse: float = 0.0):
        self.fail_rate, self.latency, self.seed, self.mode_collapse = fail_rate, latency, seed, mode_collapse
        self.calls = 0

    def _probs(self, prompt: str) -> list[float]:
        opts = re.findall(r"^[A-Z]\) (.+)$", prompt, re.M)
        price = re.search(r"price=([\d.]+)", prompt)
        price = float(price.group(1)) if price else 50.0
        h = int(hashlib.sha256(prompt.encode()).hexdigest()[:8], 16)
        rng = random.Random(h + self.seed)
        n = max(len(opts), 2)
        base = np.array([1.0 + 2.0 * (i == 0) * max(0.0, (80 - price) / 80) + rng.random() * 0.3 for i in range(n)])
        if self.mode_collapse:
            base[0] += self.mode_collapse * 10
        return list(base / base.sum())

    async def complete(self, prompt, *, temperature=1.0, max_tokens=200, logprobs=False):
        self.calls += 1
        if self.latency:
            await asyncio.sleep(self.latency)
        if random.random() < self.fail_rate:
            raise RuntimeError("mock transient failure")
        p = self._probs(prompt)
        opts = re.findall(r"^[A-Z]\) (.+)$", prompt, re.M)
        if "JSON_PROBS" in prompt:
            return Completion(json.dumps({o: round(x, 3) for o, x in zip(opts, p)}))
        # tek seçim: temperature ile örnekle
        rng = random.Random(hash((prompt, self.calls)) if temperature > 0 else 0)
        idx = int(np.argmax(p)) if temperature == 0 else rng.choices(range(len(p)), weights=p)[0]
        lp = [{chr(65 + i): math.log(p[i]) for i in range(len(opts))}] if logprobs else None
        return Completion(chr(65 + idx) if opts else "?", lp)


class AnthropicProvider(LLMProvider):
    """Anthropic Messages API. Logprobs DESTEKLENMEZ -> multi_sample veya verbal kullan."""
    name = "anthropic"
    supports_logprobs = False

    def __init__(self, model: str = "claude-sonnet-5-5"):
        import anthropic  # tembel import (paket yoksa burada hata verir)
        self.model, self._loop, self._client = model, None, None

    @property
    def client(self):
        import anthropic
        loop = asyncio.get_running_loop()
        if self._client is None or loop is not self._loop:
            self._client, self._loop = anthropic.AsyncAnthropic(), loop
        return self._client

    async def complete(self, prompt, *, temperature=1.0, max_tokens=200, logprobs=False):
        r = await self.client.messages.create(model=self.model, max_tokens=max_tokens, temperature=temperature,
                                              messages=[{"role": "user", "content": prompt}])
        return Completion("".join(b.text for b in r.content if getattr(b, "type", "") == "text"))


class OpenAIProvider(LLMProvider):
    """OpenAI Chat Completions. Logprobs bazı modellerde var; hata verirse strateji düşer."""
    name = "openai"
    supports_logprobs = True  # model bağımlı; llm_dist hata yakalayıp multi_sample'a düşer

    def __init__(self, model: str = "gpt-4o-mini"):
        import openai
        load_env()
        self._key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_KEY")
        self.model, self._loop, self._client = model, None, None

    @property
    def client(self):
        """predict() her çağrıda yeni event loop açar; istemci loop'a bağlı olduğundan loop değişince yeniden kurulur."""
        import openai
        loop = asyncio.get_running_loop()
        if self._client is None or loop is not self._loop:
            self._client, self._loop = openai.AsyncOpenAI(api_key=self._key), loop
        return self._client

    async def complete(self, prompt, *, temperature=1.0, max_tokens=200, logprobs=False):
        kw = dict(model=self.model, temperature=temperature, max_tokens=max_tokens,
                  messages=[{"role": "user", "content": prompt}])
        if logprobs:
            kw.update(logprobs=True, top_logprobs=20)
        r = await self.client.chat.completions.create(**kw)
        ch = r.choices[0]
        lp = None
        if logprobs and ch.logprobs and ch.logprobs.content:
            lp = [{t.token: t.logprob for t in ch.logprobs.content[0].top_logprobs}]
        return Completion(ch.message.content or "", lp)


# ---------------------------------------------------------------- disk cache
class DiskCache:
    def __init__(self, directory: str = ".llm_cache"):
        self.dir = Path(directory); self.dir.mkdir(parents=True, exist_ok=True)

    def _p(self, key: str) -> Path:
        return self.dir / (hashlib.sha256(key.encode()).hexdigest() + ".json")

    def get(self, key: str):
        p = self._p(key)
        return json.loads(p.read_text()) if p.exists() else None

    def set(self, key: str, value) -> None:
        self._p(key).write_text(json.dumps(value))


# ---------------------------------------------------------------- LLM persona modeli
def build_prompt(ctx: Context, style: str) -> str:
    """Seçenekler harf etiketli (A, B, ...): ilk-token çakışmasını (Al/Alma) önler, logprobs için tek token verir."""
    persona = "; ".join(f"{k}={v}" for k, v in ctx.get("persona", {}).items())
    opts = "\n".join(f"{chr(65 + i)}) {o}" for i, o in enumerate(ctx["options"]))
    head = f"Sen şu kişisin: {persona}.\nDurum: {ctx['stimulus']}\nSeçenekler:\n{opts}\n"
    if style == "verbal":
        names = ", ".join(f'"{o}"' for o in ctx["options"])
        return head + (f"JSON_PROBS: Bu kişinin her seçeneği seçme olasılığını JSON olarak ver (toplam 1). "
                       f"Anahtarlar tam olarak şunlar olsun: {names}. Sadece JSON.")
    return head + "Bu kişi hangisini seçer? Sadece seçeneğin harfini yaz (örn. A)."


class LLMPersonaModel(DecisionModel):
    """strategy: 'verbal' (sözlü olasılık, 1 çağrı) | 'multi_sample' (n örnek, ampirik) | 'logprobs' (varsa; yoksa düşer)."""
    name = "llm_persona"

    def __init__(self, provider: LLMProvider, strategy: str = "multi_sample", n_samples: int = 8,
                 temperature: float = 1.0, concurrency: int = 8, retries: int = 3, backoff: float = 0.5,
                 cache: DiskCache | None = None, batch_size: int = 64, smoothing: float = 0.5):
        self.p, self.strategy, self.n = provider, strategy, n_samples
        self.temp, self.sem = temperature, None
        self.concurrency, self.retries, self.backoff = concurrency, retries, backoff
        self.cache, self.batch_size, self.smoothing = cache, batch_size, smoothing
        self.stats = Counter()

    async def _call(self, prompt: str, tag: str, **kw) -> Completion | None:
        key = f"{self.p.name}|{getattr(self.p, 'model', '')}|{tag}|{kw}|{prompt}"
        if self.cache and (hit := self.cache.get(key)) is not None:
            self.stats["cache_hit"] += 1
            return Completion(hit["text"], hit.get("lp"))
        for attempt in range(self.retries + 1):
            try:
                async with self.sem:
                    c = await self.p.complete(prompt, **kw)
                self.stats["calls"] += 1
                if self.cache:
                    self.cache.set(key, {"text": c.text, "lp": c.logprobs})
                return c
            except Exception:
                self.stats["errors"] += 1
                if attempt == self.retries:
                    self.stats["gave_up"] += 1
                    return None
                await asyncio.sleep(self.backoff * 2 ** attempt * (0.5 + random.random()))

    @staticmethod
    def _match(text: str, options: list[str]) -> str | None:
        t = text.strip().lower()
        if t[:1].isalpha() and (len(t) == 1 or not t[1].isalpha()):  # "A", "A)", "a."
            i = ord(t[0]) - 97
            if 0 <= i < len(options):
                return options[i]
        for o in options:
            if t == o.lower():
                return o
        hits = [o for o in options if o.lower() in t]
        return hits[0] if len(hits) == 1 else None

    async def _one(self, ctx: Context) -> Dist:
        opts = ctx["options"]
        uniform = {o: 1 / len(opts) for o in opts}
        strat = self.strategy
        if strat == "logprobs" and not self.p.supports_logprobs:
            strat = "multi_sample"; self.stats["fallback_logprobs"] += 1
        if strat == "verbal":
            c = await self._call(build_prompt(ctx, "verbal"), "verbal", temperature=self.temp)
            if c:
                m = re.search(r"\{.*\}", c.text, re.S)
                try:
                    return normalize(json.loads(m.group(0)), opts)
                except Exception:
                    self.stats["parse_fail"] += 1
            return uniform
        if strat == "logprobs":
            c = await self._call(build_prompt(ctx, "choice"), "lp", temperature=0.0, logprobs=True)
            if c and c.logprobs:
                lp = c.logprobs[0]
                d: Dist = {}
                for t, v in lp.items():  # "A" ve " A" gibi varyantlar toplanır
                    t = t.strip().upper()
                    if len(t) == 1 and 0 <= ord(t) - 65 < len(opts):
                        d[opts[ord(t) - 65]] = d.get(opts[ord(t) - 65], 0.0) + math.exp(v)
                if d:
                    return normalize(d, opts)
            self.stats["lp_fail"] += 1
            strat = "multi_sample"
        cs = await asyncio.gather(*[self._call(build_prompt(ctx, "choice"), f"s{i}", temperature=self.temp)
                                    for i in range(self.n)])
        cnt = Counter(m for c in cs if c and (m := self._match(c.text, opts)))
        if not cnt:
            return uniform
        return normalize({o: cnt.get(o, 0) + self.smoothing for o in opts}, opts, eps=0)

    async def apredict(self, contexts: list[Context]) -> list[Dist]:
        self.sem = asyncio.Semaphore(self.concurrency)
        out: list[Dist] = []
        for i in range(0, len(contexts), self.batch_size):
            out += await asyncio.gather(*[self._one(c) for c in contexts[i:i + self.batch_size]])
        return out


# ---------------------------------------------------------------- kural tabanlı
class RuleModel(DecisionModel):
    """utility_fn(ctx, option) -> float; softmax(beta * u). Kurallar belliyse LLM'siz baz çözüm."""
    name = "rule"

    def __init__(self, utility_fn, beta: float = 1.0):
        self.u, self.beta = utility_fn, beta

    async def apredict(self, contexts):
        out = []
        for c in contexts:
            u = np.array([self.u(c, o) for o in c["options"]]) * self.beta
            e = np.exp(u - u.max())
            out.append({o: float(p) for o, p in zip(c["options"], e / e.sum())})
        return out


# ---------------------------------------------------------------- istatistik/ML
class MLModel(DecisionModel):
    """sklearn sınıflandırıcı. feature_fn(ctx, option)->dict özellikleri; ikili satın al/alma ('seç' sınıfı = 1)
    öğrenilir, seçenekler arasında normalize edilir (conditional-logit benzeri kaba yaklaşım)."""
    name = "ml"

    def __init__(self, feature_fn, estimator=None):
        from sklearn.linear_model import LogisticRegression
        self.f = feature_fn
        self.est = estimator or LogisticRegression(max_iter=1000)
        self.cols: list[str] = []

    def fit(self, contexts: list[Context], chosen: list[str]):
        rows, y = [], []
        for c, ch in zip(contexts, chosen):
            for o in c["options"]:
                rows.append(self.f(c, o)); y.append(int(o == ch))
        self.cols = sorted(rows[0])
        self.est.fit(np.array([[r[k] for k in self.cols] for r in rows]), y)
        return self

    async def apredict(self, contexts):
        out = []
        for c in contexts:
            X = np.array([[self.f(c, o)[k] for k in self.cols] for o in c["options"]])
            p = self.est.predict_proba(X)[:, 1]
            out.append(normalize({o: v for o, v in zip(c["options"], p)}, c["options"]))
        return out


def aggregate(contexts: list[Context], dists: list[Dist], weights=None) -> Dist:
    """Popülasyon dağılımı = (ağırlıklı) ortalama bireysel dağılım (dağılım-öncelikli: örnekleme gürültüsü yok)."""
    opts = contexts[0]["options"]
    w = np.ones(len(dists)) if weights is None else np.asarray(weights, float)
    return {o: float(np.average([d[o] for d in dists], weights=w)) for o in opts}
