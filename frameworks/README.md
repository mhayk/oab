# OAB Frameworks

Client-agnostic reasoning procedures. Each is an ordered set of steps with explicit inputs,
decision gates, and a required output artifact.

Knowing facts is not the same as reasoning well. `knowledge/` holds what is true about systems;
frameworks hold **how to use it** — and they are what makes OAB's behaviour reproducible rather
than emergent.

## The frameworks

| Framework | Answers |
| :-- | :-- |
| [`discovery/`](discovery/procedure.md) | What must we know before designing anything — and what can we skip asking? |
| [`capacity-planning/`](capacity-planning/procedure.md) | What are the actual numbers, and which one should we go and measure? |
| [`complexity-budget/`](complexity-budget/procedure.md) | Can this team carry this architecture? |
| [`architecture-design/`](architecture-design/procedure.md) | What should we build, and what did we refuse? |
| [`architecture-review/`](architecture-review/procedure.md) | What is wrong with what exists, given its actual scale? |
| [`evolution-triggers/`](evolution-triggers/procedure.md) | When does this decision expire? |

## Rules for every framework

1. **Client-agnostic.** No agent or model name. CI enforces this. An integration wraps a framework;
   it never contains one.
2. **Gates block.** A gate is a refusal to proceed, not a suggestion.
3. **Outputs are schema-valid.** Every framework names the artifact it produces and the schema it
   conforms to.
4. **Quantify or label.** No recommendation without a number, or an explicit "unquantified —
   provisional" marker.
5. **Name the file and the condition.** When a framework tells an agent to consult knowledge, it
   names which file and under what condition. "Consult the knowledge base" produces either nothing
   or everything.

## The eight hard rules

Every framework that produces a recommendation obeys these. They are what a model skips unless a
procedure forces it, and they are what produce proportionality.

| | Rule |
| :-- | :-- |
| R-A | No recommendation without a number, or an explicit provisional label |
| R-B | Every assumption appears in the output, with a confidence |
| R-C | Every option set includes the simplest viable option, even when rejected |
| R-D | Every significant decision carries at least one measurable trigger |
| R-E | Never introduce a component that appeared in no option |
| R-F | A stage-N system may not use stage-(N+2) machinery without a written override |
| R-G | State confidence honestly; low confidence recommends measurement before commitment |
| R-H | Cite the knowledge unit ids used |
