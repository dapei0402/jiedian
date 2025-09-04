import requests
import uuid
import time
import random
import string
import base64
import urllib.parse
import yaml

# ====================== 配置 ======================
GITHUB_TOKEN = "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"
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

def generate_random_user_agent():
    user_agents = [
        "okhttp/4.12.0",
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(user_agents)

def generate_headers(device_id, token=None, auth_token=None):
    headers = {
        "deviceid": device_id,
        "devicetype": "1",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "api.tianmiao.icu",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": generate_random_user_agent()
    }
    if token and auth_token:
        headers["token"] = token
        headers["authtoken"] = auth_token
    return headers

def create_session():
    session = requests.Session()
    return session

def register_account(email, password, device_id):
    url = "https://api.tianmiao.icu/api/register"
    data = {"email": email, "invite_code": "", "password": password, "password_word": password}
    headers = generate_headers(device_id)
    r = requests.post(url, headers=headers, json=data, timeout=10)
    r.raise_for_status()
    result = r.json()
    if result.get("code") != 1:
        raise Exception(f"注册失败: {result.get('message')}")
    return result["data"]["auth_data"], result["data"]["token"]

def bind_invite_code(invite_code, device_id, token, auth_token):
    url = "https://api.tianmiao.icu/api/bandInviteCode"
    data = {"invite_code": invite_code}
    headers = generate_headers(device_id, token, auth_token)
    r = requests.post(url, headers=headers, json=data, timeout=10)
    r.raise_for_status()
    result = r.json()
    if result.get("code") != 1:
        raise Exception(f"邀请码绑定失败: {result.get('message')}")
    return True

def get_vip_nodes(device_id, token, auth_token):
    url = "https://api.tianmiao.icu/api/nodeListV2"
    data = {"protocol":"all","include_ss":"1","include_shadowsocks":"1","include_trojan":"1"}
    headers = generate_headers(device_id, token, auth_token)
    r = requests.post(url, headers=headers, json=data, timeout=10)
    r.raise_for_status()
    result = r.json()
    if result.get("code") != 1:
        raise Exception(f"获取节点失败: {result.get('message')}")
    vip_nodes = []
    for group in result["data"]:
        if group["type"]=="vip" and "node" in group:
            for node in group["node"]:
                if isinstance(node, dict) and "url" in node:
                    vip_nodes.append(node)
    return vip_nodes

def save_v2ray_subscription(nodes, file_path):
    urls = [node["url"] for node in nodes if "url" in node]
    sub_text = "\n".join(urls)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sub_text)
    return base64.b64encode(sub_text.encode()).decode()

def save_clash_config(nodes, file_path):
    clash_config = {"proxies":[],"proxy-groups":[],"rules":[]}
    clash_config["proxies"] = nodes
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)

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
    save_v2ray_subscription(all_nodes, V2_LOCAL)
    # 保存 Clash 配置
    save_clash_config(all_nodes, CLASH_LOCAL)
    
    # 上传到 GitHub
    upload_to_github(V2_LOCAL, GITHUB_PATH_V2)
    upload_to_github(CLASH_LOCAL, GITHUB_PATH_CLASH)
    
    print("\n===== 上传完成 =====")
    print(f"V2Ray订阅链接: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/{GITHUB_PATH_V2}")
    print(f"Clash订阅链接: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/{GITHUB_PATH_CLASH}")

if __name__ == "__main__":
    main()

