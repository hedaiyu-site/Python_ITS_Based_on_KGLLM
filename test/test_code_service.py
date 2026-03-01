import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.code_service import CodeService

async def test_code_service():
    """测试CodeService功能"""
    print("开始测试CodeService...")
    
    # 创建CodeService实例
    code_service = CodeService()
    
    # 测试1: 代码分析
    print("\n1. 测试代码分析:")
    test_code = """
def calculate_sum(a, b):
    result = a + b
    return result

print(calculate_sum(5, 3))
"""
    
    try:
        analysis = await code_service.analyze(test_code, "python")
        print(f"语法错误: {analysis['syntax_errors']}")
        print(f"风格问题: {analysis['style_issues']}")
        print(f"复杂度评分: {analysis['complexity_score']}")
        print(f"改进建议: {analysis['suggestions']}")
    except Exception as e:
        print(f"测试1失败: {str(e)}")
    
    # 测试2: 代码纠错
    print("\n2. 测试代码纠错:")
    buggy_code = """
def calculate_sum(a, b):
    result = a + b
    return reslt  # 故意拼写错误

print(calculate_sum(5, 3))
"""
    
    try:
        correction = await code_service.correct(buggy_code, "python")
        print(f"纠正后的代码: {correction['corrected_code']}")
        print(f"纠错说明: {correction['explanation']}")
    except Exception as e:
        print(f"测试2失败: {str(e)}")
    
    # 测试3: 代码生成
    print("\n3. 测试代码生成:")
    prompt = "生成一个计算斐波那契数列的函数"
    
    try:
        generation = await code_service.generate(prompt, "python")
        print(f"生成的代码: {generation['generated_code']}")
    except Exception as e:
        print(f"测试3失败: {str(e)}")
    
    # 测试4: 代码解释
    print("\n4. 测试代码解释:")
    complex_code = """
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in [x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
"""
    
    try:
        explanation = await code_service.explain(complex_code, "python")
        print(f"代码解释: {explanation['explanation']}")
        print(f"关键词: {explanation['keywords']}")
    except Exception as e:
        print(f"测试4失败: {str(e)}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    asyncio.run(test_code_service())