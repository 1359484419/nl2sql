#!/bin/bash
# ============================================================
# NL2SQL BI Agent — 一键启动脚本
# ============================================================
# 用法: bash scripts/start.sh
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "============================================"
echo "  NL2SQL BI Agent 启动脚本"
echo "============================================"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装 Python 3.10+${NC}"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到 Node.js，请先安装${NC}"
    exit 1
fi

# ─── 步骤 1：安装后端依赖 ────────────────────────────────
echo -e "\n${YELLOW}📦 安装后端 Python 依赖...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

# ─── 步骤 2：安装前端依赖 ────────────────────────────────
echo -e "\n${YELLOW}📦 安装前端依赖...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    npm install
    cd ..
fi

# ─── 步骤 3：检查 .env ─────────────────────────────────
echo -e "\n${YELLOW}⚙️  检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  未找到 .env 文件，复制 .env.example → .env${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  请根据需要修改 .env 文件中的配置（Ollama/OpenAI/数据库）${NC}"
fi

# ─── 步骤 4：检查 Ollama ───────────────────────────────
if grep -q "USE_OLLAMA=true" .env; then
    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}⚠️  未找到 Ollama，请安装: https://ollama.com${NC}"
        echo -e "${YELLOW}  或切换到 OpenAI 模式：USE_OLLAMA=false${NC}"
    elif ! pgrep -x "ollama" > /dev/null; then
        echo -e "${YELLOW}⚠️  Ollama 未运行，正在启动...${NC}"
        ollama serve &
        sleep 3
        echo -e "${GREEN}✅ Ollama 已启动${NC}"
    fi
fi

# ─── 步骤 5：检查数据库 ────────────────────────────────
echo -e "\n${YELLOW}🗄️  检查数据库...${NC}"
DB_TYPE=$(grep "^DB_TYPE=" .env | cut -d= -f2)
if [ "$DB_TYPE" = "postgresql" ]; then
    if ! command -v psql &> /dev/null; then
        echo -e "${YELLOW}⚠️  未找到 psql，请安装 PostgreSQL 或切换到 SQLite 模式${NC}"
        echo -e "${YELLOW}  修改 .env: DB_TYPE=sqlite${NC}"
    fi
fi

# ─── 步骤 6：生成模拟数据 ───────────────────────────────
echo -e "\n${YELLOW}📊 生成模拟数据...${NC}"
source .venv/bin/activate
python -m scripts.generate_mock_data 2>/dev/null || echo -e "${YELLOW}⚠️  数据生成跳过（可能数据库未运行）${NC}"

# ─── 步骤 7：构建向量索引 ───────────────────────────────
echo -e "\n${YELLOW}🔍 构建向量索引（Milvus）...${NC}"
source .venv/bin/activate
python -c "
from backend.rag.retriever import UnifiedRetriever
try:
    retriever = UnifiedRetriever()
    retriever.build_all_indexes(drop_existing=True)
    print('✅ 向量索引构建完成')
except Exception as e:
    print(f'⚠️  索引构建跳过: {e}')
" 2>/dev/null || echo -e "${YELLOW}⚠️  索引构建跳过${NC}"

echo -e "\n============================================"
echo -e "${GREEN}✅ 启动完成！${NC}"
echo "============================================"
echo -e "后端: ${YELLOW}http://localhost:8000${NC}"
echo -e "前端: ${YELLOW}http://localhost:5173${NC}"
echo -e "API文档: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "启动后端: ${GREEN}uvicorn backend.main:app --reload --port 8000${NC}"
echo -e "启动前端: ${GREEN}cd frontend && npm run dev${NC}"
echo ""
