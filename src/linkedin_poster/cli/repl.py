"""REPL session loop with prompt_toolkit for the LinkedIn Copywriter CLI."""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from linkedin_poster.generation.client import PostGenerator, GenerationResult
from linkedin_poster.output.storage import save_post, list_posts
from linkedin_poster.cli.commands import parse_input, parse_format
from linkedin_poster.cli.display import (
    display_post_pair,
    display_posts_table,
    generation_spinner,
    display_welcome,
    display_help,
    display_saved,
    display_error,
    display_new_session,
    console,
)


class Session:
    """Manages the REPL session state."""

    def __init__(self, generator: PostGenerator = None, prompt_session: PromptSession = None):
        self.generator = generator or PostGenerator()
        self.current_result: GenerationResult | None = None
        self.current_format: str = "short"
        self._prompt_session = prompt_session

    def run(self):
        """Main REPL loop."""
        if self._prompt_session is None:
            self._prompt_session = PromptSession(history=InMemoryHistory())
        display_welcome()

        while True:
            try:
                raw = self._prompt_session.prompt("LinkedIn Copywriter > ")
            except (EOFError, KeyboardInterrupt):
                console.print("\nGoodbye!")
                break

            command, arg = parse_input(raw)

            if command == "":
                continue
            elif command == "/quit":
                console.print("Goodbye!")
                break
            elif command == "/help":
                display_help()
            elif command == "/new":
                self._handle_new(arg)
            elif command == "/save":
                self._handle_save()
            elif command == "/list":
                self._handle_list()
            elif command == "topic":
                self._handle_topic_or_refinement(raw.strip())
            else:
                display_error(
                    f"Unknown command: {command}. Type /help for available commands."
                )

    def _handle_new(self, arg: str | None):
        """Start a new post session."""
        self.current_format = parse_format(arg)
        self.generator.reset()
        self.current_result = None
        display_new_session(self.current_format)

    def _handle_save(self):
        """Save current post pair to disk."""
        if self.current_result is None:
            display_error("No post to save. Generate a post first.")
            return

        result = self.current_result
        file_path = save_post(
            topic=result.topic,
            en_text=result.en_text,
            pt_text=result.pt_text,
            format_type=result.format_key,
        )
        display_saved(str(file_path))

    def _handle_list(self):
        """List saved posts."""
        entries = list_posts()
        display_posts_table(entries)

    def _handle_topic_or_refinement(self, text: str):
        """Generate a new post or refine the current one."""
        if self.current_result is None:
            # First message = new topic
            with generation_spinner() as status:
                status.update("Generating EN post...")
                # generate_pair handles both EN and PT
                result = self.generator.generate_pair(text, self.current_format)
                status.update("Generating PT post...")
                # PT is already generated inside generate_pair;
                # status messages are approximate since both happen inside generate_pair
            self.current_result = result
        else:
            # Subsequent messages = refinement
            with generation_spinner() as status:
                status.update("Refining EN post...")
                result = self.generator.refine(text)
                status.update("Refining PT post...")
            self.current_result = result

        display_post_pair(
            result.en_text,
            result.pt_text,
            result.en_passed,
            result.pt_passed,
        )


def run_repl():
    """Entry point for the REPL."""
    session = Session()
    session.run()
