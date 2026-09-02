#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, timedelta
from http.cookiejar import CookieJar


BASE_URL = os.environ.get("YU_WMS_URL", "http://127.0.0.1:8765").rstrip("/")


class WMSClient:
    def __init__(self) -> None:
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPCookieProcessor(self.cookie_jar),
        )

    def request(self, method: str, path: str, body: bytes | None = None, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
        request = urllib.request.Request(f"{BASE_URL}{path}", data=body, method=method, headers=headers or {})
        try:
            with self.opener.open(request, timeout=10) as response:
                return response.status, dict(response.headers), response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), exc.read()

    def get_json(self, path: str) -> tuple[int, dict]:
        status, _, body = self.request("GET", path)
        return status, json.loads(body.decode("utf-8") or "{}")

    def get_bytes(self, path: str) -> tuple[int, dict[str, str], bytes]:
        return self.request("GET", path)

    def post_json(self, path: str, payload: dict) -> tuple[int, dict]:
        status, _, body = self.request(
            "POST",
            path,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            {"Content-Type": "application/json"},
        )
        return status, json.loads(body.decode("utf-8") or "{}")

    def post_multipart(self, path: str, fields: dict[str, str], file_field: str, filename: str, content: bytes, content_type: str) -> tuple[int, dict]:
        boundary = "YuWMSBoundarySOP"
        chunks: list[bytes] = []
        for key, value in fields.items():
            chunks.append(f"--{boundary}\r\n".encode())
            chunks.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            chunks.append(str(value).encode("utf-8"))
            chunks.append(b"\r\n")
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode())
        chunks.append(f"Content-Type: {content_type}\r\n\r\n".encode())
        chunks.append(content)
        chunks.append(b"\r\n")
        chunks.append(f"--{boundary}--\r\n".encode())
        status, _, body = self.request("POST", path, b"".join(chunks), {"Content-Type": f"multipart/form-data; boundary={boundary}"})
        return status, json.loads(body.decode("utf-8") or "{}")


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def item_by_id(rows: list[dict], key: str, value: str) -> dict | None:
    return next((row for row in rows if row.get(key) == value), None)


def login(client: WMSClient, username: str, password: str) -> dict:
    status, data = client.post_json("/api/login", {"username": username, "password": password})
    expect(status == 200, f"{username} 登录失败：{status} {data}")
    return data


def reset_demo(client: WMSClient) -> dict:
    status, data = client.post_json("/api/reset", {})
    expect(status == 200, f"重置失败：{status} {data}")
    return data


def id_from_notice(data: dict) -> str:
    notice = str(data.get("notice") or "")
    return notice.rsplit("：", 1)[-1].strip()


def main() -> int:
    results: list[str] = []
    admin = WMSClient()

    status, data = admin.get_json("/api/bootstrap")
    expect(status == 401, f"未登录 bootstrap 应返回 401，实际 {status} {data}")
    results.append("未登录拦截 OK")

    login(admin, "admin", "admin123")
    reset_demo(admin)
    results.append("管理员登录和账套重置 OK")

    status, data = admin.get_json("/api/bootstrap")
    expect(status == 200 and data.get("smart"), "智能中心数据未返回")
    expect(data["smart"]["alerts"], "智能预警中心应有演示风险项")
    expect(data["smart"]["safety_recommendations"], "动态安全库存建议未生成")
    expect(len(data["tms"]["carriers"]) == 3, "TMS承运商种子数据应为3个")
    expect(len(data["tms"]["lanes"]) == 3, "TMS线路种子数据应为3条")
    expect(len(data["tms"].get("channel_rules", [])) >= 12, "渠道效期规则未初始化")
    results.append("智能预警中心和动态安全库存建议 OK")
    results.append("TMS承运商/线路/渠道效期规则 OK")

    status, data = admin.post_json("/api/smart/query", {"question": "FG-DOG-ADULT-10KG 还有多少库存"})
    answer = data.get("smart_answer", {})
    expect(status == 200 and answer.get("intent") == "库存查询" and answer.get("rows"), "自然语言库存查询助手失败")
    status, data = admin.post_json("/api/smart/query", {"question": "哪些批次临期"})
    answer = data.get("smart_answer", {})
    expect(status == 200 and answer.get("intent") == "临期查询" and "临期" in answer.get("answer", ""), "自然语言临期查询助手失败")
    results.append("自然语言查询助手 OK")

    status, data = admin.post_json("/api/smart/sop", {"question": "成品发货怎么做"})
    sop = data.get("smart_sop", {})
    expect(status == 200 and sop.get("topic") == "成品发货" and any("发货通知" in step for step in sop.get("steps", [])), "智能SOP助手未返回成品发货步骤")
    results.append("智能SOP助手 OK")

    inbound_payload = {
        "goods_id": "3726",
        "qty": 120,
        "supplier": "SOP入库验证",
        "supplier_batch": "SOP-BATCH-3726",
        "production_date": "2026-06-02",
        "expiry_date": "2026-12-31",
        "po_no": "PO-SOP-3726",
        "location_id": "RM-A01-01",
        "quality_status": "合格",
        "owner": "MARS-RMR",
        "sscc": "SOPSSCC3726001",
        "remark": "SOP 6.2-6.4 入库/收货/上架验证",
    }
    status, data = admin.post_json("/api/inbounds", inbound_payload)
    expect(status == 200, f"入库失败：{status} {data}")
    stock = item_by_id(data["inventory"], "sscc", "SOPSSCC3726001")
    expect(stock and stock["qty"] == 120 and stock["location_id"] == "RM-A01-01", "入库后库存不正确")
    results.append("入库通知/收货/SSCC/上架 OK")

    status, data = admin.post_json("/api/moves", {"sscc": "SOPSSCC3726001", "to_location": "RM-A02-01", "operator": "SOP叉车", "remark": "SOP 6.5 移库验证"})
    expect(status == 200, f"移库失败：{status} {data}")
    stock = item_by_id(data["inventory"], "sscc", "SOPSSCC3726001")
    expect(stock and stock["location_id"] == "RM-A02-01", "移库后库位不正确")
    results.append("电脑/RF 移库 OK")

    status, data = admin.post_json("/api/scans", {"code": "SOPSSCC3726001", "scan_type": "RF枪", "action": "查询"})
    expect(status == 200 and data["scan_result"]["parsed_type"] == "SSCC" and data["scan_result"]["location_id"] == "RM-A02-01", "RF枪 SSCC 扫描识别失败")
    status, data = admin.post_json("/api/scans", {"code": "RM-A02-01", "scan_type": "二维码", "action": "目标库位"})
    expect(status == 200 and data["scan_result"]["parsed_type"] == "LOCATION", "二维码库位扫描识别失败")
    results.append("RF枪/二维码扫描接入 OK")

    status, data = admin.post_json("/api/location-recommendations", {"goods_id": "3726", "qty": 120, "quality_status": "合格"})
    expect(status == 200 and data["location_recommendations"] and data["location_recommendations"][0]["area"] in {"原料仓", "红蓝通道"}, "合格原料库位推荐失败")
    status, data = admin.post_json("/api/location-recommendations", {"goods_id": "3726", "qty": 1, "quality_status": "冻结"})
    expect(status == 200 and any(item["id"] == "QC-HOLD" for item in data["location_recommendations"]), "冻结/隔离物料未推荐质量区")
    results.append("库位推荐 OK")

    status, data = admin.post_json("/api/camera-scans", {"location_id": "RM-A02-01", "camera_name": "SOP-CAM-01", "image_note": "SOP库位在线建模采集"})
    expect(status == 200 and any(row["location_id"] == "RM-A02-01" for row in data["camera_scans"]), "摄像头库位采集记录失败")
    model_row = item_by_id(data["location_model"], "id", "RM-A02-01")
    expect(model_row and model_row["last_camera_scan"], "三维库位模型未关联最近采集")
    results.append("在线摄像头采集和三维库位模型 OK")

    status, data = admin.post_json("/api/labels/generate", {
        "label_type": "原料标签",
        "goods_id": "3726",
        "batch_no": "SOP-LABEL-RM-001",
        "supplier_batch": "SOP-BATCH-3726",
        "production_date": "2026-06-02",
        "expiry_date": "2026-12-31",
        "qty": 110,
        "unit": "kg",
        "location_id": "RM-A02-01",
        "sscc": "SOPSSCC3726001",
        "quality_status": "合格",
        "code_type": "条码+二维码",
        "copies": 2,
    })
    expect(status == 200 and data["current_label"]["label_type"] == "原料标签" and data["current_label"]["barcode_value"] == "SOPSSCC3726001", "原料标签生成失败")
    status, data = admin.post_json("/api/labels/generate", {
        "label_type": "产品标签",
        "goods_id": "FG-DOG-ADULT-10KG",
        "batch_no": "SOP-LABEL-FG-001",
        "production_date": "2026-06-02",
        "expiry_date": "2027-06-02",
        "qty": 50,
        "location_id": "FG-A01-01",
        "quality_status": "合格",
        "code_type": "条码",
    })
    expect(status == 200 and data["current_label"]["label_type"] == "产品标签" and any(row["batch_no"] == "SOP-LABEL-RM-001" for row in data["label_prints"]), "产品标签生成或打印记录失败")
    status, _, body = admin.get_bytes("/api/export?dataset=label_prints")
    expect(status == 200 and body.startswith(b"PK"), "标签打印记录导出失败")
    results.append("原料/产品标签模板和打印记录 OK")

    status, data = admin.post_json("/api/status", {"sscc": "SOPSSCC3726001", "quality_status": "冻结", "reason": "SOP 6.9 属性变更验证"})
    expect(status == 200, f"属性冻结失败：{status} {data}")
    stock = item_by_id(data["inventory"], "sscc", "SOPSSCC3726001")
    expect(stock and stock["quality_status"] == "冻结", "冻结状态未生效")
    status, data = admin.post_json("/api/status", {"sscc": "SOPSSCC3726001", "quality_status": "合格", "reason": "SOP 6.9 放行验证"})
    expect(status == 200, f"属性放行失败：{status} {data}")
    results.append("在库属性变更 OK")

    status, data = admin.post_json("/api/counts", {"sscc": "SOPSSCC3726001", "actual_qty": 110, "reason": "SOP 6.8 盘点差异调整验证"})
    expect(status == 200, f"盘点失败：{status} {data}")
    stock = item_by_id(data["inventory"], "sscc", "SOPSSCC3726001")
    expect(stock and stock["qty"] == 110, "盘点后实盘数量未同步")
    expect(data["counts"][0]["diff_qty"] == -10, "盘点差异未记录")
    results.append("盘点和库存调整 OK")

    raw_counter = WMSClient()
    login(raw_counter, "raw", "raw123")
    status, deny = raw_counter.post_json("/api/counts", {"sscc": "SOPSSCC3726001", "actual_qty": 109, "count_type": "日常盘点", "scope": "原料仓", "reason": "SOP普通账号差异调整拒绝"})
    expect(status == 403 and "系统差异调整" in deny.get("error", ""), "非主管/管理员账号不应允许系统差异调整")
    status, raw_data = raw_counter.post_json("/api/counts", {"sscc": "SOPSSCC3726001", "actual_qty": 110, "count_type": "月度盘点", "scope": "原料仓", "reason": "SOP普通账号无差异记录"})
    raw_count = next((row for row in raw_data.get("counts", []) if row["sscc"] == "SOPSSCC3726001" and row["count_type"] == "月度盘点" and row["adjusted"] == 0), None)
    expect(status == 200 and raw_count, "普通账号应允许无差异盘点记录")
    results.append("盘点差异调整权限 OK")

    status, data = admin.post_json("/api/outbounds", {"goods_id": "3637", "qty": 1000, "destination": "粉碎投料", "bin_no": "BIN-01", "courbon_connected": True, "remark": "SOP 6.6 出库分配验证"})
    expect(status == 200, f"出库分配失败：{status} {data}")
    outbound_id = id_from_notice(data)
    outbound = item_by_id(data["outbounds"], "id", outbound_id)
    expect(outbound is not None, "出库单未返回到列表")
    expect(outbound["goods_id"] == "3637" and outbound["status"] == "已分配", "出库单状态不正确")
    expect(outbound["allocated_qty"] == 1000 and outbound["shortage_qty"] == 0, "出库分配数量不正确")
    expect(outbound["lines"][0]["location_id"] == "RM-S01", "未优先分配取样后优先货位")
    expect(sum(line["qty"] for line in outbound["lines"]) == 1000, "分拣明细数量不正确")
    status, data = admin.post_json(f"/api/outbounds/{outbound['id']}/confirm", {})
    expect(status == 200, f"出库确认失败：{status} {data}")
    confirmed = item_by_id(data["outbounds"], "id", outbound["id"])
    expect(confirmed and confirmed["status"] == "已完成", "出库确认后状态不正确")
    first_stock = item_by_id(data["inventory"], "sscc", "SSCC202606020002")
    expect(first_stock is None, "优先货位整托出库后不应继续显示在库")
    second_stock = item_by_id(data["inventory"], "sscc", "SSCC202606020001")
    expect(second_stock and second_stock["qty"] == 1150 and second_stock["reserved_qty"] == 0, "跨托分配扣减不正确")
    results.append("出库通知/FIFO分配/分拣/投料确认 OK")

    status, data = admin.post_json("/api/outbounds", {"goods_id": "3726", "qty": 999999, "destination": "欠品验证", "bin_no": "BIN-99"})
    shortage_id = id_from_notice(data)
    shortage = item_by_id(data["outbounds"], "id", shortage_id)
    expect(status == 200 and shortage and shortage["status"] == "欠品", "欠品单未正确生成")
    status, deny = admin.post_json(f"/api/outbounds/{shortage_id}/confirm", {})
    expect(status == 400 and "欠品" in deny.get("error", ""), "欠品单不应允许确认")
    results.append("欠品拦截 OK")

    status, data = admin.post_json("/api/finished/receive", {
        "goods_id": "FG-DOG-ADULT-10KG",
        "qty": 30,
        "location_id": "FG-RETURN-01",
        "production_line": "退货复核",
        "supplier_batch": "FG-RETURN-SOP",
        "production_date": "2026-06-02",
        "expiry_date": "2027-06-02",
        "po_no": "TR-SOP-001",
        "quality_status": "待检",
        "sscc": "SOPFGRETURN001",
        "remark": "SOP 6.7 退货/成品入库验证",
    })
    expect(status == 200, f"成品退货入库失败：{status} {data}")
    fg_return = item_by_id(data["inventory"], "sscc", "SOPFGRETURN001")
    expect(fg_return and fg_return["location_id"] == "FG-RETURN-01" and fg_return["quality_status"] == "待检", "成品退货入库库存不正确")
    results.append("返品/成品入库 OK")

    status, data = admin.post_json("/api/finished/ship", {"goods_id": "FG-DOG-ADULT-10KG", "qty": 50, "customer": "SOP客户", "order_no": "SO-SOP-001", "ship_dock": "DOCK-FG-01"})
    expect(status == 200, f"成品发运分配失败：{status} {data}")
    fg_out_id = id_from_notice(data)
    fg_out = item_by_id(data["finished"]["outbounds"], "id", fg_out_id)
    expect(fg_out is not None, "成品发运单未返回到列表")
    expect(fg_out["status"] == "已分配" and fg_out["allocated_qty"] == 50, "成品发运分配不正确")
    status, data = admin.post_json(f"/api/outbounds/{fg_out['id']}/confirm", {})
    expect(status == 200, f"成品装车确认失败：{status} {data}")
    results.append("成品客户发运/装车确认 OK")

    tms_shipment = next((item for item in data["tms"]["shipments"] if item.get("source_outbound_id") == fg_out_id), None)
    expect(tms_shipment and tms_shipment["status"] == "待发车", "成品装车后未自动生成TMS运单")
    tms_id = urllib.parse.quote(tms_shipment["id"], safe="")
    driver_task = next((item for item in data["tms"].get("driver_tasks", []) if item.get("shipment_id") == tms_shipment["id"]), None)
    expect(driver_task and driver_task["task_status"] == "待接单", "TMS运单未自动派发司机任务")
    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/driver", {"action": "已接单", "pod_note": "SOP司机接单"})
    expect(status == 200, f"TMS司机接单失败：{status} {data}")
    driver_task = next((item for item in data["tms"].get("driver_tasks", []) if item.get("shipment_id") == urllib.parse.unquote(tms_id)), None)
    expect(driver_task and driver_task["task_status"] == "已接单", "TMS司机任务接单状态不正确")
    results.append("TMS司机任务自动派发/接单 OK")

    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/dispatch", {"vehicle_no": "苏E-TMS01", "driver": "SOP运输司机", "seal_no": "TMSSEAL01"})
    expect(status == 200, f"TMS发车失败：{status} {data}")
    tms_shipment = item_by_id(data["tms"]["shipments"], "id", tms_shipment["id"])
    expect(tms_shipment and tms_shipment["status"] == "已发车", "TMS发车状态不正确")
    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/event", {"event_type": "温度上报", "location_text": "SOP在途点", "temperature": 6})
    expect(status == 200, f"TMS正常温控事件失败：{status} {data}")
    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/event", {"event_type": "温度上报", "location_text": "SOP在途点", "temperature": 12})
    expect(status == 200, f"TMS超温事件失败：{status} {data}")
    tms_shipment = item_by_id(data["tms"]["shipments"], "id", urllib.parse.unquote(tms_id))
    expect(tms_shipment and tms_shipment["exception_flag"] == 1 and tms_shipment["status"] == "异常", "TMS超温异常未触发")
    status, data = admin.post_json("/api/tms/iot", {
        "shipment_id": urllib.parse.unquote(tms_id),
        "device_id": "IOT-SOP-01",
        "location_text": "SOP IoT在途点",
        "temperature": 14,
        "humidity": 68,
        "latitude": 31.2304,
        "longitude": 121.4737,
        "reefer_status": "运行",
        "speed": 72,
        "door_open": True,
        "note": "SOP IoT超温验证",
    })
    expect(status == 200, f"TMS IoT遥测失败：{status} {data}")
    telemetry = next((item for item in data["tms"].get("telemetry", []) if item.get("device_id") == "IOT-SOP-01"), None)
    expect(telemetry and telemetry["risk_level"] == "高", "IoT超温遥测未识别为高风险")
    expect(data["tms"]["control_tower"]["high_risk_telemetry"] >= 1, "TMS控制塔未统计IoT高风险")
    results.append("TMS IoT/GPS温控自动接入 OK")

    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/pod", {"signed_by": "SOP客户仓管", "received_qty": 50, "damaged_qty": 0, "shortage_qty": 0})
    expect(status == 200, f"TMS POD失败：{status} {data}")
    status, data = admin.post_json(f"/api/tms/shipments/{tms_id}/freight", {"actual_fee": 260})
    expect(status == 200, f"TMS运费对账失败：{status} {data}")
    tms_shipment = item_by_id(data["tms"]["shipments"], "id", urllib.parse.unquote(tms_id))
    expect(tms_shipment and float(tms_shipment["actual_fee"]) == 260, "TMS实际运费未写入")
    freight_bill = next((bill for bill in data["tms"].get("freight_bills", []) if bill["shipment_id"] == urllib.parse.unquote(tms_id)), None)
    expect(freight_bill and float(freight_bill["actual_fee"]) == 260 and freight_bill["billing_status"] == "差异", "TMS独立运费账单未正确写入")
    performance = next((row for row in data["tms"].get("performance", []) if row["carrier_code"] == tms_shipment["carrier_code"]), None)
    expect(performance and performance["shipment_count"] >= 1, "TMS承运商绩效未生成")
    status, data = admin.post_json("/api/integrations/events", {"system_name": "ERP", "event_type": "ERP运费回传", "shipment_id": urllib.parse.unquote(tms_id), "actual_fee": 270, "reason": "SOP ERP运费回传"})
    expect(status == 200, f"ERP运费接口回传失败：{status} {data}")
    freight_bill = next((bill for bill in data["tms"].get("freight_bills", []) if bill["shipment_id"] == urllib.parse.unquote(tms_id)), None)
    integration = next((row for row in data["tms"].get("integrations", []) if row.get("event_type") == "ERP运费回传" and row.get("object_id") == urllib.parse.unquote(tms_id)), None)
    expect(freight_bill and float(freight_bill["actual_fee"]) == 270 and integration and integration["status"] == "成功", "ERP运费接口日志或账单未正确写入")
    status, data = admin.post_json("/api/audit/packages", {"package_type": "运输审计", "shipment_id": urllib.parse.unquote(tms_id)})
    expect(status == 200, f"运输审计包生成失败：{status} {data}")
    audit_package = next((row for row in data["tms"].get("audit_packages", []) if row.get("ref_id") == urllib.parse.unquote(tms_id)), None)
    expect(audit_package and audit_package["status"] == "已生成", "运输审计证据包未返回")
    results.append("TMS运输执行/温控/POD/运费 OK")
    results.append("TMS独立运费账单和承运商绩效 OK")
    results.append("TMS外部接口日志和审计证据包 OK")

    wave_order_ids: list[str] = []
    for suffix, qty in (("A", 10), ("B", 15)):
        status, data = admin.post_json("/api/finished/ship", {
            "goods_id": "FG-DOG-ADULT-10KG",
            "qty": qty,
            "customer": f"SOP波次客户{suffix}",
            "order_no": f"SO-SOP-WAVE-{suffix}",
            "ship_dock": "DOCK-FG-02",
            "remark": "SOP成品多订单合并拣货验证",
        })
        expect(status == 200, f"成品波次发货通知 {suffix} 创建失败：{status} {data}")
        order_id = id_from_notice(data)
        order = item_by_id(data["finished"]["outbounds"], "id", order_id)
        expect(order and order["status"] == "已分配" and order["shortage_qty"] == 0, f"成品波次订单 {suffix} 未完成分配")
        wave_order_ids.append(order_id)

    status, data = admin.post_json("/api/smart/waves/generate", {
        "dock": "DOCK-FG-02",
        "route": "SOP华东合并线",
        "ship_date": "2026-06-02",
        "remark": "智能中心将两张客户订单合并为一个拣货波次",
    })
    expect(status == 200, f"智能成品波次创建失败：{status} {data}")
    wave_id = id_from_notice(data)
    wave = item_by_id(data["finished"]["waves"], "id", wave_id)
    expect(wave and len(wave["orders"]) == 2 and wave["lines"], "成品波次未返回订单或合并拣货明细")
    expect({order["outbound_id"] for order in wave["orders"]} == set(wave_order_ids), "智能波次未选择同月台待发货订单")
    expect(sum(float(line["total_qty"]) for line in wave["lines"]) == 25, "成品波次合并拣货数量不正确")

    for line in wave["lines"]:
        status, data = admin.post_json(f"/api/finished/waves/{wave_id}/pick", {
            "sscc": line["sscc"],
            "picker": "SOP拣货员",
        })
        expect(status == 200, f"成品波次拣货失败：{status} {data}")
    wave = item_by_id(data["finished"]["waves"], "id", wave_id)
    expect(wave and wave["status"] == "已拣货", "成品波次拣货完成后状态不正确")
    expect(all(order["status"] == "已拣货" for order in wave["orders"]), "成品波次订单未同步为已拣货")

    for index, order_id in enumerate(wave_order_ids, start=1):
        status, data = admin.post_json(f"/api/finished/waves/{wave_id}/review", {
            "outbound_id": order_id,
            "staging_location": f"STAGE-SOP-{index}",
            "reviewer": "SOP复核员",
            "remark": "按订单复核合并拣货结果",
        })
        expect(status == 200, f"成品订单复核失败：{status} {data}")
    wave = item_by_id(data["finished"]["waves"], "id", wave_id)
    expect(wave and all(order["status"] == "已复核" for order in wave["orders"]), "成品波次订单复核状态不正确")

    for index, order_id in enumerate(wave_order_ids, start=1):
        status, data = admin.post_json(f"/api/finished/waves/{wave_id}/ship", {
            "outbound_id": order_id,
            "dock": "DOCK-FG-02",
            "truck_no": "苏E-SOP01",
            "driver": "SOP司机",
            "seal_no": f"SOPSEAL{index:02d}",
        })
        expect(status == 200, f"成品订单装车发货失败：{status} {data}")
    wave = item_by_id(data["finished"]["waves"], "id", wave_id)
    expect(wave and wave["status"] == "已完成", "成品波次全部发货后未完成")
    expect(all(order["status"] == "已发货" for order in wave["orders"]), "成品波次订单未全部发货")
    results.append("智能生成成品波次/多订单合并拣货 OK")

    tms_shipment = item_by_id(data["tms"]["shipments"], "id", urllib.parse.unquote(tms_id))
    shipped_line = next((line for line in tms_shipment.get("lines", []) if line.get("lot_no")), None)
    expect(shipped_line, "TMS运单明细未携带批次")
    status, data = admin.post_json("/api/recalls", {"goods_id": shipped_line["goods_id"], "supplier_batch": shipped_line["lot_no"], "reason": "SOP批次召回定位"})
    expect(status == 200 and data["tms"]["recalls"], "批次召回未生成")
    recall = data["tms"]["recalls"][0]
    expect(recall["affected_shipments"] >= 1, "批次召回未定位到已发运单")
    expect(recall.get("affected_shipment_ids"), "批次召回未记录命中运单号")
    frozen_stock = next((row for row in data["inventory"] if row["goods_id"] == shipped_line["goods_id"] and row["supplier_batch"] == shipped_line["lot_no"] and row["quality_status"] == "冻结"), None)
    expect(frozen_stock, "批次召回未冻结在库命中批次")
    results.append("批次召回定位到TMS运单 OK")

    near_expiry = (date.today() + timedelta(days=30)).isoformat()
    status, data = admin.post_json("/api/finished/receive", {
        "goods_id": "FG-DOG-ADULT-10KG",
        "qty": 5,
        "location_id": "FG-A01-01",
        "production_line": "SOP效期测试",
        "supplier_batch": "FG-EXPIRY-SOP",
        "production_date": date.today().isoformat(),
        "expiry_date": near_expiry,
        "po_no": "MO-EXPIRY-SOP",
        "quality_status": "合格",
        "sscc": "SOPEXPORTEXPIRY001",
        "remark": "SOP渠道最小剩余效期验证",
    })
    expect(status == 200, f"渠道效期测试成品入库失败：{status} {data}")
    status, data = admin.post_json("/api/finished/ship", {
        "goods_id": "FG-DOG-ADULT-10KG",
        "qty": 1,
        "customer": "SOP出口客户",
        "channel_code": "EXPORT",
        "order_no": "SO-SOP-EXPIRY",
        "ship_dock": "DOCK-FG-03",
    })
    expiry_out_id = id_from_notice(data)
    expiry_out = item_by_id(data["finished"]["outbounds"], "id", expiry_out_id)
    expect(status == 200 and expiry_out and expiry_out["status"] == "效期不足" and expiry_out["allocated_qty"] == 0, "渠道最小剩余效期未拦截近效期成品")
    status, deny = admin.post_json(f"/api/outbounds/{expiry_out_id}/confirm", {})
    expect(status == 400 and "效期不足" in deny.get("error", ""), "效期不足发货单不应允许确认")
    results.append("渠道最小剩余效期拦截 OK")

    safety_rec = next((item for item in data["smart"]["safety_recommendations"] if item["action"] != "保持"), None)
    expect(safety_rec, "应生成可应用的动态安全库存调整建议")
    status, data = admin.post_json("/api/smart/safety/apply", {
        "goods_id": safety_rec["goods_id"],
        "safety_qty": safety_rec["suggested_safety_qty"],
        "reason": "SOP智能安全库存应用验证",
    })
    product = item_by_id(data["products"], "id", safety_rec["goods_id"])
    expect(status == 200 and product and float(product["safety_qty"]) == float(safety_rec["suggested_safety_qty"]), "动态安全库存建议未写回主数据")
    results.append("动态安全库存一键应用 OK")

    status, data = admin.post_json("/api/masters/products", {
        "id": "PKG-SOP-HOLD",
        "name": "SOP暂扣包材",
        "category": "包材",
        "unit": "pcs",
        "min_qty": 2,
        "safety_qty": 5,
        "expiry_alert_days": 30,
    })
    expect(status == 200 and item_by_id(data["products"], "id", "PKG-SOP-HOLD"), "包材主数据保存失败")
    status, data = admin.post_json("/api/packaging/receive", {
        "goods_id": "PKG-SOP-HOLD",
        "qty": 5,
        "location_id": "PK-HOLD-01",
        "supplier": "SOP包材供应商",
        "supplier_batch": "PKG-SOP-HOLD",
        "po_no": "PO-SOP-PKG-HOLD",
        "quality_status": "暂扣",
        "sscc": "SOPPKGHOLD001",
        "remark": "SOP暂扣验证",
    })
    held_stock = item_by_id(data["inventory"], "sscc", "SOPPKGHOLD001")
    expect(status == 200 and held_stock and held_stock["quality_status"] == "暂扣", "包材暂扣入库失败")
    expect(data["stats"]["packaging_hold_count"] >= 1, "包材暂扣统计未更新")
    status, data = admin.post_json("/api/packaging/issue", {"goods_id": "PKG-SOP-HOLD", "qty": 1, "destination": "包装一线领用", "bin_no": "PK-LINE-SOP"})
    pkg_shortage_id = id_from_notice(data)
    pkg_shortage = item_by_id(data["packaging"]["outbounds"], "id", pkg_shortage_id)
    expect(status == 200 and pkg_shortage and pkg_shortage["status"] == "欠品" and pkg_shortage["allocated_qty"] == 0, "暂扣包材不应参与领用分配")
    status, deny = admin.post_json(f"/api/outbounds/{pkg_shortage_id}/confirm", {})
    expect(status == 400 and "欠品" in deny.get("error", ""), "暂扣导致的欠品单不应允许确认")
    status, data = admin.post_json("/api/status", {"sscc": "SOPPKGHOLD001", "quality_status": "合格", "reason": "SOP暂扣放行"})
    released_stock = item_by_id(data["inventory"], "sscc", "SOPPKGHOLD001")
    expect(status == 200 and released_stock and released_stock["quality_status"] == "合格", "包材暂扣放行失败")
    status, data = admin.post_json("/api/packaging/issue", {"goods_id": "PKG-SOP-HOLD", "qty": 2, "destination": "包装一线领用", "bin_no": "PK-LINE-SOP"})
    pkg_issue_id = id_from_notice(data)
    pkg_issue = item_by_id(data["packaging"]["outbounds"], "id", pkg_issue_id)
    expect(status == 200 and pkg_issue and pkg_issue["status"] == "已分配" and pkg_issue["allocated_qty"] == 2, "包材放行后领用分配失败")
    status, data = admin.post_json(f"/api/outbounds/{pkg_issue_id}/confirm", {})
    expect(status == 200, f"包材领用确认失败：{status} {data}")
    released_stock = item_by_id(data["inventory"], "sscc", "SOPPKGHOLD001")
    expect(released_stock and released_stock["qty"] == 3, "包材领用确认后库存扣减失败")
    status, _, body = admin.get_bytes("/api/export?dataset=packaging_inventory")
    expect(status == 200 and body.startswith(b"PK"), "包材库存导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=template_packaging_receipts")
    expect(status == 200 and body.startswith(b"PK"), "包材入库模板导出失败")
    results.append("包材WMS和暂扣控制 OK")

    status, data = admin.post_json("/api/cycle-counts", {"count_type": "月度盘点", "scope": "包材", "reason": "SOP月度盘点清单"})
    expect(status == 200 and any(row["count_type"] == "月度盘点" and row["scope"] == "包材" for row in data["counts"]), "月度盘点清单生成失败")
    status, data = admin.post_json("/api/cycle-counts", {"count_type": "年度盘点", "scope": "全仓", "reason": "SOP年度盘点清单"})
    expect(status == 200 and any(row["count_type"] == "年度盘点" and row["scope"] == "全仓" for row in data["counts"]), "年度盘点清单生成失败")
    results.append("月度/年度盘点清单 OK")

    status, headers, body = admin.get_bytes("/api/export?dataset=inventory")
    expect(status == 200 and body.startswith(b"PK"), "库存明细 Excel 导出失败")
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        expect("xl/worksheets/sheet1.xml" in archive.namelist(), "导出 Excel 缺少 sheet1.xml")
    status, _, body = admin.get_bytes("/api/export?dataset=template_inbounds")
    expect(status == 200 and body.startswith(b"PK"), "入库模板导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_shipments")
    expect(status == 200 and body.startswith(b"PK"), "TMS运输单导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_events")
    expect(status == 200 and body.startswith(b"PK"), "TMS事件导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_pods")
    expect(status == 200 and body.startswith(b"PK"), "TMS POD导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_freight_bills")
    expect(status == 200 and body.startswith(b"PK"), "TMS运费账单导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_performance")
    expect(status == 200 and body.startswith(b"PK"), "TMS承运商绩效导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_iot_telemetry")
    expect(status == 200 and body.startswith(b"PK"), "TMS IoT/GPS遥测导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=tms_driver_tasks")
    expect(status == 200 and body.startswith(b"PK"), "TMS司机任务导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=integration_events")
    expect(status == 200 and body.startswith(b"PK"), "外部系统接口日志导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=audit_packages")
    expect(status == 200 and body.startswith(b"PK"), "审计证据包导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=channel_expiry_rules")
    expect(status == 200 and body.startswith(b"PK"), "渠道效期规则导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=recalls")
    expect(status == 200 and body.startswith(b"PK"), "召回记录导出失败")
    results.append("Excel 导出和模板 OK")

    product_csv = "GoodsID,名称,类别,单位,最低库存,安全库存,临期提醒天数,MES,保质期天数\nSOP-RM-001,SOP测试原料,原料,kg,2,10,10,是,365\n".encode("utf-8")
    status, data = admin.post_multipart("/api/import", {"import_type": "products"}, "file", "products.csv", product_csv, "text/csv")
    product = item_by_id(data["products"], "id", "SOP-RM-001")
    expect(status == 200 and product and product["min_qty"] == 2 and product["safety_qty"] == 10 and product["expiry_alert_days"] == 10, "货品主数据 Excel/CSV 导入失败")
    near_expiry = (date.today() + timedelta(days=3)).isoformat()
    inbound_csv = f"GoodsID,数量,库位,供应商/来源,批次,生产日期,BBD,PO/单号,货主,品质,备注\nSOP-RM-001,3,RM-A01-01,SOP导入,SOP-IMP,{date.today().isoformat()},{near_expiry},PO-SOP-IMP,MARS-RMR,合格,SOP导入验证\n".encode("utf-8")
    status, data = admin.post_multipart("/api/import", {"import_type": "inbounds"}, "file", "inbounds.csv", inbound_csv, "text/csv")
    expect(status == 200 and data["notice"].endswith("1 行"), "入库 Excel/CSV 导入失败")
    stock_warning = item_by_id(data["stock_warnings"], "id", "SOP-RM-001")
    expect(stock_warning and stock_warning["stock_status"] == "yellow" and stock_warning["reorder_qty"] == 7, "安全库存预警未按设置触发")
    expiry_warning = next((row for row in data["expiry_warnings"] if row["goods_id"] == "SOP-RM-001" and row["supplier_batch"] == "SOP-IMP"), None)
    expect(expiry_warning and expiry_warning["days_left"] == 3 and expiry_warning["expiry_status"] == "warn", "临期提醒未按设置触发")
    results.append("Excel/CSV 批量导入 OK")

    status, _, body = admin.get_bytes("/api/export?dataset=stock_warnings")
    expect(status == 200 and body.startswith(b"PK"), "安全库存预警 Excel 导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=expiry_warnings")
    expect(status == 200 and body.startswith(b"PK"), "临期提醒 Excel 导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=template_products")
    expect(status == 200 and body.startswith(b"PK"), "货品安全库存设置模板导出失败")
    results.append("安全库存设置和临期提醒 OK")

    viewer = WMSClient()
    login(viewer, "view", "view123")
    status, data = viewer.post_json("/api/inbounds", inbound_payload)
    expect(status == 403, "只读账号不应允许入库")
    status, _, body = viewer.get_bytes("/api/export?dataset=inventory")
    expect(status == 200 and body.startswith(b"PK"), "只读账号应允许导出查询数据")
    status, data = viewer.post_multipart("/api/import", {"import_type": "inbounds"}, "file", "inbounds.csv", inbound_csv, "text/csv")
    expect(status == 403, "只读账号不应允许导入")
    status, _, body = viewer.get_bytes("/api/export?dataset=operation_logs")
    expect(status == 403, "只读账号不应允许导出系统操作日志")
    results.append("账户权限和软件使用权限 OK")

    pkg = WMSClient()
    login(pkg, "pkg", "pkg123")
    status, data = pkg.post_json("/api/packaging/receive", {"goods_id": "PKG-LABEL-TRACE", "qty": 1, "location_id": "PK-HOLD-01", "quality_status": "暂扣", "sscc": "SOPPKGROLE001", "remark": "包材账号权限验证"})
    expect(status == 200, "包材账号应允许包材入库和暂扣")
    status, data = pkg.post_json("/api/inbounds", inbound_payload)
    expect(status == 403, "包材账号不应允许原料入库")
    results.append("包材账号权限 OK")

    status, data = admin.post_json("/api/spares/parts", {
        "id": "SP-SOP-TEST-0001",
        "name": "SOP测试备件",
        "spec": "M12",
        "brand": "国产",
        "category": "机械类",
        "abc_class": "B",
        "unit": "个",
        "current_qty": 2,
        "min_qty": 1,
        "safety_qty": 2,
        "max_qty": 10,
        "lead_days": 7,
        "unit_price": 100,
        "supplier": "SOP供应商",
        "location": "SP-SOP-01",
        "equipment_name": "SOP测试设备",
        "equipment_code": "SOP01",
    })
    expect(status == 200 and item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001"), "备件主数据保存失败")
    status, data = admin.post_json("/api/spares/receive", {"part_id": "SP-SOP-TEST-0001", "qty": 5, "ref_no": "PO-SOP-SP", "approver": "设备工程师", "keeper": "备件库管"})
    part = item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001")
    expect(status == 200 and part and part["current_qty"] == 7, "备件入库失败")
    status, deny = admin.post_json("/api/spares/issue", {"part_id": "SP-SOP-TEST-0001", "qty": 1, "equipment_name": "SOP测试设备", "requester": "维修人员"})
    expect(status == 400 and "work_order" in deny.get("error", ""), "备件领用必须绑定工单")
    status, data = admin.post_json("/api/spares/issue", {
        "part_id": "SP-SOP-TEST-0001",
        "qty": 2,
        "work_order": "WO-SOP-SP-001",
        "equipment_name": "SOP测试设备",
        "equipment_code": "SOP01",
        "reason": "故障维修",
        "requester": "维修人员",
        "keeper": "备件库管",
        "old_part_status": "退库",
    })
    part = item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001")
    expect(status == 200 and part and part["current_qty"] == 5, "备件工单领用失败")
    status, deny = admin.post_json("/api/spares/issue", {
        "part_id": "SP-FS-VC01-0002",
        "qty": 1,
        "work_order": "WO-SOP-FS-001",
        "equipment_name": "真空喷涂机",
        "requester": "维修人员",
        "approver": "维修主管",
    })
    expect(status == 400 and "清场确认" in deny.get("error", ""), "食品接触备件领用必须清场确认")
    status, data = admin.post_json("/api/spares/issue", {
        "part_id": "SP-FS-VC01-0002",
        "qty": 1,
        "work_order": "WO-SOP-FS-002",
        "equipment_name": "真空喷涂机",
        "equipment_code": "VC01",
        "reason": "计划保养",
        "requester": "维修人员",
        "approver": "维修主管",
        "keeper": "备件库管",
        "old_part_status": "报废",
        "food_clearance": True,
    })
    expect(status == 200, f"食品接触备件清场后领用失败：{status} {data}")
    status, data = admin.post_json("/api/spares/return", {"part_id": "SP-SOP-TEST-0001", "qty": 1, "work_order": "WO-SOP-SP-001", "keeper": "备件库管", "old_part_status": "可维修件"})
    part = item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001")
    expect(status == 200 and part and part["current_qty"] == 6, "备件退库失败")
    status, data = admin.post_json("/api/spares/count", {"part_id": "SP-SOP-TEST-0001", "actual_qty": 4, "reason": "SOP备件盘点"})
    part = item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001")
    expect(status == 200 and part and part["current_qty"] == 4, "备件盘点失败")
    status, data = admin.post_json("/api/spares/scrap", {"part_id": "SP-SOP-TEST-0001", "qty": 1, "reason": "损坏无法修复", "approver": "设备经理", "requester": "维修人员"})
    part = item_by_id(data["spares"]["parts"], "id", "SP-SOP-TEST-0001")
    expect(status == 200 and part and part["current_qty"] == 3, "备件报废失败")
    status, _, body = admin.get_bytes("/api/export?dataset=spare_parts")
    expect(status == 200 and body.startswith(b"PK"), "备件台账导出失败")
    status, _, body = admin.get_bytes("/api/export?dataset=template_spare_issues")
    expect(status == 200 and body.startswith(b"PK"), "备件领用模板导出失败")
    spare_csv = "备件编码,备件名称,规格型号,类别,ABC等级,单位,当前库存,最低库存,安全库存,最高库存,单价,货位,适用设备,设备编号\nSP-SOP-IMP-0001,SOP导入备件,DN25,气动类,B,个,2,1,2,8,88,SP-SOP-02,SOP导入设备,SOP02\n".encode("utf-8")
    status, data = admin.post_multipart("/api/import", {"import_type": "spare_parts"}, "file", "spare_parts.csv", spare_csv, "text/csv")
    expect(status == 200 and item_by_id(data["spares"]["parts"], "id", "SP-SOP-IMP-0001"), "备件主数据导入失败")
    equip = WMSClient()
    login(equip, "equip", "equip123")
    status, data = equip.post_json("/api/spares/receive", {"part_id": "SP-SOP-IMP-0001", "qty": 1, "keeper": "设备部备件"})
    expect(status == 200, "设备部账号应允许备件入库")
    status, data = equip.post_json("/api/inbounds", inbound_payload)
    expect(status == 403, "设备部账号不应允许原料入库")
    results.append("设备部备品备件管理 OK")

    status, data = admin.get_json("/api/bootstrap")
    log_paths = {row.get("path") for row in data.get("operation_logs", [])}
    expect(status == 200 and data.get("operation_logs") and "/api/counts" in log_paths and "/api/cycle-counts" in log_paths, "系统操作日志未记录关键业务接口")
    status, _, body = admin.get_bytes("/api/export?dataset=operation_logs")
    expect(status == 200 and body.startswith(b"PK"), "系统操作日志 Excel 导出失败")
    results.append("系统操作日志记录 OK")

    reset_demo(admin)
    results.append("验收后账套重置 OK")

    print("SOP_FLOW_TEST_PASS")
    for result in results:
        print(f"- {result}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line verifier should print actionable failure.
        print("SOP_FLOW_TEST_FAIL")
        print(exc)
        raise
