#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件整理工具主入口
"""

import os
import sys
from tkinter import Tk
from ui import FileOrganizerUI


def main():
    """主函数"""
    root = Tk()
    app = FileOrganizerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
