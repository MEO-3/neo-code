"""
Event name constants and a thin PyPubSub wrapper.

All inter-component communication goes through here.
No component should import another component directly to trigger behaviour.
"""

from pubsub import pub


# ── Event Names ────────────────────────────────────────────────────────────────

# File lifecycle
FILE_OPENED = "file.opened"          # data: path: str, content: str
FILE_SAVED = "file.saved"            # data: path: str
FILE_NEW = "file.new"                # no data

# Code execution
EXECUTION_REQUESTED = "execution.requested"        # data: code: str
EXECUTION_STOP_REQUESTED = "execution.stop"        # no data
EXECUTION_STARTED = "execution.started"            # no data
EXECUTION_FINISHED = "execution.finished"          # data: exit_code: int

# Subprocess output
STDOUT_RECEIVED = "stdout.received"  # data: text: str
STDERR_RECEIVED = "stderr.received"  # data: text: str
CANVAS_COMMAND = "canvas.command"    # data: cmd: dict  e.g. {"cmd": "forward", "args": [100]}

# Curriculum
PROJECT_OPENED = "project.opened"    # data: project: Project (from features.curriculum.models)


# ── Convenience wrappers ───────────────────────────────────────────────────────

def subscribe(event: str, listener) -> None:
    pub.subscribe(listener, event)


def unsubscribe(event: str, listener) -> None:
    try:
        pub.unsubscribe(listener, event)
    except pub.TopicNameError:
        pass


def publish(event: str, **kwargs) -> None:
    pub.sendMessage(event, **kwargs)
