"""Bundled LLM documentation content for kb-yaml-to-lens dashboard compiler.

This module provides access to the bundled documentation resources:
- llms-full.txt: Complete documentation for LLM context
- guides/: Workflow guides for dashboard creation
"""

from importlib.resources import as_file, files


def get_full_docs() -> str:
    """Get the complete LLM documentation content.

    Returns:
        The contents of llms-full.txt, containing all documentation
        concatenated for LLM context.

    Raises:
        FileNotFoundError: If llms-full.txt is not bundled in the package.
    """
    resources = files('kb_dashboard_docs.resources')
    llms_full = resources.joinpath('llms-full.txt')
    return llms_full.read_text(encoding='utf-8')


def list_guides() -> list[str]:
    """List available workflow guides.

    Returns:
        List of guide names (without the .md extension).
    """
    resources = files('kb_dashboard_docs.resources')
    guides_dir = resources.joinpath('guides')

    guides: list[str] = []
    try:
        # Use iterdir to list contents
        with as_file(guides_dir) as guides_path:
            if guides_path.is_dir():
                guides.extend(item.stem for item in guides_path.iterdir() if item.suffix == '.md' and item.is_file())
    except (TypeError, FileNotFoundError):
        # Directory doesn't exist or can't be iterated
        pass

    return sorted(guides)


def get_guide(name: str) -> str:
    """Get the content of a specific workflow guide.

    Args:
        name: The guide name (with or without .md extension).

    Returns:
        The contents of the guide markdown file.

    Raises:
        FileNotFoundError: If the guide doesn't exist.
    """
    # Normalize name (remove .md if present)
    name = name.removesuffix('.md')

    resources = files('kb_dashboard_docs.resources')
    guide_file = resources.joinpath('guides', f'{name}.md')

    try:
        return guide_file.read_text(encoding='utf-8')
    except FileNotFoundError:
        available = list_guides()
        available_str = ', '.join(available) if len(available) > 0 else '(none bundled)'
        msg = f"Guide '{name}' not found. Available guides: {available_str}"
        raise FileNotFoundError(msg) from None


__all__ = ['get_full_docs', 'get_guide', 'list_guides']
