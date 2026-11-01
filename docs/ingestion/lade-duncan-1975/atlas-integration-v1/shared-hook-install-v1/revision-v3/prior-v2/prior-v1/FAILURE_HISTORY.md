# Retained development failure

The first SOURCE_FREEZE writer attempted relative_to(absolute_repository_root) on relative owned paths. pathlib raised ValueError before a freeze was written. Resolving the owned directory to an absolute path corrected only the metadata writer. No checked binding, expected hash, policy or production file changed; both source overlays had already passed.
