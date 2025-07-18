# 肉鸽自动射击小游戏

这是一个使用 Python 和 Pygame 库制作的简单的2D俯视角肉鸽（Roguelite）自动射击游戏。

## 游戏玩法

- **自动攻击**: 玩家会自动向最近的敌人发射子弹。
- **移动**: 你只需要专注于走位，躲避不断生成的敌人。
- **升级**: 每击杀10个敌人，你会获得1个升级点。
- **关卡**: 清空当前关卡的所有敌人后，你可以使用升级点强化自己，然后进入下一关，迎接更强的挑战。
- **技能**: 游戏包含一个技能系统，你可以使用技能来帮助你更好地生存。

## 操作说明

- **移动**:
  - `W`, `A`, `S`, `D` 键 或 `↑`, `←`, `↓`, `→` (方向键)
- **技能**:
  - `空格键`: 使用冲刺技能
- **暂停**:
  - `ESC`: 暂停或恢复游戏
- **重新开始**:
  - 在 "游戏结束" 画面，按 `R` 键重新开始游戏。

## 如何运行

1.  确保你已经安装了 Python 和 Pygame 库。
    ```bash
    pip install pygame
    ```
2.  下载项目文件，确保 `main.py` 和字体文件 `SourceHanSansSC-Regular.ttf` 在同一个目录下。
3.  运行 `main.py` 文件。
    ```bash
    python main.py
    ```

祝你玩得开心！
