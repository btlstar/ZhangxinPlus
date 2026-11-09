# 发布准备

工具版本 0.2.0，插件核心版本 0.1.5，官方资源 92217。核心文件保持与 AkagiPlus v3.8.0-plus.2 一致。

1. 在 Windows x64 专用 Python 3.12 环境安装 requirements-lock.txt。
2. 运行 `python -m unittest test_manage test_service test_gui`。
3. 运行 `python package.py`；只打包程序、依赖、许可、说明与文件摘要。
4. 独立解压检查窗口与依赖；实际游戏界面测试由用户操作。保留原始备份，不在发布包中加入测试数据。
5. 查看 docs/COMMIT_MESSAGE.md 创建提交并推送独立仓库，创建 v0.2.0 预发布版。
6. 正文使用 docs/RELEASE_NOTES.md，附上 ZIP 和 .zip.sha256；仓库公开前核对没有个人路径或游戏资源。

当前阶段先提供本地候选版与发布材料，完成独立 GUI 的实际使用确认后再公开 Release。
