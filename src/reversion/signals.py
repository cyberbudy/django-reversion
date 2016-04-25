from django.dispatch.dispatcher import Signal


# Version management signals.
pre_revision_commit = Signal(providing_args=["instances", "revision", "versions"])
post_revision_commit = Signal(providing_args=["instances", "revision", "versions"])

version_approve = Signal(providing_args=["before", "after" "instance"])
version_reject = Signal(providing_args=["before", "after", "instance"])
