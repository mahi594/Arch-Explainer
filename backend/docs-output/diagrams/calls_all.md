# Function Call Graph (whole repo, cross-module only)

Which modules' functions call into other modules (intra-module calls omitted for clarity).

```mermaid
graph TD
  main["main"]
  SummaryCache_get["SummaryCache.get"]
  ingest_directory["ingest_directory"]
  parse_file["parse_file"]
  run_pipeline["run_pipeline"]
  extract_repo_graph["extract_repo_graph"]
  FakeEmbedder_embed_chunks["FakeEmbedder.embed_chunks"]
  FakeStore_store_chunks["FakeStore.store_chunks"]
  group_chunks_into_modules["group_chunks_into_modules"]
  FakeSummarizer_summarize_module["FakeSummarizer.summarize_module"]
  FakeSummarizer_summarize_architecture_overview["FakeSummarizer.summarize_architecture_overview"]
  generate_diagrams["generate_diagrams"]
  generate_class_and_call_diagrams["generate_class_and_call_diagrams"]
  write_docs_to_directory["write_docs_to_directory"]
  render_diagram_images["render_diagram_images"]
  create_embedder["create_embedder"]
  PgVectorStore_initialize["PgVectorStore.initialize"]
  SummaryCache_close["SummaryCache.close"]
  generate_architecture_diagram["generate_architecture_diagram"]
  SummaryCache_set["SummaryCache.set"]
  generate_dependency_diagram["generate_dependency_diagram"]
  generate_class_diagram["generate_class_diagram"]
  generate_call_graph["generate_call_graph"]
  module_of["module_of"]
  generate_sequence_diagram["generate_sequence_diagram"]
  EmbeddingCache_get["EmbeddingCache.get"]
  SummaryCache_key["SummaryCache._key"]
  EmbeddingCache_set["EmbeddingCache.set"]
  EmbeddingCache_close["EmbeddingCache.close"]
  with_cache["with_cache"]
  PgVectorStore_store_chunks["PgVectorStore.store_chunks"]
  PgVectorStore_close["PgVectorStore.close"]
  resolve_and_filter_calls["resolve_and_filter_calls"]
  default_generate_fn["_default_generate_fn"]
  test_classifies_internal_dependency_as_imports["test_classifies_internal_dependency_as_imports"]
  extract_relationships["extract_relationships"]
  test_classifies_external_dependency_as_uses["test_classifies_external_dependency_as_uses"]
  test_internal_match_is_case_insensitive["test_internal_match_is_case_insensitive"]
  test_skips_self_reference["test_skips_self_reference"]
  test_skips_empty_dependency_strings["test_skips_empty_dependency_strings"]
  test_no_modules_no_relationships["test_no_modules_no_relationships"]
  test_sanitize_id_produces_valid_mermaid_id["test_sanitize_id_produces_valid_mermaid_id"]
  sanitize_id["_sanitize_id"]
  test_architecture_diagram_includes_all_module_nodes["test_architecture_diagram_includes_all_module_nodes"]
  test_architecture_diagram_includes_external_nodes_and_edges["test_architecture_diagram_includes_external_nodes_and_edges"]
  test_architecture_diagram_is_valid_mermaid_graph_td["test_architecture_diagram_is_valid_mermaid_graph_td"]
  test_architecture_diagram_handles_empty_modules["test_architecture_diagram_handles_empty_modules"]
  test_dependency_diagram_excludes_external_edges["test_dependency_diagram_excludes_external_edges"]
  test_dependency_diagram_is_graph_lr["test_dependency_diagram_is_graph_lr"]
  test_generate_diagrams_returns_both_diagram_types["test_generate_diagrams_returns_both_diagram_types"]
  test_generate_diagrams_handles_no_modules_without_crashing["test_generate_diagrams_handles_no_modules_without_crashing"]
  test_embed_text_includes_type_name_and_path["test_embed_text_includes_type_name_and_path"]
  chunk_to_embedding_text["chunk_to_embedding_text"]
  test_file_chunk_always_present["test_file_chunk_always_present"]
  test_extracts_class_and_methods_with_correct_parent["test_extracts_class_and_methods_with_correct_parent"]
  test_nested_function_not_extracted_separately["test_nested_function_not_extracted_separately"]
  test_extracts_standalone_function["test_extracts_standalone_function"]
  test_extracts_imports["test_extracts_imports"]
  test_extracts_top_level_constant["test_extracts_top_level_constant"]
  test_chunk_ids_are_stable_across_runs["test_chunk_ids_are_stable_across_runs"]
  test_syntax_error_falls_back_instead_of_raising["test_syntax_error_falls_back_instead_of_raising"]
  test_empty_file_returns_single_file_chunk["test_empty_file_returns_single_file_chunk"]
  test_discover_finds_python_files_recursively["test_discover_finds_python_files_recursively"]
  discover_python_files["discover_python_files"]
  test_discover_excludes_pycache["test_discover_excludes_pycache"]
  test_discover_returns_empty_list_for_no_python_files["test_discover_returns_empty_list_for_no_python_files"]
  test_ingest_directory_produces_relative_file_paths["test_ingest_directory_produces_relative_file_paths"]
  test_run_pipeline_runs_all_six_steps_in_order["test_run_pipeline_runs_all_six_steps_in_order"]
  test_run_pipeline_skips_storage_when_store_is_none["test_run_pipeline_skips_storage_when_store_is_none"]
  test_run_pipeline_raises_on_empty_repo["test_run_pipeline_raises_on_empty_repo"]
  test_run_pipeline_generates_diagrams["test_run_pipeline_generates_diagrams"]
  test_row_to_chunk_converts_db_row_to_code_chunk["test_row_to_chunk_converts_db_row_to_code_chunk"]
  row_to_chunk["_row_to_chunk"]
  test_row_to_chunk_handles_null_metadata["test_row_to_chunk_handles_null_metadata"]
  store["store"]
  test_store_and_search_round_trip["test_store_and_search_round_trip"]
  PgVectorStore_search_similar["PgVectorStore.search_similar"]
  PgVectorStore_delete_chunks["PgVectorStore.delete_chunks"]
  test_delete_chunks_removes_them["test_delete_chunks_removes_them"]
  test_groups_chunks_by_top_level_directory["test_groups_chunks_by_top_level_directory"]
  test_root_level_files_grouped_under_root["test_root_level_files_grouped_under_root"]
  test_mixed_root_and_subdirectory_files["test_mixed_root_and_subdirectory_files"]
  test_deeply_nested_files_group_by_immediate_parent_not_top_level["test_deeply_nested_files_group_by_immediate_parent_not_top_level"]
  test_module_prompt_includes_module_name_and_files["test_module_prompt_includes_module_name_and_files"]
  build_module_prompt["build_module_prompt"]
  test_architecture_overview_prompt_includes_module_descriptions["test_architecture_overview_prompt_includes_module_descriptions"]
  build_architecture_overview_prompt["build_architecture_overview_prompt"]
  test_summarize_module_retries_on_invalid_json_then_succeeds["test_summarize_module_retries_on_invalid_json_then_succeeds"]
  test_slugify_lowercases_and_replaces_spaces["test_slugify_lowercases_and_replaces_spaces"]
  slugify["slugify"]
  test_slugify_strips_special_characters["test_slugify_strips_special_characters"]
  test_slugify_empty_string_has_fallback["test_slugify_empty_string_has_fallback"]
  test_module_markdown_includes_all_sections["test_module_markdown_includes_all_sections"]
  render_module_markdown["render_module_markdown"]
  test_module_markdown_omits_empty_optional_sections["test_module_markdown_omits_empty_optional_sections"]
  test_diagram_markdown_wraps_mermaid_in_code_fence["test_diagram_markdown_wraps_mermaid_in_code_fence"]
  render_diagram_markdown["render_diagram_markdown"]
  test_overview_markdown_includes_repo_and_commit["test_overview_markdown_includes_repo_and_commit"]
  render_overview_markdown["render_overview_markdown"]
  test_overview_markdown_links_to_each_module_and_diagram["test_overview_markdown_links_to_each_module_and_diagram"]
  test_overview_markdown_omits_diagrams_section_when_none["test_overview_markdown_omits_diagrams_section_when_none"]
  test_writes_index_module_and_diagram_files["test_writes_index_module_and_diagram_files"]
  test_writes_only_index_when_no_modules_or_diagrams["test_writes_only_index_when_no_modules_or_diagrams"]
  test_writing_twice_overwrites_instead_of_duplicating["test_writing_twice_overwrites_instead_of_duplicating"]
  test_creates_output_directory_if_it_does_not_exist["test_creates_output_directory_if_it_does_not_exist"]
  test_returned_paths_are_the_actual_files_written["test_returned_paths_are_the_actual_files_written"]
  main --> SummaryCache_get
  ingest_directory --> parse_file
  run_pipeline --> extract_repo_graph
  run_pipeline --> FakeEmbedder_embed_chunks
  run_pipeline --> FakeStore_store_chunks
  run_pipeline --> group_chunks_into_modules
  run_pipeline --> FakeSummarizer_summarize_module
  run_pipeline --> FakeSummarizer_summarize_architecture_overview
  run_pipeline --> generate_diagrams
  run_pipeline --> generate_class_and_call_diagrams
  run_pipeline --> write_docs_to_directory
  run_pipeline --> render_diagram_images
  main --> create_embedder
  main --> PgVectorStore_initialize
  main --> SummaryCache_close
  generate_architecture_diagram --> SummaryCache_set
  generate_architecture_diagram --> SummaryCache_get
  generate_dependency_diagram --> SummaryCache_get
  generate_class_diagram --> SummaryCache_set
  generate_call_graph --> module_of
  generate_call_graph --> SummaryCache_set
  generate_sequence_diagram --> SummaryCache_set
  generate_sequence_diagram --> SummaryCache_get
  generate_class_and_call_diagrams --> module_of
  generate_class_and_call_diagrams --> SummaryCache_set
  generate_class_and_call_diagrams --> SummaryCache_get
  EmbeddingCache_get --> SummaryCache_key
  EmbeddingCache_set --> SummaryCache_key
  EmbeddingCache_close --> SummaryCache_close
  with_cache --> SummaryCache_get
  with_cache --> SummaryCache_set
  PgVectorStore_store_chunks --> SummaryCache_get
  PgVectorStore_close --> SummaryCache_close
  resolve_and_filter_calls --> SummaryCache_get
  default_generate_fn --> with_cache
  test_classifies_internal_dependency_as_imports --> extract_relationships
  test_classifies_external_dependency_as_uses --> extract_relationships
  test_internal_match_is_case_insensitive --> extract_relationships
  test_skips_self_reference --> extract_relationships
  test_skips_empty_dependency_strings --> extract_relationships
  test_no_modules_no_relationships --> extract_relationships
  test_sanitize_id_produces_valid_mermaid_id --> sanitize_id
  test_architecture_diagram_includes_all_module_nodes --> generate_architecture_diagram
  test_architecture_diagram_includes_external_nodes_and_edges --> extract_relationships
  test_architecture_diagram_includes_external_nodes_and_edges --> generate_architecture_diagram
  test_architecture_diagram_is_valid_mermaid_graph_td --> generate_architecture_diagram
  test_architecture_diagram_handles_empty_modules --> generate_architecture_diagram
  test_dependency_diagram_excludes_external_edges --> extract_relationships
  test_dependency_diagram_excludes_external_edges --> generate_dependency_diagram
  test_dependency_diagram_is_graph_lr --> generate_dependency_diagram
  test_generate_diagrams_returns_both_diagram_types --> generate_diagrams
  test_generate_diagrams_handles_no_modules_without_crashing --> generate_diagrams
  test_embed_text_includes_type_name_and_path --> chunk_to_embedding_text
  test_file_chunk_always_present --> parse_file
  test_extracts_class_and_methods_with_correct_parent --> parse_file
  test_nested_function_not_extracted_separately --> parse_file
  test_extracts_standalone_function --> parse_file
  test_extracts_imports --> parse_file
  test_extracts_top_level_constant --> parse_file
  test_chunk_ids_are_stable_across_runs --> parse_file
  test_syntax_error_falls_back_instead_of_raising --> parse_file
  test_syntax_error_falls_back_instead_of_raising --> SummaryCache_get
  test_empty_file_returns_single_file_chunk --> parse_file
  test_discover_finds_python_files_recursively --> discover_python_files
  test_discover_excludes_pycache --> discover_python_files
  test_discover_returns_empty_list_for_no_python_files --> discover_python_files
  test_ingest_directory_produces_relative_file_paths --> discover_python_files
  test_ingest_directory_produces_relative_file_paths --> ingest_directory
  test_run_pipeline_runs_all_six_steps_in_order --> run_pipeline
  test_run_pipeline_runs_all_six_steps_in_order --> SummaryCache_set
  test_run_pipeline_skips_storage_when_store_is_none --> run_pipeline
  test_run_pipeline_raises_on_empty_repo --> run_pipeline
  test_run_pipeline_generates_diagrams --> run_pipeline
  test_row_to_chunk_converts_db_row_to_code_chunk --> row_to_chunk
  test_row_to_chunk_handles_null_metadata --> row_to_chunk
  store --> PgVectorStore_initialize
  store --> SummaryCache_close
  test_store_and_search_round_trip --> PgVectorStore_search_similar
  test_store_and_search_round_trip --> PgVectorStore_delete_chunks
  test_delete_chunks_removes_them --> PgVectorStore_delete_chunks
  test_delete_chunks_removes_them --> PgVectorStore_search_similar
  test_groups_chunks_by_top_level_directory --> group_chunks_into_modules
  test_groups_chunks_by_top_level_directory --> SummaryCache_set
  test_root_level_files_grouped_under_root --> group_chunks_into_modules
  test_root_level_files_grouped_under_root --> SummaryCache_set
  test_mixed_root_and_subdirectory_files --> group_chunks_into_modules
  test_mixed_root_and_subdirectory_files --> SummaryCache_set
  test_deeply_nested_files_group_by_immediate_parent_not_top_level --> group_chunks_into_modules
  test_deeply_nested_files_group_by_immediate_parent_not_top_level --> SummaryCache_set
  test_module_prompt_includes_module_name_and_files --> build_module_prompt
  test_architecture_overview_prompt_includes_module_descriptions --> build_architecture_overview_prompt
  test_summarize_module_retries_on_invalid_json_then_succeeds --> build_module_prompt
  test_slugify_lowercases_and_replaces_spaces --> slugify
  test_slugify_strips_special_characters --> slugify
  test_slugify_empty_string_has_fallback --> slugify
  test_module_markdown_includes_all_sections --> render_module_markdown
  test_module_markdown_omits_empty_optional_sections --> render_module_markdown
  test_diagram_markdown_wraps_mermaid_in_code_fence --> render_diagram_markdown
  test_overview_markdown_includes_repo_and_commit --> render_overview_markdown
  test_overview_markdown_links_to_each_module_and_diagram --> render_overview_markdown
  test_overview_markdown_omits_diagrams_section_when_none --> render_overview_markdown
  test_writes_index_module_and_diagram_files --> write_docs_to_directory
  test_writes_only_index_when_no_modules_or_diagrams --> write_docs_to_directory
  test_writing_twice_overwrites_instead_of_duplicating --> write_docs_to_directory
  test_creates_output_directory_if_it_does_not_exist --> write_docs_to_directory
  test_returned_paths_are_the_actual_files_written --> write_docs_to_directory
```
