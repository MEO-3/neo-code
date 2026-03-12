# NeoCode GTK Runtime Setup Guide

## 1. Error Summary

When running:

```
python -m neo_code
```

The following errors may appear:

### Error 1

```
ERROR: Dependency 'girepository-2.0' is required but not found.
```

**Cause**

The system library **GObject Introspection** is missing. This library allows Python bindings (PyGObject) to access GTK libraries.

---

### Error 2

```
ValueError: Namespace Gtk not available
```

**Cause**

GTK4 runtime and its introspection bindings are not installed.

---

### Error 3

```
ValueError: Namespace Adw not available
```

**Cause**

**Libadwaita** (Adw) is missing. Libadwaita provides modern GNOME UI components used with GTK4.

---

# 2. Required Components

The application depends on the following stack:

| Layer | Package | Purpose |
|---|---|---|
| Python | PyGObject | Python bindings for GObject |
| System | gobject-introspection | Enables dynamic bindings |
| GUI | GTK4 | GUI toolkit |
| UI framework | Libadwaita | Modern GNOME UI components |

---

# 3. Required Packages

## Debian / Ubuntu (x86_64 & ARM64)

The packages are identical for both architectures.

Install dependencies:

```
sudo apt update

sudo apt install \
python3-dev \
pkg-config \
gcc \
libgirepository1.0-dev \
gobject-introspection \
libgtk-4-1 \
libgtk-4-dev \
gir1.2-gtk-4.0 \
libadwaita-1-0 \
libadwaita-1-dev \
gir1.2-adw-1 \
libcairo2-dev
```

Then install Python bindings:

```
pip install PyGObject
```

---

# 4. Conda Environment (Recommended)

If using Anaconda or Miniconda, install everything from conda-forge.

Create environment:

```
conda create -n neo python=3.12
conda activate neo
```

Install GUI dependencies:

```
conda install -c conda-forge \
pygobject \
gtk4 \
libadwaita
```

Run the application:

```
python -m neo_code
```

---

# 5. Verification

Verify GTK bindings:

```
python -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk"
```

Verify Libadwaita bindings:

```
python -c "import gi; gi.require_version('Adw','1'); from gi.repository import Adw"
```

Both commands should run without errors.

---

# 6. Architecture Support

| Architecture | Supported |
|---|---|
| x86_64 | Yes |
| ARM64 (aarch64) | Yes |
| ARMv7 | Yes (with compatible distro packages) |

GTK4, PyGObject, and Libadwaita rely on system libraries compiled for the target architecture.

---

# 7. Common Issues

## Python 3.13 Compatibility

Some PyGObject builds may not yet fully support Python 3.13.

Recommended Python versions:

- Python 3.11
- Python 3.12

---

## Mixing Conda and System GTK

Avoid mixing:

- apt GTK packages
- conda Python environments

This can cause missing namespace errors.

Preferred solutions:

- Use all apt packages with system Python, or
- Use all conda-forge packages

---

# 8. Minimal Dependency Checklist

Required runtime components:

- PyGObject
- GTK4
- Libadwaita
- GObject Introspection

If any of these are missing, the application will fail with a "Namespace not available" error.

