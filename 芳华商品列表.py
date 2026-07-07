import requests
#参数 "pageNum": 1, "pageSize": 199, 这里可调节，------form大飞
def get_goods_list():
    url = "https://api.cdwjyyh.com/app/integral/getIntegralGoodsList"
    
    # 请求参数保持不变
    params = {
        "pageNum": 1,
        "pageSize": 199,
        "keyword": ""
    }
    
    # 基础请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; 22081212C Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/139.0.7296.98 Mobile Safari/537.36 uni-app",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 确保请求成功
        if response.status_code == 200:
            result = response.json()
            
            if result.get("code") == 200:
                goods_list = result.get("data", {}).get("list", [])
                total_items = result.get("data", {}).get("total", 0)
                
                print(f"✅ 成功获取商品，当前第 {params['pageNum']} 页 (总商品数: {total_items})\n" + "="*40)
                
                # 遍历并格式化输出商品列表
                for index, goods in enumerate(goods_list, 1):
                    goods_id = goods.get("goodsId")
                    name = goods.get("goodsName")
                    price = goods.get("otPrice")
                    integral = goods.get("integral")
                    
                    print(f"{index}. {name}")
                    print(f"   ├─ 商品 ID : {goods_id}")
                    print(f"   ├─ 市场价  : ¥{price:.2f}")
                    print(f"   └─ 兑换芳华币: {integral}")
                print("="*40)
            else:
                print(f"❌ 接口返回错误: {result.get('msg')}")
        else:
            print(f"❌ HTTP 请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 脚本执行异常: {e}")

if __name__ == "__main__":
    get_goods_list()