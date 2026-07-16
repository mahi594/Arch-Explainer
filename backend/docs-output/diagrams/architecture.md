# System Architecture

High-level view of modules and their key external dependencies.

```mermaid
graph TD
  api["api"]
  arch_explainer_models["arch_explainer.models"]
  diagram["diagram"]
  github_app["github_app"]
  index["index"]
  ingest_parser["ingest.parser"]
  publish["publish"]
  root["root"]
  scripts["scripts"]
  tests["tests"]
  understand["understand"]
  ext_PyGithub_inferred_for_GitHub_API_client(["PyGithub (inferred for GitHub API client)"])
  ext_arch_explainer_diagram_generator(["arch_explainer.diagram.generator"])
  ext_arch_explainer_index_embedder(["arch_explainer.index.embedder"])
  ext_arch_explainer_index_store(["arch_explainer.index.store"])
  ext_arch_explainer_ingest_parser(["arch_explainer.ingest.parser"])
  ext_arch_explainer_publish_writer(["arch_explainer.publish.writer"])
  ext_arch_explainer_understand_summarizer(["arch_explainer.understand.summarizer"])
  ext_argparse(["argparse"])
  ext_ast(["ast"])
  ext_collections(["collections"])
  ext_dataclasses(["dataclasses"])
  ext_datetime(["datetime"])
  ext_dotenv(["dotenv"])
  ext_enum(["enum"])
  ext_fastapi_inferred_for_webhooks(["fastapi (inferred for webhooks)"])
  ext_google_genai(["google.genai"])
  ext_hashlib(["hashlib"])
  ext_json(["json"])
  ext_logging_inferred_for_operational_logging(["logging (inferred for operational logging)"])
  ext_os(["os"])
  ext_os_inferred_for_environment_variables(["os (inferred for environment variables)"])
  ext_pathlib(["pathlib"])
  ext_psycopg(["psycopg"])
  ext_psycopg_pool(["psycopg_pool"])
  ext_pydantic(["pydantic"])
  ext_pytest(["pytest"])
  ext_python_jose_inferred_for_JWT_handling(["python-jose (inferred for JWT handling)"])
  ext_re(["re"])
  ext_requests_inferred_for_API_calls(["requests (inferred for API calls)"])
  ext_run_pipeline(["run_pipeline"])
  ext_sentence_transformers(["sentence_transformers"])
  ext_sqlite3(["sqlite3"])
  ext_sys(["sys"])
  ext_time(["time"])
  ext_typing(["typing"])
  arch_explainer_models -->|uses| ext_datetime
  arch_explainer_models -->|uses| ext_enum
  arch_explainer_models -->|uses| ext_typing
  arch_explainer_models -->|uses| ext_pydantic
  diagram -->|uses| ext_re
  diagram -->|imports| arch_explainer_models
  github_app -->|uses| ext_fastapi_inferred_for_webhooks
  github_app -->|uses| ext_python_jose_inferred_for_JWT_handling
  github_app -->|uses| ext_requests_inferred_for_API_calls
  github_app -->|uses| ext_PyGithub_inferred_for_GitHub_API_client
  github_app -->|uses| ext_os_inferred_for_environment_variables
  github_app -->|uses| ext_logging_inferred_for_operational_logging
  index -->|imports| arch_explainer_models
  index -->|uses| ext_hashlib
  index -->|uses| ext_json
  index -->|uses| ext_sqlite3
  index -->|uses| ext_time
  index -->|uses| ext_pathlib
  index -->|uses| ext_typing
  index -->|uses| ext_dataclasses
  index -->|uses| ext_google_genai
  index -->|uses| ext_sentence_transformers
  index -->|uses| ext_psycopg_pool
  index -->|uses| ext_psycopg
  ingest_parser -->|imports| arch_explainer_models
  ingest_parser -->|uses| ext_ast
  ingest_parser -->|uses| ext_hashlib
  publish -->|uses| ext_re
  publish -->|uses| ext_pathlib
  publish -->|imports| arch_explainer_models
  root -->|uses| ext_time
  root -->|uses| ext_psycopg
  root -->|uses| ext_psycopg_pool
  scripts -->|uses| ext_os
  scripts -->|uses| ext_sys
  scripts -->|uses| ext_pathlib
  scripts -->|uses| ext_argparse
  scripts -->|uses| ext_hashlib
  scripts -->|uses| ext_dotenv
  scripts -->|uses| ext_psycopg
  scripts -->|uses| ext_arch_explainer_diagram_generator
  scripts -->|uses| ext_arch_explainer_ingest_parser
  scripts -->|imports| arch_explainer_models
  scripts -->|uses| ext_arch_explainer_publish_writer
  scripts -->|uses| ext_arch_explainer_understand_summarizer
  scripts -->|uses| ext_arch_explainer_index_embedder
  tests -->|uses| ext_pytest
  tests -->|uses| ext_pathlib
  tests -->|uses| ext_json
  tests -->|uses| ext_os
  tests -->|uses| ext_sys
  tests -->|uses| ext_arch_explainer_diagram_generator
  tests -->|imports| arch_explainer_models
  tests -->|uses| ext_arch_explainer_index_embedder
  tests -->|uses| ext_arch_explainer_ingest_parser
  tests -->|uses| ext_run_pipeline
  tests -->|uses| ext_arch_explainer_index_store
  tests -->|uses| ext_arch_explainer_understand_summarizer
  tests -->|uses| ext_arch_explainer_publish_writer
  understand -->|imports| arch_explainer_models
  understand -->|uses| ext_pydantic
  understand -->|uses| ext_google_genai
  understand -->|uses| ext_sqlite3
  understand -->|uses| ext_hashlib
  understand -->|uses| ext_json
  understand -->|uses| ext_time
  understand -->|uses| ext_collections
  understand -->|uses| ext_pathlib
  understand -->|uses| ext_typing
  classDef moduleNode fill:#0ea5e9,color:#fff,stroke:#0369a1,stroke-width:2px;
  class api,arch_explainer_models,diagram,github_app,index,ingest_parser,publish,root,scripts,tests,understand moduleNode;
  classDef externalNode fill:#6b7280,color:#fff,stroke:#374151,stroke-width:1px;
  class ext_PyGithub_inferred_for_GitHub_API_client,ext_arch_explainer_diagram_generator,ext_arch_explainer_index_embedder,ext_arch_explainer_index_store,ext_arch_explainer_ingest_parser,ext_arch_explainer_publish_writer,ext_arch_explainer_understand_summarizer,ext_argparse,ext_ast,ext_collections,ext_dataclasses,ext_datetime,ext_dotenv,ext_enum,ext_fastapi_inferred_for_webhooks,ext_google_genai,ext_hashlib,ext_json,ext_logging_inferred_for_operational_logging,ext_os,ext_os_inferred_for_environment_variables,ext_pathlib,ext_psycopg,ext_psycopg_pool,ext_pydantic,ext_pytest,ext_python_jose_inferred_for_JWT_handling,ext_re,ext_requests_inferred_for_API_calls,ext_run_pipeline,ext_sentence_transformers,ext_sqlite3,ext_sys,ext_time,ext_typing externalNode;
```
