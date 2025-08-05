from video_researcher.configuration import Configuration


def test_configuration_empty() -> None:
    Configuration.from_context()
