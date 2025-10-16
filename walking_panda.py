# walking_panda.py
from math import pi, sin, cos
import argparse
import os
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor


class WalkingPanda(ShowBase):
    """
    Small cute panda + optional music.
    - Default scale results in a smaller panda (0.005 * 0.6 = 0.003).
    - Music path can be provided via --music, otherwise uses assets/sounds/ambient.ogg.
    - Volume hotkeys: ']' up, '[' down.
    """

    def __init__(
        self,
        no_rotate: bool = False,
        scale: float = 0.6,
        volume: float = 0.9,
        music_path: str | None = None,
    ):
        super().__init__()
        self._rotate_enabled = not no_rotate
        self._volume = max(0.0, min(1.0, float(volume)))  # clamp [0,1]

        # Scene
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)

        # Panda actor (cute small)
        self.panda_actor = Actor("models/panda-model", {"walk": "models/panda-walk4"})
        base_scale = 0.005
        final_scale = base_scale * float(scale)
        self.panda_actor.setScale(final_scale, final_scale, final_scale)
        self.panda_actor.reparentTo(self.render)
        self.panda_actor.loop("walk")

        # Optional camera rotation
        if self._rotate_enabled:
            self.taskMgr.add(self._spin_camera_task, "SpinCameraTask")

        # Music (optional)
        default_music = os.path.join("assets", "sounds", "ambient.ogg")
        self._music_path = music_path if music_path else default_music
        self._music = None
        self._init_music()

        # Runtime volume hotkeys
        self.accept("]", self._bump_volume, [+0.05])  # louder
        self.accept("[", self._bump_volume, [-0.05])  # quieter

    def _init_music(self) -> None:
        """Load & play ambient music if file exists; log helpful info."""
        try:
            if os.path.isfile(self._music_path):
                self._music = self.loader.loadMusic(self._music_path)
                if self._music:
                    self._music.setLoop(True)
                    self._apply_volume()
                    self._music.play()
                    print(f"[audio] Playing: {self._music_path} (vol={self._volume:.2f})")
                else:
                    print(f"[audio] Failed to load music handle: {self._music_path}")
            else:
                print(f"[audio] File not found: {self._music_path} (music skipped)")
        except Exception as exc:
            print(f"[audio] Error loading music: {exc}")
            self._music = None

    def _apply_volume(self) -> None:
        if self._music:
            self._music.setVolume(self._volume)

    def _bump_volume(self, delta: float) -> None:
        self._volume = max(0.0, min(1.0, self._volume + delta))
        self._apply_volume()
        print(f"[audio] Volume: {self._volume:.2f}")

    def _spin_camera_task(self, task: Task):
        angle_degrees = task.time * 6.0
        angle_radians = angle_degrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angle_radians), -20.0 * cos(angle_radians), 3)
        self.camera.setHpr(angle_degrees, 0, 0)
        return Task.cont


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="walking_panda",
        description="Small cute panda with optional music and volume controls.",
    )
    parser.add_argument(
        "--no-rotate",
        help="Disable camera rotation",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.6,
        metavar="MULT",
        help="Panda size multiplier over base 0.002 (e.g., 0.4, 0.6, 1.0).",
    )
    parser.add_argument(
        "--volume",
        type=float,
        default=0.9,
        metavar="0..1",
        help="Music volume (0.0–1.0).",
    )
    parser.add_argument(
        "--music",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to an audio file (e.g., assets/sounds/ambient.ogg).",
    )
    args = parser.parse_args()

    app = WalkingPanda(
        no_rotate=args.no_rotate,
        scale=args.scale,
        volume=args.volume,
        music_path=args.music,
    )
    app.run()


if __name__ == "__main__":
    main()

