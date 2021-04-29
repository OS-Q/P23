import os

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

framework_package = "framework-arduino-sam"
if board.get("build.core", "").lower() != "arduino":
    framework_package += "-%s" % board.get("build.core").lower()
FRAMEWORK_DIR = platform.get_package_dir(framework_package)

SYSTEM_DIR = os.path.join(FRAMEWORK_DIR, "system")

assert os.path.isdir(SYSTEM_DIR)
assert os.path.isdir(FRAMEWORK_DIR)

env.SConscript("arduino-common.py")

env.Append(
    CPPDEFINES=[
        "ARDUINO_ARCH_SAM"
    ],

    CPPPATH=[
        os.path.join(FRAMEWORK_DIR, "cores", "arduino"),
        os.path.join(SYSTEM_DIR, "libsam"),
        os.path.join(SYSTEM_DIR, "CMSIS", "CMSIS", "Include"),
        os.path.join(SYSTEM_DIR, "CMSIS", "Device", "ATMEL")
    ],

    LINKFLAGS=[
        "-Wl,--entry=Reset_Handler", "-u", "_sbrk", "-u", "link", "-u",
        "_close", "-u", "_fstat", "-u", "_isatty", "-u", "_lseek", "-u",
        "_read", "-u", "_write", "-u", "_exit", "-u", "kill",
        "-u", "_getpid"
    ],

    LIBS=["sam_sam3x8e_gcc_rel", "gcc"]
)

env.Append(
    ASFLAGS=env.get("CCFLAGS", [])[:]
)

#
# Target: Build Core Library
#

libs = []

if "build.variant" in board:
    variants_dir = os.path.join(
        "$PROJECT_DIR", board.get("build.variants_dir")) if board.get(
            "build.variants_dir", "") else os.path.join(FRAMEWORK_DIR, "variants")
    env.Append(
        CPPPATH=[
            os.path.join(variants_dir, board.get("build.variant"))
        ],

        LIBPATH=[
            os.path.join(variants_dir, board.get("build.variant"))
        ],
    )
    libs.append(env.BuildLibrary(
        os.path.join("$BUILD_DIR", "FrameworkArduinoVariant"),
        os.path.join(variants_dir, board.get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    os.path.join("$BUILD_DIR", "FrameworkArduino"),
    os.path.join(FRAMEWORK_DIR, "cores", "arduino")
))

env.Prepend(LIBS=libs)