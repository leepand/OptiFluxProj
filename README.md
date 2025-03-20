# OptiFluxProj
机器学习项目管理

# 设置正确的FLASK_APP
export FLASK_APP=run.py

# 初始化迁移仓库
flask db init

# 生成迁移脚本
flask db migrate -m "initial migration"

# 应用迁移
flask db upgrade