import os
import pathlib


def compile_markdown_references() -> None:
    """Compile markdown docs under `src/dashboard_compiler` into `yaml_reference.md`.

    The main `dashboard/dashboard.md` file is placed first (if present), followed by all other markdown files sorted by relative path.
    """
    repo_root = pathlib.Path(__file__).parent.parent
    output_file_path = repo_root / 'yaml_reference.md'
    docs_root_path = repo_root / 'src' / 'dashboard_compiler'

    main_dashboard_doc_rel_path = 'dashboard/dashboard.md'
    main_dashboard_doc_abs_path = docs_root_path / main_dashboard_doc_rel_path

    all_md_files: list[pathlib.Path] = []

    for md_file in docs_root_path.rglob('*.md'):
        if md_file.resolve() == main_dashboard_doc_abs_path.resolve():
            continue  # Skip the main dashboard doc for now, it will be added first
        # Store relative path from repo_root for consistent sorting and display
        all_md_files.append(md_file.relative_to(repo_root))

    other_md_files: list[pathlib.Path] = sorted(all_md_files, key=lambda p: str(p))

    ordered_files_to_compile: list[pathlib.Path] = []
    if main_dashboard_doc_abs_path.exists():
        ordered_files_to_compile.append(main_dashboard_doc_abs_path.relative_to(repo_root))
    else:
        print(f'Warning: Main dashboard file not found at {main_dashboard_doc_abs_path}')

    ordered_files_to_compile.extend(other_md_files)

    with output_file_path.open('w', encoding='utf-8') as outfile:
        for i, rel_file_path in enumerate(ordered_files_to_compile):
            abs_file_path = repo_root / rel_file_path
            if not abs_file_path.is_file():
                print(f'Warning: File not found {abs_file_path}, skipping.')
                continue

            print(f'Processing: {rel_file_path}')
            _ = outfile.write('\\n---\\n\\n')
            _ = outfile.write(f'<!-- Source: {str(rel_file_path).replace(os.sep, "/")} -->\\n\\n')  # HTML comment for source
            # outfile.write(f"## Source: {str(rel_file_path).replace(os.sep, '/')}\\n\\n") # Alternative: Markdown header

            with abs_file_path.open(encoding='utf-8') as infile:
                content = infile.read()
                _ = outfile.write(content)

            if i < len(ordered_files_to_compile) - 1:
                _ = outfile.write('\\n\\n')  # Add some space before the next HR

    print(f'Successfully compiled documentation to: {output_file_path}')


if __name__ == '__main__':
    compile_markdown_references()
