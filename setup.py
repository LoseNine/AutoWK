from setuptools import setup


try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:  # pragma: no cover - wheel is declared as a build dependency.
    _bdist_wheel = None


if _bdist_wheel:
    class bdist_wheel(_bdist_wheel):
        def get_tag(self):
            python, abi, _platform = super().get_tag()
            return python, abi, "win_amd64"

    setup(cmdclass={"bdist_wheel": bdist_wheel})
else:
    setup()
