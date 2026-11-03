"""Regression tests for Snap's portal chooser and About version display."""
import os
from pathlib import Path
import runpy
import re
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = runpy.run_path(str(ROOT / 'reelplayer'), run_name='reelplayer_native_test')
PICK_FOLDER = FUNCTIONS['pick_folder']
ORIGINAL_GLOBALS = PICK_FOLDER.__globals__
PORTAL_SELECTED = '/run/user/1000/doc/d505923/smb-share:server=example,share=music'


class StubDialog:
    def __init__(self, response=1):
        self.response = response
        self.handler = None
        self.destroyed = False
        self.shown = False

    def set_modal(self, value):
        self.modal = value

    def connect(self, name, handler):
        assert name == 'response'
        self.handler = handler

    def show(self):
        self.shown = True
        self.handler(self, self.response)

    def get_filename(self):
        return PORTAL_SELECTED

    def destroy(self):
        self.destroyed = True


def fake_gtk(response=1):
    dialog = StubDialog(response)
    gtk = SimpleNamespace(
        Application=SimpleNamespace(get_default=lambda: None),
        FileChooserNative=SimpleNamespace(new=lambda *args: dialog),
        FileChooserAction=SimpleNamespace(SELECT_FOLDER=2),
        ResponseType=SimpleNamespace(ACCEPT=1),
    )
    glib = SimpleNamespace(idle_add=lambda callback: callback())
    return (gtk, glib), dialog


class NativeChooserTests(TestCase):
    def test_snap_returns_portal_document_folder(self):
        api, dialog = fake_gtk()
        with patch.dict(os.environ, {'SNAP': '/snap/test/current'}), \
             patch.dict(ORIGINAL_GLOBALS, {'GTK_NATIVE_API': api}), \
             patch('shutil.which') as which:
            self.assertEqual(PICK_FOLDER(), PORTAL_SELECTED)
            self.assertTrue(dialog.shown)
            self.assertTrue(dialog.destroyed)
            which.assert_not_called()

    def test_snap_cancel_does_not_open_zenity(self):
        api, dialog = fake_gtk(response=0)
        with patch.dict(os.environ, {'SNAP': '/snap/test/current'}), \
             patch.dict(ORIGINAL_GLOBALS, {'GTK_NATIVE_API': api}), \
             patch('shutil.which') as which:
            self.assertEqual(PICK_FOLDER(), '')
            self.assertTrue(dialog.destroyed)
            which.assert_not_called()

    def test_deb_uses_original_zenity(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch('shutil.which', return_value='/usr/bin/zenity'), \
             patch('subprocess.run') as run:
            run.return_value.returncode = 0
            run.return_value.stdout = '/home/test/Music\\n'
            self.assertEqual(PICK_FOLDER(), '/home/test/Music')
            self.assertEqual(run.call_args.args[0],
                             ['/usr/bin/zenity', '--file-selection', '--directory',
                              '--title=Choose music folder'])

    def test_about_version_matches_snapcraft(self):
        html = (ROOT / 'index.html').read_text()
        snapcraft = (ROOT / 'snap' / 'snapcraft.yaml').read_text()
        match = re.search(r"^version:\\s*'([^']+)'", snapcraft, flags=re.M)
        self.assertIsNotNone(match)
        self.assertIn(f'id="appVersion"', html)
        self.assertIn(f'Version {match.group(1)}</p>', html)
        self.assertIn('export GTK_USE_PORTAL=1', snapcraft)


if __name__ == '__main__':
    main()
