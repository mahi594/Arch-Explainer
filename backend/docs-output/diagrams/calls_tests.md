# Function Call Graph: tests

Which functions/methods call which others, resolved to repo-internal definitions only.

```mermaid
graph TD
  test_classifies_internal_dependency_as_imports["test_classifies_internal_dependency_as_imports"]
  make_module["make_module"]
  extract_relationships["extract_relationships"]
  test_classifies_external_dependency_as_uses["test_classifies_external_dependency_as_uses"]
  test_internal_match_is_case_insensitive["test_internal_match_is_case_insensitive"]
  test_skips_self_reference["test_skips_self_reference"]
  test_skips_empty_dependency_strings["test_skips_empty_dependency_strings"]
  test_no_modules_no_relationships["test_no_modules_no_relationships"]
  test_sanitize_id_produces_valid_mermaid_id["test_sanitize_id_produces_valid_mermaid_id"]
  sanitize_id["_sanitize_id"]
  test_architecture_diagram_includes_all_module_nodes["test_architecture_diagram_includes_all_module_nodes"]
  generate_architecture_diagram["generate_architecture_diagram"]
  test_architecture_diagram_includes_external_nodes_and_edges["test_architecture_diagram_includes_external_nodes_and_edges"]
  test_architecture_diagram_is_valid_mermaid_graph_td["test_architecture_diagram_is_valid_mermaid_graph_td"]
  test_architecture_diagram_handles_empty_modules["test_architecture_diagram_handles_empty_modules"]
  test_dependency_diagram_excludes_external_edges["test_dependency_diagram_excludes_external_edges"]
  generate_dependency_diagram["generate_dependency_diagram"]
  test_dependency_diagram_is_graph_lr["test_dependency_diagram_is_graph_lr"]
  test_generate_diagrams_returns_both_diagram_types["test_generate_diagrams_returns_both_diagram_types"]
  generate_diagrams["generate_diagrams"]
  test_generate_diagrams_handles_no_modules_without_crashing["test_generate_diagrams_handles_no_modules_without_crashing"]
  test_embed_text_includes_type_name_and_path["test_embed_text_includes_type_name_and_path"]
  make_chunk["make_chunk"]
  chunk_to_embedding_text["chunk_to_embedding_text"]
  test_embed_chunks_returns_one_embedding_per_chunk["test_embed_chunks_returns_one_embedding_per_chunk"]
  fake_embed_fn["fake_embed_fn"]
  FakeEmbedder_embed_chunks["FakeEmbedder.embed_chunks"]
  test_embed_chunks_batches_requests["test_embed_chunks_batches_requests"]
  test_retries_on_transient_failure_then_succeeds["test_retries_on_transient_failure_then_succeeds"]
  test_raises_after_exhausting_retries["test_raises_after_exhausting_retries"]
  test_raises_on_vector_count_mismatch["test_raises_on_vector_count_mismatch"]
  test_file_chunk_always_present["test_file_chunk_always_present"]
  parse_file["parse_file"]
  test_extracts_class_and_methods_with_correct_parent["test_extracts_class_and_methods_with_correct_parent"]
  test_nested_function_not_extracted_separately["test_nested_function_not_extracted_separately"]
  test_extracts_standalone_function["test_extracts_standalone_function"]
  test_extracts_imports["test_extracts_imports"]
  test_extracts_top_level_constant["test_extracts_top_level_constant"]
  test_chunk_ids_are_stable_across_runs["test_chunk_ids_are_stable_across_runs"]
  test_syntax_error_falls_back_instead_of_raising["test_syntax_error_falls_back_instead_of_raising"]
  SummaryCache_get["SummaryCache.get"]
  test_empty_file_returns_single_file_chunk["test_empty_file_returns_single_file_chunk"]
  test_discover_finds_python_files_recursively["test_discover_finds_python_files_recursively"]
  write_sample_repo["write_sample_repo"]
  discover_python_files["discover_python_files"]
  test_discover_excludes_pycache["test_discover_excludes_pycache"]
  test_discover_returns_empty_list_for_no_python_files["test_discover_returns_empty_list_for_no_python_files"]
  test_ingest_directory_produces_relative_file_paths["test_ingest_directory_produces_relative_file_paths"]
  ingest_directory["ingest_directory"]
  test_run_pipeline_runs_all_six_steps_in_order["test_run_pipeline_runs_all_six_steps_in_order"]
  run_pipeline["run_pipeline"]
  SummaryCache_set["SummaryCache.set"]
  test_run_pipeline_skips_storage_when_store_is_none["test_run_pipeline_skips_storage_when_store_is_none"]
  test_run_pipeline_raises_on_empty_repo["test_run_pipeline_raises_on_empty_repo"]
  test_run_pipeline_generates_diagrams["test_run_pipeline_generates_diagrams"]
  test_row_to_chunk_converts_db_row_to_code_chunk["test_row_to_chunk_converts_db_row_to_code_chunk"]
  row_to_chunk["_row_to_chunk"]
  test_row_to_chunk_handles_null_metadata["test_row_to_chunk_handles_null_metadata"]
  store["store"]
  PgVectorStore_initialize["PgVectorStore.initialize"]
  SummaryCache_close["SummaryCache.close"]
  test_store_and_search_round_trip["test_store_and_search_round_trip"]
  FakeStore_store_chunks["FakeStore.store_chunks"]
  PgVectorStore_search_similar["PgVectorStore.search_similar"]
  PgVectorStore_delete_chunks["PgVectorStore.delete_chunks"]
  test_delete_chunks_removes_them["test_delete_chunks_removes_them"]
  test_groups_chunks_by_top_level_directory["test_groups_chunks_by_top_level_directory"]
  group_chunks_into_modules["group_chunks_into_modules"]
  test_root_level_files_grouped_under_root["test_root_level_files_grouped_under_root"]
  test_mixed_root_and_subdirectory_files["test_mixed_root_and_subdirectory_files"]
  test_deeply_nested_files_group_by_immediate_parent_not_top_level["test_deeply_nested_files_group_by_immediate_parent_not_top_level"]
  test_module_prompt_includes_module_name_and_files["test_module_prompt_includes_module_name_and_files"]
  build_module_prompt["build_module_prompt"]
  test_architecture_overview_prompt_includes_module_descriptions["test_architecture_overview_prompt_includes_module_descriptions"]
  build_architecture_overview_prompt["build_architecture_overview_prompt"]
  test_summarize_module_happy_path["test_summarize_module_happy_path"]
  FakeSummarizer_summarize_module["FakeSummarizer.summarize_module"]
  test_summarize_module_strips_markdown_fences["test_summarize_module_strips_markdown_fences"]
  test_summarize_module_retries_on_invalid_json_then_succeeds["test_summarize_module_retries_on_invalid_json_then_succeeds"]
  test_summarize_module_retry_prompt_includes_validation_error["test_summarize_module_retry_prompt_includes_validation_error"]
  test_summarize_module_raises_after_exhausting_retries["test_summarize_module_raises_after_exhausting_retries"]
  test_summarize_module_raises_on_schema_mismatch["test_summarize_module_raises_on_schema_mismatch"]
  test_summarize_architecture_overview_returns_plain_text["test_summarize_architecture_overview_returns_plain_text"]
  FakeSummarizer_summarize_architecture_overview["FakeSummarizer.summarize_architecture_overview"]
  make_doc["make_doc"]
  make_diagram["make_diagram"]
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
  write_docs_to_directory["write_docs_to_directory"]
  test_writes_only_index_when_no_modules_or_diagrams["test_writes_only_index_when_no_modules_or_diagrams"]
  test_writing_twice_overwrites_instead_of_duplicating["test_writing_twice_overwrites_instead_of_duplicating"]
  test_creates_output_directory_if_it_does_not_exist["test_creates_output_directory_if_it_does_not_exist"]
  test_returned_paths_are_the_actual_files_written["test_returned_paths_are_the_actual_files_written"]
  test_classifies_internal_dependency_as_imports --> make_module
  test_classifies_internal_dependency_as_imports --> extract_relationships
  test_classifies_external_dependency_as_uses --> make_module
  test_classifies_external_dependency_as_uses --> extract_relationships
  test_internal_match_is_case_insensitive --> make_module
  test_internal_match_is_case_insensitive --> extract_relationships
  test_skips_self_reference --> make_module
  test_skips_self_reference --> extract_relationships
  test_skips_empty_dependency_strings --> make_module
  test_skips_empty_dependency_strings --> extract_relationships
  test_no_modules_no_relationships --> extract_relationships
  test_sanitize_id_produces_valid_mermaid_id --> sanitize_id
  test_architecture_diagram_includes_all_module_nodes --> make_module
  test_architecture_diagram_includes_all_module_nodes --> generate_architecture_diagram
  test_architecture_diagram_includes_external_nodes_and_edges --> make_module
  test_architecture_diagram_includes_external_nodes_and_edges --> extract_relationships
  test_architecture_diagram_includes_external_nodes_and_edges --> generate_architecture_diagram
  test_architecture_diagram_is_valid_mermaid_graph_td --> make_module
  test_architecture_diagram_is_valid_mermaid_graph_td --> generate_architecture_diagram
  test_architecture_diagram_handles_empty_modules --> generate_architecture_diagram
  test_dependency_diagram_excludes_external_edges --> make_module
  test_dependency_diagram_excludes_external_edges --> extract_relationships
  test_dependency_diagram_excludes_external_edges --> generate_dependency_diagram
  test_dependency_diagram_is_graph_lr --> generate_dependency_diagram
  test_dependency_diagram_is_graph_lr --> make_module
  test_generate_diagrams_returns_both_diagram_types --> make_module
  test_generate_diagrams_returns_both_diagram_types --> generate_diagrams
  test_generate_diagrams_handles_no_modules_without_crashing --> generate_diagrams
  test_embed_text_includes_type_name_and_path --> make_chunk
  test_embed_text_includes_type_name_and_path --> chunk_to_embedding_text
  test_embed_chunks_returns_one_embedding_per_chunk --> fake_embed_fn
  test_embed_chunks_returns_one_embedding_per_chunk --> make_chunk
  test_embed_chunks_returns_one_embedding_per_chunk --> FakeEmbedder_embed_chunks
  test_embed_chunks_batches_requests --> fake_embed_fn
  test_embed_chunks_batches_requests --> make_chunk
  test_embed_chunks_batches_requests --> FakeEmbedder_embed_chunks
  test_retries_on_transient_failure_then_succeeds --> FakeEmbedder_embed_chunks
  test_retries_on_transient_failure_then_succeeds --> make_chunk
  test_raises_after_exhausting_retries --> FakeEmbedder_embed_chunks
  test_raises_after_exhausting_retries --> make_chunk
  test_raises_on_vector_count_mismatch --> FakeEmbedder_embed_chunks
  test_raises_on_vector_count_mismatch --> make_chunk
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
  test_discover_finds_python_files_recursively --> write_sample_repo
  test_discover_finds_python_files_recursively --> discover_python_files
  test_discover_excludes_pycache --> write_sample_repo
  test_discover_excludes_pycache --> discover_python_files
  test_discover_returns_empty_list_for_no_python_files --> discover_python_files
  test_ingest_directory_produces_relative_file_paths --> write_sample_repo
  test_ingest_directory_produces_relative_file_paths --> discover_python_files
  test_ingest_directory_produces_relative_file_paths --> ingest_directory
  test_run_pipeline_runs_all_six_steps_in_order --> write_sample_repo
  test_run_pipeline_runs_all_six_steps_in_order --> run_pipeline
  test_run_pipeline_runs_all_six_steps_in_order --> SummaryCache_set
  test_run_pipeline_skips_storage_when_store_is_none --> write_sample_repo
  test_run_pipeline_skips_storage_when_store_is_none --> run_pipeline
  test_run_pipeline_raises_on_empty_repo --> run_pipeline
  test_run_pipeline_generates_diagrams --> write_sample_repo
  test_run_pipeline_generates_diagrams --> run_pipeline
  test_row_to_chunk_converts_db_row_to_code_chunk --> row_to_chunk
  test_row_to_chunk_handles_null_metadata --> row_to_chunk
  store --> PgVectorStore_initialize
  store --> SummaryCache_close
  test_store_and_search_round_trip --> make_chunk
  test_store_and_search_round_trip --> FakeStore_store_chunks
  test_store_and_search_round_trip --> PgVectorStore_search_similar
  test_store_and_search_round_trip --> PgVectorStore_delete_chunks
  test_delete_chunks_removes_them --> make_chunk
  test_delete_chunks_removes_them --> FakeStore_store_chunks
  test_delete_chunks_removes_them --> PgVectorStore_delete_chunks
  test_delete_chunks_removes_them --> PgVectorStore_search_similar
  test_groups_chunks_by_top_level_directory --> make_chunk
  test_groups_chunks_by_top_level_directory --> group_chunks_into_modules
  test_groups_chunks_by_top_level_directory --> SummaryCache_set
  test_root_level_files_grouped_under_root --> make_chunk
  test_root_level_files_grouped_under_root --> group_chunks_into_modules
  test_root_level_files_grouped_under_root --> SummaryCache_set
  test_mixed_root_and_subdirectory_files --> make_chunk
  test_mixed_root_and_subdirectory_files --> group_chunks_into_modules
  test_mixed_root_and_subdirectory_files --> SummaryCache_set
  test_deeply_nested_files_group_by_immediate_parent_not_top_level --> make_chunk
  test_deeply_nested_files_group_by_immediate_parent_not_top_level --> group_chunks_into_modules
  test_deeply_nested_files_group_by_immediate_parent_not_top_level --> SummaryCache_set
  test_module_prompt_includes_module_name_and_files --> make_chunk
  test_module_prompt_includes_module_name_and_files --> build_module_prompt
  test_architecture_overview_prompt_includes_module_descriptions --> build_architecture_overview_prompt
  test_summarize_module_happy_path --> FakeSummarizer_summarize_module
  test_summarize_module_happy_path --> make_chunk
  test_summarize_module_strips_markdown_fences --> FakeSummarizer_summarize_module
  test_summarize_module_strips_markdown_fences --> make_chunk
  test_summarize_module_retries_on_invalid_json_then_succeeds --> FakeSummarizer_summarize_module
  test_summarize_module_retries_on_invalid_json_then_succeeds --> make_chunk
  test_summarize_module_retries_on_invalid_json_then_succeeds --> build_module_prompt
  test_summarize_module_retry_prompt_includes_validation_error --> FakeSummarizer_summarize_module
  test_summarize_module_retry_prompt_includes_validation_error --> make_chunk
  test_summarize_module_raises_after_exhausting_retries --> FakeSummarizer_summarize_module
  test_summarize_module_raises_after_exhausting_retries --> make_chunk
  test_summarize_module_raises_on_schema_mismatch --> FakeSummarizer_summarize_module
  test_summarize_module_raises_on_schema_mismatch --> make_chunk
  test_summarize_architecture_overview_returns_plain_text --> FakeSummarizer_summarize_architecture_overview
  make_doc --> make_module
  make_doc --> make_diagram
  test_slugify_lowercases_and_replaces_spaces --> slugify
  test_slugify_strips_special_characters --> slugify
  test_slugify_empty_string_has_fallback --> slugify
  test_module_markdown_includes_all_sections --> render_module_markdown
  test_module_markdown_includes_all_sections --> make_module
  test_module_markdown_omits_empty_optional_sections --> make_module
  test_module_markdown_omits_empty_optional_sections --> render_module_markdown
  test_diagram_markdown_wraps_mermaid_in_code_fence --> render_diagram_markdown
  test_diagram_markdown_wraps_mermaid_in_code_fence --> make_diagram
  test_overview_markdown_includes_repo_and_commit --> make_doc
  test_overview_markdown_includes_repo_and_commit --> render_overview_markdown
  test_overview_markdown_links_to_each_module_and_diagram --> make_doc
  test_overview_markdown_links_to_each_module_and_diagram --> render_overview_markdown
  test_overview_markdown_omits_diagrams_section_when_none --> make_doc
  test_overview_markdown_omits_diagrams_section_when_none --> render_overview_markdown
  test_writes_index_module_and_diagram_files --> make_doc
  test_writes_index_module_and_diagram_files --> write_docs_to_directory
  test_writes_only_index_when_no_modules_or_diagrams --> make_doc
  test_writes_only_index_when_no_modules_or_diagrams --> write_docs_to_directory
  test_writing_twice_overwrites_instead_of_duplicating --> make_doc
  test_writing_twice_overwrites_instead_of_duplicating --> write_docs_to_directory
  test_creates_output_directory_if_it_does_not_exist --> write_docs_to_directory
  test_creates_output_directory_if_it_does_not_exist --> make_doc
  test_returned_paths_are_the_actual_files_written --> write_docs_to_directory
  test_returned_paths_are_the_actual_files_written --> make_doc
```
