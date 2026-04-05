@echo off
echo ========================================
echo 战役一验证原型（模拟版）
echo ========================================
echo.
echo 特点：
echo - 零成本（不调用真实 LLM）
echo - 5 分钟内完成 30 章流程验证
echo - 验证架构流程是否通顺
echo.
pause

cd /d %~dp0..
python scripts/prototype_mock.py

echo.
echo ========================================
echo 验证完成！
echo ========================================
echo.
echo 结果保存在 data/prototype_results/ 目录
pause
