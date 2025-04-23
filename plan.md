# Dashboard Compiler Project Plan

This document outlines the overall plan for the dashboard compiler project, which aims to convert a simplified YAML dashboard representation into Kibana dashboard JSON.

## Objective

To create a robust and maintainable Python application that can compile YAML dashboard definitions into valid Kibana dashboard JSON, supporting various panel and visualization types.

## Current State

*   The Pydantic models representing the core YAML structure have been refactored into a logical directory hierarchy within `dashboard_compiler/models/`.
*   Initial unit tests have been created for the refactored models based on sample JSON outputs, and the models have been reviewed against these samples.
*   Basic `to_json()` methods exist for some models, but the implementation for Lens panels is incomplete and needs significant refinement based on sample JSON outputs.
*   The `compiler.py` can load and parse YAML into the Pydantic model.
*   Sample YAML configurations (`configs/`) and corresponding target JSON outputs (`samples/`) are available for reference and testing.
*   Previous plans (`plans/more-models.md`, `plans/plan-refactor-models.md`, `plans/plan-verify.md`, `plans/plan-execute-model-review-tests.md`) document the completed refactoring and initial testing, and outline steps for future work.

## Goals

1.  **Implement Complete Lens JSON Generation:** Fully implement the `to_json()` methods for all Lens-related models to accurately generate the required JSON structure based on sample outputs.
2.  **Implement ID and Reference Generation:** Develop and integrate logic for generating unique IDs and handling references within the generated JSON.
3.  **Implement Deserialization (Future):** Add functionality to deserialize Kibana JSON back into Pydantic models (as noted in the original plan, but lower priority for compilation).
4.  **Add Comprehensive Integration Testing with Syrupy:** Write integration tests using `pytest` and `syrupy` with `JSONSnapshotExtension` to ensure the compiler correctly generates JSON for various YAML inputs, comparing against sample outputs.
5.  **Add Robust Error Handling:** Implement error handling for invalid input or unexpected data.
6.  **Refine YAML Schema and Models:** Continuously refine the YAML schema and Pydantic models based on requirements and sample analysis.

## Required Worker Resources

*   **Worker 1: Lead Code Expert + Python:** Responsible for implementing the core JSON generation logic, ID/reference handling, and comprehensive testing.

## Implementation Plans

*   **Implement Lens Compilation:** See `plans/plan-implement-lens-json.md` for detailed steps on refining Lens models and implementing JSON generation.
*   **Comprehensive Integration Testing with Syrupy:** Create a detailed plan for implementing integration tests using `syrupy`.
*   **Error Handling Plan:** See `plans/more-models.md` (Step 6) for detailed steps on adding error handling.

## Verification Plan

*   See `plans/plan-verify.md` for detailed steps on verifying the correctness of the models and the initial unit tests.

## Valuable Sources

*   `yaml-reference.md`: Defines the target YAML schema.
*   Files in the `configs/` directory: Provide examples of the YAML input.
*   Files in the `samples/` directory: Provide examples of the desired JSON output.
*   `plans/more-models.md`: Original plan outlining steps for Lens panel implementation and testing.
*   `plans/plan-refactor-models.md`: Detailed plan for refactoring the model file structure (Completed).
*   `plans/plan-verify.md`: Detailed plan for model review and unit test creation (Completed).
*   `plans/plan-execute-model-review-tests.md`: Detailed subtask plan for executing the model review and unit test creation (Completed).
*   `plans/plan-implement-lens-json.md`: Detailed subtask plan for implementing Lens JSON generation and ID/reference handling.
*   Syrupy Documentation: `https://syrupy-project.github.io/syrupy/`

## Open Questions and Next Steps Considerations

*   **Complete `to_json` Implementations:** Fully implement the `to_json` methods for all models, particularly the complex Lens visualization state models (`XYVisualizationState`, `PieVisualizationState`, etc.), accurately mapping model attributes to the required JSON structure based on sample outputs.
*   **ID and Reference Generation Logic:** Develop and integrate a mechanism for generating unique IDs for panels, layers, and columns, and correctly populating the `references` arrays in the dashboard and panel JSON.
*   **Panel Validator Refinement:** Update the `@model_validator` in the base `Panel` class (or add specific validators in subclasses) to correctly instantiate the appropriate panel subclass based on the `type` field in the input data.
*   **LensState Validator/Instantiation:** Implement logic to correctly instantiate the appropriate `LensVisualizationState` subclass within the `LensState` model based on the `visualization` type specified in the input.
*   **Handling Sample Discrepancies:** Address any discrepancies or complexities in the sample JSON that are not fully captured by the current simplified models during the `to_json` implementation.
*   **Research Clever JSON Diffing:** Explore the knowledge base for clever ideas or existing tools/libraries for diffing complex JSON structures, especially in the context of testing generated output against reference samples.
*   **Implement Syrupy Integration Tests:** Create detailed test cases in `tests/test_compiler.py` using `syrupy` with `JSONSnapshotExtension` to compare the output of `compile_dashboard_to_testable_dict` against the sample JSON files.
*   **Error Handling Implementation:** Add error handling for invalid YAML input, missing required fields, or incorrect data types during parsing and compilation.