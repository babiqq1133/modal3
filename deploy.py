import modal
import time
import subprocess

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
    # ===================== 最穩清理：直接呼叫 Modal CLI 清掉所有沙盒 =====================
    print("🧽 Cleaning ALL sandboxes via modal CLI...")
    try:
        # 呼叫 modal CLI 強制清理所有沙盒
        subprocess.run(["modal", "sandbox", "prune", "--force"], check=True, capture_output=True)
        print("✅ All old sandboxes pruned.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Prune warning (may be no sandboxes): {e.stderr.decode()}")
    time.sleep(3)  # 給 Modal 後端一點時間更新狀態
    # ================================================================================

    print("🧪 Launching new sandbox...")
    sandbox = modal.Sandbox.create(app=app, image=image, timeout=86400, region="asia-southeast1")

    print("🚀 Running app.py in sandbox (background)...")
    sandbox.exec("sh", "-c", f"cd {WORKSPACE_DIR} && nohup python3 app.py > /dev/null 2>&1 &")

    print("✅ Launched app.py in sandbox. New sandbox ID:", sandbox.object_id)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sandbox", action="store_true", help="Run app.py in Modal Sandbox")
    args = parser.parse_args()

    if args.sandbox:
        run_in_sandbox()
    else:
        print("ℹ️ Use --sandbox to run in Modal Sandbox")
