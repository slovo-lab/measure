"""What an adapter can report back for one pair. Written by Claude (AI)."""


class Refused(Exception):
    """The tool declined the task because the quantities do not fit together.

    Adapters raise this only for the tool's own dimension or kind errors, so
    that a crash for another reason is not mistaken for a correct refusal.
    """


class NotOffered(Exception):
    """The tool has no feature for this task. Not a pass and not a failure."""
