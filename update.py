import requests
import uuid
import time
import random
import string
import base64
import urllib.parse
import yaml
import os  # 新增

# ====================== 配置 ======================
# 从环境变量读取 GitHub Token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise Exception("请先在系统环境变量中设置 GITHUB_TOKEN！")

GITHUB_REPO = "dapei0402/jiedian"
GITHUB_BRANCH = "main"
GITHUB_PATH_V2 = "sub/v2ray.txt"
GITHUB_PATH_CLASH = "sub/clash.txt"

# 本地暂存文件
V2_LOCAL = "v2ray.txt"
CLASH_LOCAL = "clash.yaml"

# ================================================
def generate_random_email():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + "@qq.com"

# ...（省略之前的函数，例如 generate_random_user_agent、generate_headers、register_account 等，保持不变）...

def upload_to_github(local_path, repo_path):
    with open(local_path, "r", encoding="utf-8") as f:
        content = f.read()
    encoded_content = base64.b64encode(content.encode()).decode()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 先获取 SHA
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        sha = r.json()["sha"]
    else:
        sha = None
    
    data = {"message": f"Update {repo_path}", "content": encoded_content, "branch": GITHUB_BRANCH}
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=headers, json=data)
    r.raise_for_status()

# 主程序保持原样
def main():
    num = int(input("请输入需要生成的账号数量: "))
    invite_code = "ghqhsqRD"
    password = "asd789369"
    
    all_nodes = []
    
    for i in range(num):
        print(f"\n===== 正在处理第 {i+1} 个账号 =====")
        device_id = str(uuid.uuid4())
        email = generate_random_email()
        print(f"注册账号: {email} ……")
        token, auth_token = register_account(email, password, device_id)
        print("注册成功")
        
        print(f"绑定邀请码: {invite_code} ……")
        bind_invite_code(invite_code, device_id, token, auth_token)
        print("绑定成功")
        
        print("获取 VIP 节点 ……")
        nodes = get_vip_nodes(device_id, token, auth_token)
        print(f"找到 {len(nodes)} 个 VIP 节点")
        all_nodes.extend(nodes)
        time.sleep(1)
    
    # 保存 V2Ray 订阅
    os.makedirs(os.path.dirname(V2_LOCAL) or ".", exist_ok=True)
    save_v2ray_subscription(all_nodes, V2_LOCAL)
    
    # 保存 Clash 配置
    os.makedirs(os.path.dirname(CLASH_LOCAL) or ".", exist_ok=True)
    save_clash_config(all_nodes, CLASH_LOCAL)
    
    # 上传到 GitHub
    upload_to_github(V2_LOCAL, GITHUB_PATH_V2)
    upload_to_github(CLASH_LOCAL, GITHUB_PATH_CLASH)
    
    print("\n===== 上传完成 =====")
    print(f"V2Ray订阅链接: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/{GITHUB_PATH_V2}")
    print(f"Clash订阅链接: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/{GITHUB_PATH_CLASH}")

if __name__ == "__main__":
    main()

