import asyncio
from services.user_service import UserService

async def test_user_service():
    """测试UserService模块"""
    user_service = UserService()
    
    print("测试UserService模块...")
    
    # 测试注册功能
    print("\n1. 测试注册功能:")
    register_result = await user_service.register("test_user", "123456", "test@example.com")
    print(f"注册结果: {register_result}")
    
    # 如果注册成功，测试登录功能
    if "user_id" in register_result:
        user_id = register_result["user_id"]
        
        print(f"\n2. 测试登录功能 (user_id: {user_id}):")
        login_result = await user_service.login("test_user", "123456")
        print(f"登录结果: {login_result}")
        
        # 如果登录成功，测试获取用户信息
        if "user_id" in login_result:
            print(f"\n3. 测试获取用户信息 (user_id: {user_id}):")
            profile_result = await user_service.get_profile(user_id)
            print(f"用户信息: {profile_result}")
            
            # 测试更新用户信息
            print(f"\n4. 测试更新用户信息 (user_id: {user_id}):")
            update_data = {"level": "intermediate", "preferences": {"theme": "dark"}}
            update_result = await user_service.update_profile(user_id, update_data)
            print(f"更新结果: {update_result}")
            
            # 测试再次获取用户信息，验证更新是否成功
            print(f"\n5. 测试再次获取用户信息，验证更新是否成功:")
            updated_profile = await user_service.get_profile(user_id)
            print(f"更新后的用户信息: {updated_profile}")

if __name__ == "__main__":
    asyncio.run(test_user_service())