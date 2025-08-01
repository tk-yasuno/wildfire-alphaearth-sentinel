@echo off
REM AlphaEarth火災検知システム - Streamlit起動スクリプト (Windows)

echo 🔥 AlphaEarth火災検知システム - Streamlit可視化ダッシュボード
echo ================================================

REM 仮想環境のアクティベート確認
if defined VIRTUAL_ENV (
    echo ✅ 仮想環境が有効: %VIRTUAL_ENV%
) else (
    echo ⚠️  仮想環境が検出されません。推奨: 仮想環境での実行
)

REM 依存関係のインストール確認
echo 📦 依存関係を確認中...
pip install -q -r requirements_streamlit.txt

if %errorlevel% equ 0 (
    echo ✅ 依存関係のインストール完了
) else (
    echo ❌ 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

REM Streamlitアプリケーションの起動
echo 🚀 Streamlitダッシュボードを起動中...
echo 📱 ブラウザで http://localhost:8501 にアクセスしてください
echo 🛑 終了するには Ctrl+C を押してください
echo.

streamlit run streamlit_fire_dashboard.py --server.port 8501 --server.address localhost

echo 👋 ダッシュボードが終了しました
pause
