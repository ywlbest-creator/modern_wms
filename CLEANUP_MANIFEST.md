# wms 文件夹清理清单

清理日期：2026-06-02

## 保留

- `modern_wms/app.py`
- `modern_wms/static/index.html`
- `modern_wms/static/styles.css`
- `modern_wms/static/app.js`
- `modern_wms/wms.db`
- `modern_wms/README.md`
- `modern_wms/SOP_VERIFICATION.md`
- `modern_wms/sop_flow_test.py`
- `modern_wms/CLEANUP_MANIFEST.md`

## 开源仓库排除内容

- 本地运行数据库 `wms.db`。
- 系统缓存、日志和临时文件。
- 与源代码无关的本地资料、安装包和办公文档。
- 根目录和新版目录中的 `.DS_Store` 系统文件。

## 清理前已完成验证

- 检查后端、前端、权限、Excel 导入导出代码。
- 执行 `python3 sop_flow_test.py`，核心业务流程自动验收通过。
