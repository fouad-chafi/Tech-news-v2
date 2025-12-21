import logging
from typing import List, Dict, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.layout import Layout
from rich.text import Text
from rich import box

logger = logging.getLogger(__name__)

class CLIInterface:
    def __init__(self):
        self.console = Console()

    def show_welcome(self) -> None:
        welcome_text = """
[bold cyan]Tech News Aggregator[/bold cyan]
[yellow]Automated RSS feed processing with AI analysis[/yellow]

[dim]Fetch articles from 100+ tech sources, analyze them with local LLM,
categorize dynamically, and store in Supabase database.[/dim]
        """
        panel = Panel(
            welcome_text.strip(),
            title="[bold blue]Welcome[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def show_connection_status(self, db_status: bool, llm_status: bool) -> bool:
        status_table = Table(title="System Status", box=box.ROUNDED)
        status_table.add_column("Component", style="cyan", no_wrap=True)
        status_table.add_column("Status", style="bold")
        status_table.add_column("Details", style="dim")

        db_status_text = "[green]Connected[/green]" if db_status else "[red]Failed[/red]"
        db_details = "Supabase database accessible" if db_status else "Check configuration"
        status_table.add_row("Database", db_status_text, db_details)

        llm_status_text = "[green]Connected[/green]" if llm_status else "[red]Failed[/red]"
        llm_details = "Local LLM responding" if llm_status else "Check LLM server"
        status_table.add_row("LLM", llm_status_text, llm_details)

        self.console.print(status_table)
        self.console.print()

        if not db_status or not llm_status:
            self.console.print("[bold red]System initialization failed. Please check the errors above.[/bold red]")
            return False

        self.console.print("[bold green]All systems ready![/bold green]")
        return True

    def show_sources_by_group(self, sources_by_group: Dict[str, List[Dict[str, Any]]]) -> None:
        table = Table(title="RSS Sources by Group", box=box.ROUNDED)
        table.add_column("Group", style="cyan", no_wrap=True, width=20)
        table.add_column("Sources", justify="center", style="magenta")
        table.add_column("Status", justify="center", width=10)
        table.add_column("Select", justify="center", width=8)

        for i, (group_name, sources) in enumerate(sources_by_group.items(), 1):
            enabled_count = sum(1 for source in sources if source.get('enabled', False))
            total_count = len(sources)
            status = f"[green]{enabled_count}[/green]/{total_count}"

            table.add_row(
                f"[{i}] {group_name}",
                str(total_count),
                status,
                "✓" if enabled_count > 0 else "○"
            )

        self.console.print(table)
        self.console.print()

    def select_source_groups(self, sources_by_group: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        self.console.print("[bold yellow]Select source groups to process:[/bold yellow]")
        self.console.print("[dim]Enter group numbers separated by commas (e.g., 1,3,5) or 'all' for all groups[/dim]")
        self.console.print()

        # Display numbered groups
        groups_list = list(sources_by_group.keys())
        for i, group in enumerate(groups_list, 1):
            enabled_count = sum(1 for source in sources_by_group[group] if source.get('enabled', False))
            total_count = len(sources_by_group[group])
            self.console.print(f"[{i:2d}] {group} ({enabled_count}/{total_count} enabled)")

        self.console.print()

        while True:
            selection = Prompt.ask("Your selection", default="all").strip().lower()

            if selection == "all":
                return groups_list

            try:
                selected_indices = [int(x.strip()) - 1 for x in selection.split(",")]
                selected_groups = []

                for idx in selected_indices:
                    if 0 <= idx < len(groups_list):
                        selected_groups.append(groups_list[idx])
                    else:
                        self.console.print(f"[red]Invalid group number: {idx + 1}[/red]")
                        break
                else:
                    if selected_groups:
                        return selected_groups

            except ValueError:
                self.console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")

    def configure_max_articles(self) -> int:
        self.console.print("[bold yellow]Configure maximum articles per source:[/bold yellow]")
        self.console.print("[dim]This limits how many articles to fetch from each RSS feed[/dim]")
        self.console.print()

        max_articles = IntPrompt.ask(
            "Maximum articles per source",
            default=10,
            show_choices=True,
            choices=["5", "10", "20", "50"]
        )
        return max(1, min(100, max_articles))

    def show_processing_start(self, selected_groups: List[str], total_sources: int, max_articles: int) -> None:
        info_text = f"""
[bold cyan]Starting RSS Processing[/bold cyan]

[yellow]Selected Groups:[/yellow] {', '.join(selected_groups)}
[yellow]Total Sources:[/yellow] {total_sources}
[yellow]Max Articles per Source:[/yellow] {max_articles}
[yellow]Estimated Total Articles:[/yellow] {total_sources * max_articles}

[dim]Press Ctrl+C to interrupt processing[/dim]
        """
        panel = Panel(
            info_text.strip(),
            title="[bold blue]Processing Configuration[/bold blue]",
            border_style="blue"
        )
        self.console.print(panel)

    def create_progress_bar(self) -> Progress:
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console
        )

    def update_progress(self, progress: Progress, task_id: str, description: str, advance: int = 1) -> None:
        progress.update(task_id, description=description, advance=advance)

    def show_source_progress(self, progress: Progress, source_name: str, articles_found: int, articles_processed: int) -> None:
        self.console.print(f"[cyan]Processing:[/cyan] {source_name} - Found {articles_found} articles, Processed {articles_processed}")

    def show_article_analysis(self, progress: Progress, title: str, categories: List[str], filtered: bool) -> None:
        if filtered:
            self.console.print(f"[red]Filtered:[/red] {title[:60]}...")
        else:
            categories_str = ", ".join(categories) if categories else "Uncategorized"
            self.console.print(f"[green]Analyzed:[/green] {title[:60]}... -> [{categories_str}]")

    def show_processing_results(self, results: Dict[str, Any]) -> None:
        results_table = Table(title="Processing Results", box=box.ROUNDED)
        results_table.add_column("Metric", style="cyan", no_wrap=True)
        results_table.add_column("Value", justify="center", style="bold")

        results_table.add_row("Sources Processed", str(results.get('sources_processed', 0)))
        results_table.add_row("Articles Found", str(results.get('articles_found', 0)))
        results_table.add_row("Articles Analyzed", str(results.get('articles_analyzed', 0)))
        results_table.add_row("Articles Stored", str(results.get('articles_stored', 0)))
        results_table.add_row("Articles Filtered", f"[red]{results.get('articles_filtered', 0)}[/red]")
        results_table.add_row("New Categories", f"[green]{results.get('new_categories', 0)}[/green]")
        results_table.add_row("Errors", f"[red]{results.get('errors', 0)}[/red]")

        self.console.print(results_table)
        self.console.print()

    def show_error(self, message: str, exception: Optional[Exception] = None) -> None:
        error_panel = Panel(
            f"[red]{message}[/red]" if not exception else f"[red]{message}\n{str(exception)}[/red]",
            title="[bold red]Error[/bold red]",
            border_style="red"
        )
        self.console.print(error_panel)

    def show_warning(self, message: str) -> None:
        warning_panel = Panel(
            f"[yellow]{message}[/yellow]",
            title="[bold yellow]Warning[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(warning_panel)

    def show_success(self, message: str) -> None:
        success_panel = Panel(
            f"[green]{message}[/green]",
            title="[bold green]Success[/bold green]",
            border_style="green"
        )
        self.console.print(success_panel)

    def confirm_action(self, message: str, default: bool = True) -> bool:
        return Confirm.ask(f"[bold yellow]{message}[/bold yellow]", default=default)

    def prompt_for_input(self, message: str, default: str = "", password: bool = False) -> str:
        return Prompt.ask(f"[bold cyan]{message}[/bold cyan]", default=default, password=password)

    def show_categories_table(self, categories: List[str]) -> None:
        if not categories:
            self.console.print("[yellow]No categories found[/yellow]")
            return

        table = Table(title="Available Categories", box=box.ROUNDED)
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Articles", justify="center", style="magenta")

        # Note: This would require database query to get article counts
        for category in sorted(categories):
            table.add_row(category, "N/A")  # Would need actual count

        self.console.print(table)

    def show_recent_articles(self, articles: List[Dict[str, Any]], limit: int = 10) -> None:
        if not articles:
            self.console.print("[yellow]No articles found[/yellow]")
            return

        table = Table(title=f"Recent {min(limit, len(articles))} Articles", box=box.ROUNDED)
        table.add_column("Title", style="cyan", no_wrap=True, max_width=50)
        table.add_column("Source", style="magenta")
        table.add_column("Categories", style="green")
        table.add_column("Score", justify="center", width=6)
        table.add_column("Date", style="dim", width=12)

        for article in articles[:limit]:
            title = article.get('title', 'No title')[:47] + "..." if len(article.get('title', '')) > 50 else article.get('title', 'No title')
            source = article.get('source_name', 'Unknown')
            categories = ", ".join(article.get('categories', [])[:2])  # Show max 2 categories
            score = str(article.get('relevance_score', 'N/A'))
            date = article.get('published_date', 'Unknown')[:10] if article.get('published_date') else 'Unknown'

            table.add_row(title, source, categories, score, date)

        self.console.print(table)

    def clear_screen(self) -> None:
        self.console.clear()

    def print_separator(self) -> None:
        self.console.print()

    def show_menu(self, title: str, options: List[str]) -> str:
        table = Table(title=title, box=box.ROUNDED, show_header=False)
        table.add_column("Option", style="cyan", no_wrap=True, width=5)
        table.add_column("Description", style="white")

        for i, option in enumerate(options, 1):
            table.add_row(f"[{i}]", option)

        self.console.print(table)

        while True:
            try:
                choice = IntPrompt.ask("Select an option", show_choices=False)
                if 1 <= choice <= len(options):
                    return str(choice)
                else:
                    self.console.print(f"[red]Please enter a number between 1 and {len(options)}[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number[/red]")