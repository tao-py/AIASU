#!/usr/bin/env python3
"""
UI层测试运行器
运行所有UI测试并生成报告
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_unit_tests():
    """运行单元测试"""
    print("=" * 60)
    print("运行单元测试")
    print("=" * 60)

    test_files = [
        "Ui/test/unit/test_theme.py",
        "Ui/test/unit/test_components.py",
        # 可以添加更多单元测试文件
    ]

    results = []
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n运行 {test_file}...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✓ {test_file} 通过")
            else:
                print(f"✗ {test_file} 失败")
                print(result.stdout)
                print(result.stderr)

            results.append(
                {
                    "file": test_file,
                    "passed": result.returncode == 0,
                    "output": result.stdout,
                    "errors": result.stderr,
                }
            )
        else:
            print(f"⚠ {test_file} 不存在，跳过")

    return results


def run_integration_tests():
    """运行集成测试"""
    print("\n" + "=" * 60)
    print("运行集成测试")
    print("=" * 60)

    # 这里可以添加集成测试
    print("集成测试将在后续版本中实现")
    return []


def run_performance_tests():
    """运行性能测试"""
    print("\n" + "=" * 60)
    print("运行性能测试")
    print("=" * 60)

    # 这里可以添加性能测试
    print("性能测试将在后续版本中实现")
    return []


def run_demo():
    """运行演示程序"""
    print("\n" + "=" * 60)
    print("运行UI演示程序")
    print("=" * 60)

    try:
        from Ui.test_framework import run_demo

        print("启动UI演示程序...")
        run_demo()
        return True
    except Exception as e:
        print(f"演示程序运行失败: {e}")
        return False


def print_summary(unit_results, integration_results, performance_results):
    """打印测试摘要"""
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)

    # 单元测试摘要
    if unit_results:
        passed = sum(1 for r in unit_results if r["passed"])
        total = len(unit_results)
        print(f"单元测试: {passed}/{total} 通过")

        if passed < total:
            print("失败的测试:")
            for result in unit_results:
                if not result["passed"]:
                    print(f"  - {result['file']}")

    # 集成测试摘要
    print(f"集成测试: 待实现")

    # 性能测试摘要
    print(f"性能测试: 待实现")

    # 总体结果
    total_passed = sum(1 for r in unit_results if r["passed"]) if unit_results else 0
    total_tests = len(unit_results) if unit_results else 0

    print(f"\n总体: {total_passed}/{total_tests} 测试通过")

    if total_passed == total_tests and total_tests > 0:
        print("✓ 所有测试通过!")
        return True
    else:
        print("✗ 部分测试失败")
        return False


def main():
    """主函数"""
    print("AIASU UI层测试运行器")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    print(f"项目根目录: {project_root}")

    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            return run_demo()
        elif sys.argv[1] == "--unit":
            unit_results = run_unit_tests()
            return print_summary(unit_results, [], [])
        elif sys.argv[1] == "--integration":
            integration_results = run_integration_tests()
            return True  # 集成测试待实现
        elif sys.argv[1] == "--performance":
            performance_results = run_performance_tests()
            return True  # 性能测试待实现
        elif sys.argv[1] == "--help":
            print("\n使用方法:")
            print("  python run_tests.py              # 运行所有测试")
            print("  python run_tests.py --demo       # 运行演示程序")
            print("  python run_tests.py --unit       # 运行单元测试")
            print("  python run_tests.py --integration # 运行集成测试")
            print("  python run_tests.py --performance # 运行性能测试")
            print("  python run_tests.py --help       # 显示帮助")
            return True

    # 运行所有测试
    print("开始运行所有测试...")

    unit_results = run_unit_tests()
    integration_results = run_integration_tests()
    performance_results = run_performance_tests()

    success = print_summary(unit_results, integration_results, performance_results)

    # 询问是否运行演示程序
    if success:
        print("\n测试通过! 是否运行演示程序? (y/n): ", end="")
        response = input().strip().lower()
        if response == "y" or response == "是":
            run_demo()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
