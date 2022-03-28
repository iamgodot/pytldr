import toml

from py_tldr import core
from py_tldr.core import cli
from py_tldr.page import DownloadError


def test_version(runner):
    result = runner.invoke(cli, ["-v"])
    assert result.exit_code == 0
    assert "tldr version" in result.output
    assert "client specification version" in result.output


class TestConfig:
    def test_initialize(self, tmp_path, mocker, runner):
        tmp_file = tmp_path / "config.toml"
        mocker.patch.object(core, "DEFAULT_CONFIG_DIR", tmp_path)
        mocker.patch.object(core, "DEFAULT_CONFIG_FILE", tmp_file)

        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert tmp_file.exists()
        with open(tmp_file, encoding="utf8") as f:
            config = toml.load(f)
            assert config == core.DEFAULT_CONFIG

    def test_custom(self, tmp_path, mocker):
        config = {"foo": "bar"}
        config_file = tmp_path / "custom.toml"
        with open(config_file, "w", encoding="utf8") as f:
            toml.dump(config, f)

        ctx = mocker.Mock(spec=["resilient_parsing"])
        ctx.resilient_parsing = False
        assert core.setup_config(ctx, None, config_file) == config


class TestCommand:
    def test_single(self, runner):
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 0
        assert "tldr" in result.output

    def test_multi(self, runner):
        result = runner.invoke(cli, ["git", "commit"])
        assert result.exit_code == 0
        assert "git commit" in result.output

    def test_with_update(self, mocker, runner):
        patched_update = mocker.patch("py_tldr.page.PageCache.update")
        result = runner.invoke(cli, ["--update", "tldr"])
        assert result.exit_code == 0
        assert "tldr" in result.output
        patched_update.assert_called_once()


class TestFailure:
    def test_sync_fail(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.sync", side_effect=DownloadError)
        result = runner.invoke(cli, ["--update"])
        assert result.exit_code == 1
        print(result.output)
        assert "failed" in result.output

    def test_find_page_fail(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.find", side_effect=DownloadError)
        result = runner.invoke(cli, ["tldr"])
        assert result.exit_code == 1
        assert "failed" in result.output

    def test_no_pages_found(self, mocker, runner):
        mocker.patch("py_tldr.page.PageFinder.find", return_value="")
        result = runner.invoke(cli, ["non-existed-cmd"])
        assert result.exit_code == 1
        assert "No result" in result.output
