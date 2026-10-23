"""İSTEĞE BAĞLI: çekirdeği LangGraph akışına saran ince katman. Çekirdek (asyncio) LangGraph'a bağımlı değildir.
pip install langgraph  -> build_graph(model) -> .invoke({"contexts": [...]})
Düğümler: simulate -> validate -> (uyarı varsa) flag -> END."""
from __future__ import annotations
from typing import Any, TypedDict


class State(TypedDict, total=False):
    contexts: list[dict]
    dists: list[dict]
    agg: dict
    warnings: list[str]


def build_graph(model, real: dict | None = None, jsd_warn: float = 0.05):
    from langgraph.graph import StateGraph, END  # tembel import
    from decision_models import aggregate
    from validation import jsd

    async def simulate(s: State) -> State:
        d = await model.apredict(s["contexts"])
        return {"dists": d, "agg": aggregate(s["contexts"], d)}

    def validate(s: State) -> State:
        w = []
        if real:
            o = list(real)
            j = jsd([real[k] for k in o], [s["agg"][k] for k in o])
            if j > jsd_warn: w.append(f"JSD={j:.3f}")
        return {"warnings": w}

    g = StateGraph(State)
    g.add_node("simulate", simulate); g.add_node("validate", validate)
    g.set_entry_point("simulate"); g.add_edge("simulate", "validate"); g.add_edge("validate", END)
    return g.compile()
