#!/usr/bin/env python3
"""Copy entry.png to /output/entry.png (literal path).

The entry image sits next to this file; the grader expects it at the
literal path /output/entry.png. The output path is a plain literal
string below — never a bot-directory environment variable, which
points at the repo directory and is read-only in the grader.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"

os.makedirs("/output", exist_ok=True)
shutil.copyfile(SRC, DST)
print(f"copied {SRC} -> {DST} ({os.path.getsize(DST)} bytes)")
