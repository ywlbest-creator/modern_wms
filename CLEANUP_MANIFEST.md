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

## 已按用户要求清除的旧资料范围

- 旧 Windows WMS 客户端、安装包和配置目录。
- 旧 SOP、PPS、PPTX、CHM、DOC、DOCX 操作资料。
- 历史库存 Excel、报价单、需求开发资料。
- 根目录和新版目录中的 `.DS_Store` 系统文件。

## 清理前已完成验证

- 复读主 SOP 和现场操作指南。
- 复读新版后端、前端、权限、Excel 导入导出代码。
- 执行 `python3 modern_wms/sop_flow_test.py`，SOP 全流程自动验收通过。
