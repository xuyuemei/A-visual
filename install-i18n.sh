#!/bin/bash

echo "🌍 安装C-Voices多语言支持依赖..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    echo "建议使用Node.js 18+版本"
    exit 1
fi

# 检查npm或yarn
if command -v yarn &> /dev/null; then
    PKG_MANAGER="yarn"
    echo "✅ 检测到yarn包管理器"
elif command -v npm &> /dev/null; then
    PKG_MANAGER="npm"
    echo "✅ 检测到npm包管理器"
else
    echo "❌ 未检测到npm或yarn包管理器"
    exit 1
fi

# 进入前端目录
cd /data/hlt/A-visual/bishework/front_work/front

echo "📦 安装i18n依赖包..."
if [ "$PKG_MANAGER" = "yarn" ]; then
    yarn add react-i18next i18next i18next-browser-languagedetector
else
    npm install react-i18next i18next i18next-browser-languagedetector
fi

echo "✅ 多语言依赖安装完成！"
echo ""
echo "🚀 启动开发服务器："
echo "   cd /data/hlt/A-visual/bishework/front_work/front"
if [ "$PKG_MANAGER" = "yarn" ]; then
    echo "   yarn dev"
else
    echo "   npm run dev"
fi
echo ""
echo "🌐 多语言功能已集成，现在可以在右上角切换中英文！"
