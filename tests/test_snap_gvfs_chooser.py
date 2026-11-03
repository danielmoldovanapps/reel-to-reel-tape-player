"""Regression checks for Snap-specific GVFS folder chooser behavior."""
import os
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

APP = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'reelplayer'),
                     run_name='reelplayer_chooser_test')
initial = APP['snap_gvfs_initial_folder']
pick_folder = APP['pick_folder']


class SnapGVFSChooserTests(TestCase):
    def test_non_snap_keeps_existing_chooser(self):
        with TemporaryDirectory() as temp, patch.dict(os.environ, {'XDG_RUNTIME_DIR': temp}, clear=True):
            (Path(temp) / 'gvfs').mkdir()
            (Path(temp) / 'gvfs' / 'smb-share:server=example,share=music').mkdir()
            self.assertEqual(initial(), '')

    def test_snap_picks_music_share(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / 'gvfs'
            (root / 'smb-share:server=example,share=kits').mkdir(parents=True)
            music = root / 'smb-share:server=example,share=music'
            music.mkdir()
            with patch.dict(os.environ, {'SNAP': '/snap/reelplayer/current',
                                         'XDG_RUNTIME_DIR': temp}):
                self.assertEqual(initial(), str(music) + os.sep)

    def test_missing_mount_falls_back_to_normal_dialog(self):
        with TemporaryDirectory() as temp:
            with patch.dict(os.environ, {'SNAP': '/snap/reelplayer/current',
                                         'XDG_RUNTIME_DIR': temp}):
                self.assertEqual(initial(), '')

    def test_zenity_receives_selected_folder_as_initial_location(self):
        with patch.dict(os.environ, {'SNAP': '/snap/reelplayer/current'}), \
             patch.dict(pick_folder.__globals__, {'snap_gvfs_initial_folder': lambda: '/mock/share/'}), \
             patch('shutil.which', return_value='/usr/bin/zenity'), \
             patch('subprocess.run') as process:
            process.return_value.returncode = 0
            process.return_value.stdout = '/mock/share/Rock\n'
            self.assertEqual(pick_folder(), '/mock/share/Rock')
            self.assertIn('--filename=/mock/share/', process.call_args.args[0])


if __name__ == '__main__':
    main()
