"""
大模型响应速度测试

测试 qwen3.5-flash 和 qwen-plus 两种模型的流式响应速度
重点测量首字响应时间(TTFT - Time To First Token)
"""

import asyncio
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai.llm_service import LLMService
from app.core.config import settings


async def test_model_stream_speed(model_name: str, test_message: str, test_round: int = 1):
    """测试单个模型的流式响应速度"""
    
    llm_service = LLMService(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model_name=model_name,
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"\n{'='*60}")
    print(f"测试模型: {model_name}")
    print(f"测试轮次: {test_round}")
    print(f"测试问题: {test_message}")
    print(f"{'='*60}")
    
    start_time = time.time()
    first_chunk_time = None
    chunk_count = 0
    total_content = ""
    
    try:
        async for chunk in llm_service.chat_stream_async(test_message):
            if first_chunk_time is None:
                first_chunk_time = time.time()
                ttft = (first_chunk_time - start_time) * 1000
                print(f"\n首字响应时间(TTFT): {ttft:.0f}ms")
                print(f"\n模型回复内容:\n")
            
            chunk_count += 1
            total_content += chunk
            print(chunk, end='', flush=True)
        
        total_time = (time.time() - start_time) * 1000
        print(f"\n\n总响应时间: {total_time:.0f}ms")
        print(f"生成token数: {chunk_count}")
        print(f"平均生成速度: {chunk_count / (total_time / 1000):.1f} tokens/s")
        
        return {
            "model": model_name,
            "ttft_ms": ttft if first_chunk_time else None,
            "total_time_ms": total_time,
            "chunk_count": chunk_count,
            "success": True
        }
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        return {
            "model": model_name,
            "ttft_ms": None,
            "total_time_ms": None,
            "chunk_count": 0,
            "success": False,
            "error": str(e)
        }


async def run_comparison_test():
    """运行对比测试"""
    
    models = ["qwen3.5-flash", "qwen-plus"]
    test_messages = [
        "什么是Python列表?",
        "如何定义一个函数?",
        "Python中的装饰器是什么?"
    ]
    
    results = []
    
    print("\n" + "="*60)
    print("大模型响应速度对比测试")
    print("="*60)
    print(f"\n测试目标: 验证首字响应时间是否 <= 2000ms (2秒)")
    print(f"API地址: {settings.LLM_BASE_URL}")
    
    for round_num, message in enumerate(test_messages, 1):
        print(f"\n\n{'#'*60}")
        print(f"测试轮次 {round_num}/{len(test_messages)}")
        print(f"{'#'*60}")
        
        for model in models:
            result = await test_model_stream_speed(model, message, round_num)
            results.append(result)
            await asyncio.sleep(1)
    
    print("\n\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    for model in models:
        model_results = [r for r in results if r["model"] == model and r["success"]]
        if model_results:
            avg_ttft = sum(r["ttft_ms"] for r in model_results) / len(model_results)
            avg_total = sum(r["total_time_ms"] for r in model_results) / len(model_results)
            success_count = len(model_results)
            
            print(f"\n{model}:")
            print(f"  成功次数: {success_count}/{len(test_messages)}")
            print(f"  平均首字响应时间(TTFT): {avg_ttft:.0f}ms")
            print(f"  平均总响应时间: {avg_total:.0f}ms")
            print(f"  是否满足 <= 2s 要求: {'✅ 是' if avg_ttft <= 2000 else '❌ 否'}")
        else:
            print(f"\n{model}: 测试失败")
    
    print("\n" + "="*60)
    print("详细结果:")
    print("="*60)
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        ttft_str = f"{result['ttft_ms']:.0f}ms" if result["ttft_ms"] else "N/A"
        total_str = f"{result['total_time_ms']:.0f}ms" if result["total_time_ms"] else "N/A"
        print(f"{i}. {result['model']:15} | TTFT: {ttft_str:8} | 总时间: {total_str:8} | {status}")


async def main():
    """主函数"""
    await run_comparison_test()


if __name__ == "__main__":
    asyncio.run(main())
