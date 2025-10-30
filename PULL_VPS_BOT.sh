#!/bin/bash
# Pull the ACTUAL working bot from VPS to analyze

echo "==============================================================================="
echo "📥 PULLING WORKING BOT FROM VPS"
echo "==============================================================================="
echo ""

# Variables - CUSTOMIZE THESE
VPS_IP="YOUR_VPS_IP"  # e.g., 75.119.149.117
VPS_USER="root"
VPS_BOT_PATH="~/trading_bot"
LOCAL_VPS_COPY="./vps_working_bot"

echo "VPS IP: $VPS_IP"
echo "VPS User: $VPS_USER"
echo "VPS Path: $VPS_BOT_PATH"
echo "Local Copy: $LOCAL_VPS_COPY"
echo ""

echo "1️⃣ Creating local directory..."
mkdir -p $LOCAL_VPS_COPY
echo "✅ Created: $LOCAL_VPS_COPY"
echo ""

echo "2️⃣ Pulling MAIN bot files from VPS..."
echo "==============================================================================="

# Pull main orchestrator files
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*ORCHESTRATOR*.py $LOCAL_VPS_COPY/ 2>/dev/null
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*RUN*.py $LOCAL_VPS_COPY/ 2>/dev/null
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*PROFIT*.py $LOCAL_VPS_COPY/ 2>/dev/null
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*SCALP*.py $LOCAL_VPS_COPY/ 2>/dev/null

echo ""
echo "3️⃣ Pulling ENGINE files..."
echo "==============================================================================="
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*ENGINE*.py $LOCAL_VPS_COPY/ 2>/dev/null
scp -r $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*ULTRA*.py $LOCAL_VPS_COPY/ 2>/dev/null

echo ""
echo "4️⃣ Pulling CONFIGURATION files..."
echo "==============================================================================="
scp $VPS_USER@$VPS_IP:$VPS_BOT_PATH/.env $LOCAL_VPS_COPY/ 2>/dev/null
scp $VPS_USER@$VPS_IP:$VPS_BOT_PATH/*.log $LOCAL_VPS_COPY/ 2>/dev/null

echo ""
echo "5️⃣ Pulling GIT info..."
echo "==============================================================================="
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && git branch" > $LOCAL_VPS_COPY/current_branch.txt 2>/dev/null
ssh $VPS_USER@$VPS_IP "cd $VPS_BOT_PATH && git log --oneline -10" > $LOCAL_VPS_COPY/recent_commits.txt 2>/dev/null

echo ""
echo "==============================================================================="
echo "✅ VPS BOT PULLED SUCCESSFULLY"
echo "==============================================================================="
echo ""
echo "📁 Files copied to: $LOCAL_VPS_COPY/"
echo ""
ls -lh $LOCAL_VPS_COPY/
echo ""
echo "==============================================================================="
echo "📋 NEXT STEP:"
echo "Share the $LOCAL_VPS_COPY directory contents with the agent"
echo "Agent will analyze YOUR real working bot and create enhancements"
echo "==============================================================================="
