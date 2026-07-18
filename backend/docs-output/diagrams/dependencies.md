# Module Dependencies

Which modules in this repo depend on which others.

```mermaid
graph LR
  api["api"]
  arch_explainer["arch_explainer"]
  diagram["diagram"]
  github_app["github_app"]
  index["index"]
  ingest["ingest"]
  publish["publish"]
  root["root"]
  scripts["scripts"]
  tests["tests"]
  understand["understand"]
  diagram --> arch_explainer
  diagram --> ingest
  index --> arch_explainer
  ingest --> arch_explainer
  publish --> arch_explainer
  scripts --> diagram
  scripts --> ingest
  scripts --> ingest
  scripts --> arch_explainer
  scripts --> publish
  scripts --> publish
  scripts --> understand
  scripts --> index
  tests --> diagram
  tests --> arch_explainer
  tests --> index
  tests --> ingest
  tests --> scripts
  tests --> index
  tests --> understand
  tests --> publish
  understand --> arch_explainer
```
