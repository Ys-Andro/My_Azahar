#!/usr/bin/env python3
"""Apply the My_Azahar Ocarina of Time 3D Android performance profile."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "src/common/settings.h"
CONFIG = ROOT / "src/android/app/src/main/jni/config.cpp"
GRADLE = ROOT / "src/android/app/build.gradle.kts"
STRINGS = ROOT / "src/android/app/src/main/res/values/strings.xml"


def ensure_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Required pattern not found in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Renderer/core defaults: OpenGL ES is the stable baseline for this dedicated OoT3D build.
ensure_once(
    SETTINGS,
    "#if defined(ANDROID) && defined(ENABLE_VULKAN) // Prefer Vulkan on Android, OpenGL on everything else\n        GraphicsAPI::Vulkan,",
    "#if defined(ANDROID) && defined(ENABLE_VULKAN) // My_Azahar OoT3D: prefer stable OpenGL ES on Adreno 6xx\n        GraphicsAPI::OpenGL,",
)
ensure_once(
    SETTINGS,
    "SwitchableSetting<bool> async_shader_compilation{false, Keys::async_shader_compilation};",
    "SwitchableSetting<bool> async_shader_compilation{true, Keys::async_shader_compilation};",
)
ensure_once(
    SETTINGS,
    "SwitchableSetting<bool> shaders_accurate_mul{true, Keys::shaders_accurate_mul};",
    "SwitchableSetting<bool> shaders_accurate_mul{false, Keys::shaders_accurate_mul};",
)
ensure_once(
    SETTINGS,
    "SwitchableSetting<LayoutOption> layout_option{LayoutOption::Default, Keys::layout_option};",
    "SwitchableSetting<LayoutOption> layout_option{LayoutOption::SingleScreen, Keys::layout_option};",
)

# Device-specific packaging: this application targets the user's ARM64 Android phone.
ensure_once(
    GRADLE,
    'val abiFilter = listOf("arm64-v8a", "x86_64")',
    'val abiFilter = listOf("arm64-v8a")',
)

# Make the launcher/UI identify this build as the dedicated Ocarina 3D edition.
ensure_once(
    STRINGS,
    '<string name="app_name" translatable="false">Azahar</string>',
    '<string name="app_name" translatable="false">My Ocarina 3D</string>',
)
ensure_once(
    STRINGS,
    '<string name="app_notification_channel_name" translatable="false">Azahar</string>',
    '<string name="app_notification_channel_name" translatable="false">My Ocarina 3D</string>',
)

profile = '''\n    // My_Azahar Ocarina of Time 3D performance profile.\n    // The Android build is intentionally specialized for OoT3D.\n    // Keep native resolution and prioritize stable frame pacing, low shader overhead,\n    // and the OpenGL path that has proven stable for OoT3D.\n    Settings::values.graphics_api = Settings::GraphicsAPI::OpenGL;\n    Settings::values.use_cpu_jit = true;\n    Settings::values.use_fastinterp = true;\n    Settings::values.cpu_clock_percentage = 100;\n    Settings::values.use_hw_shader = true;\n    Settings::values.use_shader_jit = true;\n    Settings::values.async_shader_compilation = true;\n    Settings::values.async_presentation = false;\n    Settings::values.use_disk_shader_cache = true;\n    Settings::values.shaders_accurate_mul = false;\n    Settings::values.use_vsync = false;\n    Settings::values.use_skip_duplicate_frames = false;\n    Settings::values.resolution_factor = 1;\n    Settings::values.use_integer_scaling = false;\n    Settings::values.frame_limit = 100;\n    Settings::values.texture_filter = Settings::TextureFilter::NoFilter;\n    Settings::values.texture_sampling = Settings::TextureSampling::GameControlled;\n    Settings::values.simulate_3ds_gpu_timings = false;\n    Settings::values.disable_right_eye_render = false;\n    Settings::values.render_3d = Settings::StereoRenderOption::Off;\n    Settings::values.factor_3d = 0;\n    Settings::values.swap_eyes_3d = false;\n    Settings::values.custom_textures = false;\n    Settings::values.preload_textures = false;\n    Settings::values.async_custom_loading = true;\n    Settings::values.layout_option = Settings::LayoutOption::SingleScreen;\n    Settings::values.screen_gap = 0;\n    Settings::values.aspect_ratio = Settings::AspectRatio::Default;\n\n'''
marker = "    // Apply the log_filter setting as the logger has already been initialized\n"
config_text = CONFIG.read_text(encoding="utf-8")
if "My_Azahar Ocarina of Time 3D performance profile." not in config_text:
    if marker not in config_text:
        raise SystemExit(f"Required insertion marker not found in {CONFIG}")
    config_text = config_text.replace(marker, profile + marker, 1)
    CONFIG.write_text(config_text, encoding="utf-8")

print("My_Azahar OoT3D optimization profile applied successfully.")
