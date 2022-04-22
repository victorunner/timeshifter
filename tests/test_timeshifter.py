import io
from contextlib import nullcontext as do_not_raise

import pytest

from timeshifter import shift_time
from timeshifter.timeshifter import cli


@pytest.mark.parametrize(
    'time,h,m,expected,expected_raises', [
        ('11:00', -1, -30, '9:30', do_not_raise()),
        ('11:00', 1, 30, '12:30', do_not_raise()),
        ('24:00', -1, 0, '22:59', do_not_raise()),
        ('23:00', 1, 0, None, pytest.raises(ValueError)),
    ]
)
def test_shift_time(time, h, m, expected, expected_raises):
    with expected_raises:
        res = shift_time(time, hours=h, minutes=m)
        assert res == expected


@pytest.mark.parametrize(
    'input,args,expected,expected_raises', [
        (
            '-- 12:00 --',
            ('--', '-1:00'),
            '-- 11:00 --',
            do_not_raise()
        ),
        (
            'See you at 12:00, then at 14:00\n',
            ('-a', '1:00'),
            'See you at 13:00, then at 15:00\n2 change(s)\n',
            do_not_raise()
        ),
        (
            '12:00',
            ('20:00',),
            '',
            pytest.raises(ValueError)
        ),
    ]
)
def test_cli(monkeypatch, capsys, input, args, expected, expected_raises):
    monkeypatch.setattr('sys.stdin', io.StringIO(input))

    with expected_raises:
        cli(args)
        captured = capsys.readouterr()
        assert captured.out == expected


@pytest.fixture
def run(testdir):
    def do_run(*args):
        args = ['timeshifter'] + list(args)
        return testdir.run(*args)
    return do_run


def test_cli_with_files(tmpdir, run):
    input_file = tmpdir.join('input.txt')
    content = 'See you at 12:00.'
    with input_file.open('w', encoding='utf-8') as f:
        f.write(content)

    output_file = tmpdir.join('output.txt')
    result = run('-i', input_file, '-o', output_file, '-a', '--', '-3:00')
    assert result.ret == 0

    with output_file.open('r', encoding='utf-8') as f:
        modified_content = f.read()
    assert 'See you at 9:00.\n1 change(s)' == modified_content
