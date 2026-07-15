import sys
from cli_proj.main import main


def test_main_runs(capsys):
    sys.argv = ['cli-proj', 'world']
    main()
    assert 'world' in capsys.readouterr().out
