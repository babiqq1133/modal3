import modal
import time

APP_NAME = "ai-inferbox"
WORKSPACE_DIR = "/workspace"

app = modal.App.lookup(APP_NAME, create_if_missing=True)

image = (
    modal.Image.debian_slim()
    .apt_install("curl")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path=WORKSPACE_DIR)
)

def run_in_sandbox():
    # ===================== 新增：自动清理旧沙盒 =====================
    print("🧽 Cleaning old sandbox instances...")
    for sb in modal.Sandbox.list():
        try:
            if sb.app_id == app.app_id:
                print(f"🔪 Killing old sandbox: {sb.object_id}")
                sb.terminate()
        except:
            pass
    time.sleep(2)
    # ===============================================================

    print("🧪 Launching sandbox...")

    sandbox = modal.Sandbox.create(app=app, image=image,timeout=86400,region="asia-southeast1")

    # ✅ 后台执行 app.py，不阻塞 GitHub Actions
    print("🚀 Running app.py in sandbox (background)...")
    sandbox.exec("sh", "-c", f"cd {WORKSPACE_DIR} && nohup python3 app.py > /dev/null 2>&1 &")

    print("✅ Launched app.py in sandbox.")
    # 不 terminate，保留沙盒运行
    # sandbox.terminate()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", action="store_true", help="Run app.py in Modal Sandbox")
    args = parser.parse_args()

    if args.sandbox:
        run_in_sandbox()
    else:
        print("ℹ️ Use --sandbox to run in Modal Sandbox")
