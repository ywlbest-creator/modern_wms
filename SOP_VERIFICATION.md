# YuWMS SOP 验收记录

验收日期：2026-06-05

## 验收范围

本记录覆盖 YuWMS/YuTMS 自研系统的核心业务流程、权限控制、Excel 导入导出、库存追溯、TMS 运输执行和操作日志。

## SOP 对应功能

- 个人账号登录：`/api/login`，会话 Cookie，角色权限。
- 入库通知、收货、SSCC、上架：`/api/inbounds`，创建入库单、库存批次和流水。
- RF/电脑移库：`/api/moves`，支持整托和拆分移库。
- RF枪/二维码扫描：`/api/scans`，支持识别 SSCC、库位码、GoodsID，并记录扫描来源和动作。
- 库位推荐：`/api/location-recommendations`，按货品类别、品质状态、库位优先级、容量、占用率和同品邻近推荐上架库位。
- 仓库库位在线摄像头建模：`/api/camera-scans` 记录摄像头采集，`location_model` 根据库位主数据和库存占用生成三维库位模型数据。
- 原料/产品标签模板：`/api/labels/generate`，人工录入批号后生成原料标签或产品标签，记录 Code128 条码值、二维码值、打印份数和打印流水。
- 出库通知、先进先出分配、分拣、投料确认：`/api/outbounds` 和 `/api/outbounds/{id}/confirm`，按库位优先级、BBD、SSCC 分配并扣减。
- 欠品控制：欠品单禁止确认。
- 退货/成品入库：`/api/finished/receive`，可入退货待检库位。
- 成品客户发运：`/api/finished/ship` 创建发货通知，按渠道最小剩余效期、BBD 和库位优先级分配；`/api/finished/waves` 创建波次；`/api/finished/waves/{id}/pick` 按 SSCC 合并拣货；`/api/finished/waves/{id}/review` 按订单复核；`/api/finished/waves/{id}/ship` 装车发货并扣减库存。
- TMS 运输执行：`/api/tms/shipments` 生成运单；成品发货确认后自动生成 TMS 运单；`/api/tms/shipments/{id}/dispatch` 发车；`event` 记录在途/温控事件；`pod` 记录签收；`freight` 记录独立运费账单和对账差异。
- 批次召回追溯：`/api/recalls` 按 GoodsID + 批号定位在库 SSCC 和已发运 TMS 运单，并冻结命中在库批次。
- 包材 WMS：`/api/packaging/receive`、`/api/packaging/issue` 和确认接口，覆盖包材入库、包材领用、暂扣/放行、暂扣库存不参与分配。
- 盘点差异和库存调整：`/api/counts`，差异调整仅 `admin/supervisor` 可执行，普通仓库账号只能记录无差异盘点。
- 月度/年度盘点：`/api/cycle-counts`，按全仓、类别、仓库区域或 GoodsID 生成盘点清单。
- 在库属性变更：`/api/status`，支持合格、待检、暂扣、隔离、冻结。
- 库存查询和库位查询：库存页面、全局搜索、导出库存明细。
- Excel 导入导出：`/api/export`、`/api/import`，包含 TMS 运单、在途/温控事件、POD、运费账单、承运商绩效、渠道效期规则和召回记录导出。
- 系统操作日志：`operation_logs` 自动记录登录、导入、导出、业务操作和权限拒绝，`admin/supervisor` 可查看和导出。
- 安全库存设置和临期提醒：货品主数据设置最低库存、安全库存、临期提醒天数；`stock_warnings` 和 `expiry_warnings` 输出库存预警和临期批次。
- 智能中心：`smart.alerts` 汇总库存、临期、欠品、品质状态、盘点差异和波次进度；`/api/smart/query` 提供受控自然语言查询；`/api/smart/sop` 返回场景 SOP 步骤；`/api/smart/waves/generate` 按月台智能生成成品波次；`/api/smart/safety/apply` 将动态安全库存建议写回主数据。
- 设备部备品备件：`/api/spares/parts`、`/api/spares/receive`、`/api/spares/issue`、`/api/spares/return`、`/api/spares/count`、`/api/spares/scrap`，覆盖基础台账、入库验收、维修工单领用、旧件退库、盘点调整、报废、库存预警、食品接触件清场确认、高价值/关键件审批。
- 左侧导航拆分：入库拆为收货上架、库位推荐、入库记录；出库拆为出库通知、分配拣货、出库记录；包材、成品、TMS运输、备件、RF、标签、盘点继续保持子菜单。

## 自动验收结果

命令：

```bash
python3 modern_wms/sop_flow_test.py
```

结果：

```text
SOP_FLOW_TEST_PASS
- 未登录拦截 OK
- 管理员登录和账套重置 OK
- 智能预警中心和动态安全库存建议 OK
- TMS承运商/线路/渠道效期规则 OK
- 自然语言查询助手 OK
- 智能SOP助手 OK
- 入库通知/收货/SSCC/上架 OK
- 电脑/RF 移库 OK
- RF枪/二维码扫描接入 OK
- 库位推荐 OK
- 在线摄像头采集和三维库位模型 OK
- 原料/产品标签模板和打印记录 OK
- 在库属性变更 OK
- 盘点和库存调整 OK
- 盘点差异调整权限 OK
- 出库通知/FIFO分配/分拣/投料确认 OK
- 欠品拦截 OK
- 返品/成品入库 OK
- 成品客户发运/装车确认 OK
- TMS运输执行/温控/POD/运费 OK
- TMS独立运费账单和承运商绩效 OK
- 智能生成成品波次/多订单合并拣货 OK
- 批次召回定位到TMS运单 OK
- 渠道最小剩余效期拦截 OK
- 动态安全库存一键应用 OK
- 包材WMS和暂扣控制 OK
- 月度/年度盘点清单 OK
- Excel 导出和模板 OK
- Excel/CSV 批量导入 OK
- 安全库存设置和临期提醒 OK
- 账户权限和软件使用权限 OK
- 包材账号权限 OK
- 设备部备品备件管理 OK
- 系统操作日志记录 OK
- 验收后账套重置 OK
```

结论：当前新版 YuWMS 的核心 SOP 流程验收通过。
