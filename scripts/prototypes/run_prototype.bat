@echo off
echo ========================================
echo 战役一验证原型：持续规划 + 伏笔账本
echo ========================================
echo.
echo 测试规模：3 幕 × 10 章 = 30 章（约 6 万字）
echo 预计耗时：30-60 分钟
echo.
echo 验证目标：
echo 1. 持续规划是否会导致逻辑断裂
echo 2. 伏笔账本能否自动埋设和回收
echo.
pause

cd /d %~dp0..
python scripts/prototype_continuous_planning.py

echo.
echo ========================================
echo 验证完成！
echo ========================================
echo.
echo 结果保存在 data/prototype_results/ 目录
pause
