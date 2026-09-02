#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import hmac
import cgi
import csv
import io
import mimetypes
import os
import re
import secrets
import sqlite3
import zipfile
from datetime import date, datetime, timedelta
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "wms.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    min_qty REAL NOT NULL DEFAULT 0,
    safety_qty REAL NOT NULL DEFAULT 0,
    expiry_alert_days INTEGER NOT NULL DEFAULT 60,
    courbon INTEGER NOT NULL DEFAULT 0,
    shelf_days INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    area TEXT NOT NULL,
    zone TEXT NOT NULL,
    type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 5,
    capacity REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS stock_units (
    sscc TEXT PRIMARY KEY,
    goods_id TEXT NOT NULL,
    owner TEXT NOT NULL,
    location_id TEXT NOT NULL,
    qty REAL NOT NULL,
    reserved_qty REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,
    production_date TEXT,
    expiry_date TEXT,
    supplier_batch TEXT,
    po_no TEXT,
    quality_status TEXT NOT NULL DEFAULT '合格',
    updated_at TEXT NOT NULL,
    FOREIGN KEY(goods_id) REFERENCES products(id),
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS inbound_orders (
    id TEXT PRIMARY KEY,
    goods_id TEXT NOT NULL,
    qty REAL NOT NULL,
    received_qty REAL NOT NULL,
    status TEXT NOT NULL,
    supplier TEXT,
    supplier_batch TEXT,
    production_date TEXT,
    expiry_date TEXT,
    location_id TEXT NOT NULL,
    sscc TEXT NOT NULL,
    created_at TEXT NOT NULL,
    remark TEXT,
    FOREIGN KEY(goods_id) REFERENCES products(id),
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS outbound_orders (
    id TEXT PRIMARY KEY,
    goods_id TEXT NOT NULL,
    qty REAL NOT NULL,
    allocated_qty REAL NOT NULL,
    shortage_qty REAL NOT NULL,
    status TEXT NOT NULL,
    destination TEXT NOT NULL,
    channel_code TEXT,
    min_remaining_days INTEGER NOT NULL DEFAULT 0,
    bin_no TEXT,
    courbon_connected INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    confirmed_at TEXT,
    remark TEXT,
    FOREIGN KEY(goods_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS outbound_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outbound_id TEXT NOT NULL,
    sscc TEXT NOT NULL,
    location_id TEXT NOT NULL,
    qty REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY(outbound_id) REFERENCES outbound_orders(id),
    FOREIGN KEY(sscc) REFERENCES stock_units(sscc),
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS finished_waves (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    ship_date TEXT,
    dock TEXT,
    route TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT,
    picked_at TEXT,
    completed_at TEXT,
    remark TEXT
);

CREATE TABLE IF NOT EXISTS finished_wave_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wave_id TEXT NOT NULL,
    outbound_id TEXT NOT NULL,
    status TEXT NOT NULL,
    staging_location TEXT,
    picker TEXT,
    picked_at TEXT,
    reviewer TEXT,
    reviewed_at TEXT,
    truck_no TEXT,
    driver TEXT,
    seal_no TEXT,
    loaded_at TEXT,
    shipped_at TEXT,
    remark TEXT,
    UNIQUE(wave_id, outbound_id),
    FOREIGN KEY(wave_id) REFERENCES finished_waves(id),
    FOREIGN KEY(outbound_id) REFERENCES outbound_orders(id)
);

CREATE TABLE IF NOT EXISTS finished_wave_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wave_id TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    sscc TEXT NOT NULL,
    location_id TEXT NOT NULL,
    total_qty REAL NOT NULL,
    picked_qty REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    picker TEXT,
    picked_at TEXT,
    UNIQUE(wave_id, goods_id, sscc, location_id),
    FOREIGN KEY(wave_id) REFERENCES finished_waves(id),
    FOREIGN KEY(goods_id) REFERENCES products(id),
    FOREIGN KEY(sscc) REFERENCES stock_units(sscc),
    FOREIGN KEY(location_id) REFERENCES locations(id)
);

CREATE TABLE IF NOT EXISTS moves (
    id TEXT PRIMARY KEY,
    sscc TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    from_location TEXT NOT NULL,
    to_location TEXT NOT NULL,
    qty REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    operator TEXT,
    remark TEXT
);

CREATE TABLE IF NOT EXISTS counts (
    id TEXT PRIMARY KEY,
    sscc TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    location_id TEXT NOT NULL,
    system_qty REAL NOT NULL,
    actual_qty REAL NOT NULL,
    diff_qty REAL NOT NULL,
    status TEXT NOT NULL,
    count_type TEXT NOT NULL DEFAULT '日常盘点',
    scope TEXT,
    operator TEXT,
    adjusted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    action TEXT NOT NULL,
    ref_id TEXT,
    sscc TEXT,
    goods_id TEXT,
    location_id TEXT,
    qty REAL,
    before_qty REAL,
    after_qty REAL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    username TEXT,
    display_name TEXT,
    role TEXT,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    action TEXT,
    message TEXT,
    payload TEXT,
    ip TEXT
);

CREATE TABLE IF NOT EXISTS scan_events (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    scan_type TEXT NOT NULL,
    code TEXT NOT NULL,
    parsed_type TEXT NOT NULL,
    ref_id TEXT,
    location_id TEXT,
    goods_id TEXT,
    action TEXT,
    result TEXT,
    operator TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS camera_scans (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    location_id TEXT,
    camera_name TEXT,
    model_status TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0,
    image_note TEXT,
    operator TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS label_prints (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    label_type TEXT NOT NULL,
    template_name TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    goods_name TEXT NOT NULL,
    category TEXT NOT NULL,
    batch_no TEXT NOT NULL,
    supplier_batch TEXT,
    production_date TEXT,
    expiry_date TEXT,
    qty REAL,
    unit TEXT,
    location_id TEXT,
    sscc TEXT,
    quality_status TEXT,
    code_type TEXT NOT NULL,
    barcode_value TEXT NOT NULL,
    qr_value TEXT NOT NULL,
    copies INTEGER NOT NULL DEFAULT 1,
    operator TEXT,
    payload TEXT
);

CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY(username) REFERENCES users(username)
);

CREATE TABLE IF NOT EXISTS spare_parts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    spec TEXT,
    brand TEXT,
    category TEXT NOT NULL,
    abc_class TEXT NOT NULL DEFAULT 'B',
    unit TEXT NOT NULL DEFAULT '个',
    current_qty REAL NOT NULL DEFAULT 0,
    min_qty REAL NOT NULL DEFAULT 0,
    safety_qty REAL NOT NULL DEFAULT 0,
    max_qty REAL NOT NULL DEFAULT 0,
    lead_days INTEGER NOT NULL DEFAULT 0,
    unit_price REAL NOT NULL DEFAULT 0,
    supplier TEXT,
    location TEXT,
    equipment_name TEXT,
    equipment_code TEXT,
    food_contact INTEGER NOT NULL DEFAULT 0,
    imported INTEGER NOT NULL DEFAULT 0,
    critical INTEGER NOT NULL DEFAULT 0,
    expiry_date TEXT,
    remark TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS spare_transactions (
    id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    action TEXT NOT NULL,
    part_id TEXT NOT NULL,
    qty REAL NOT NULL,
    before_qty REAL NOT NULL,
    after_qty REAL NOT NULL,
    unit_price REAL NOT NULL DEFAULT 0,
    amount REAL NOT NULL DEFAULT 0,
    location TEXT,
    ref_no TEXT,
    work_order TEXT,
    equipment_name TEXT,
    equipment_code TEXT,
    reason TEXT,
    requester TEXT,
    approver TEXT,
    keeper TEXT,
    old_part_status TEXT,
    food_clearance INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    FOREIGN KEY(part_id) REFERENCES spare_parts(id)
);

CREATE TABLE IF NOT EXISTS tms_carriers (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    contact TEXT,
    phone TEXT,
    service_type TEXT NOT NULL DEFAULT '零担',
    cold_chain INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    score REAL NOT NULL DEFAULT 100,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tms_lanes (
    code TEXT PRIMARY KEY,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    carrier_code TEXT NOT NULL,
    transit_days INTEGER NOT NULL DEFAULT 1,
    temp_min REAL,
    temp_max REAL,
    base_fee REAL NOT NULL DEFAULT 0,
    fee_per_unit REAL NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(carrier_code) REFERENCES tms_carriers(code)
);

CREATE TABLE IF NOT EXISTS tms_shipments (
    id TEXT PRIMARY KEY,
    source_outbound_id TEXT UNIQUE,
    wave_id TEXT,
    carrier_code TEXT NOT NULL,
    lane_code TEXT NOT NULL,
    customer TEXT,
    destination TEXT NOT NULL,
    vehicle_no TEXT,
    driver TEXT,
    driver_phone TEXT,
    seal_no TEXT,
    planned_departure TEXT,
    actual_departure TEXT,
    eta TEXT,
    actual_arrival TEXT,
    temp_min REAL,
    temp_max REAL,
    status TEXT NOT NULL DEFAULT '待发车',
    exception_flag INTEGER NOT NULL DEFAULT 0,
    exception_note TEXT,
    estimated_fee REAL NOT NULL DEFAULT 0,
    actual_fee REAL NOT NULL DEFAULT 0,
    billing_status TEXT NOT NULL DEFAULT '待对账',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT,
    FOREIGN KEY(source_outbound_id) REFERENCES outbound_orders(id),
    FOREIGN KEY(carrier_code) REFERENCES tms_carriers(code),
    FOREIGN KEY(lane_code) REFERENCES tms_lanes(code)
);

CREATE TABLE IF NOT EXISTS tms_shipment_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id TEXT NOT NULL,
    outbound_id TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    sscc TEXT NOT NULL,
    lot_no TEXT,
    expiry_date TEXT,
    location_id TEXT,
    qty REAL NOT NULL,
    unit TEXT,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS tms_events (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    event_time TEXT NOT NULL,
    event_type TEXT NOT NULL,
    location_text TEXT,
    temperature REAL,
    humidity REAL,
    door_open INTEGER NOT NULL DEFAULT 0,
    risk_level TEXT NOT NULL DEFAULT '低',
    note TEXT,
    operator TEXT,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS tms_pods (
    id TEXT PRIMARY KEY,
    shipment_id TEXT UNIQUE NOT NULL,
    signed_by TEXT NOT NULL,
    signed_at TEXT NOT NULL,
    received_qty REAL NOT NULL DEFAULT 0,
    damaged_qty REAL NOT NULL DEFAULT 0,
    shortage_qty REAL NOT NULL DEFAULT 0,
    note TEXT,
    operator TEXT,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS tms_freight_bills (
    id TEXT PRIMARY KEY,
    shipment_id TEXT UNIQUE NOT NULL,
    carrier_code TEXT,
    estimated_fee REAL NOT NULL DEFAULT 0,
    actual_fee REAL NOT NULL DEFAULT 0,
    difference REAL NOT NULL DEFAULT 0,
    billing_status TEXT NOT NULL DEFAULT '待对账',
    exception_reason TEXT,
    confirmed_by TEXT,
    confirmed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS tms_iot_telemetry (
    id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    telemetry_time TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    location_text TEXT,
    temperature REAL,
    humidity REAL,
    door_open INTEGER NOT NULL DEFAULT 0,
    reefer_status TEXT,
    speed REAL,
    risk_level TEXT NOT NULL DEFAULT '低',
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS tms_driver_tasks (
    id TEXT PRIMARY KEY,
    shipment_id TEXT UNIQUE NOT NULL,
    driver TEXT,
    driver_phone TEXT,
    vehicle_no TEXT,
    task_status TEXT NOT NULL DEFAULT '待接单',
    pickup_location TEXT,
    delivery_location TEXT,
    pin_code TEXT,
    assigned_at TEXT NOT NULL,
    accepted_at TEXT,
    departed_at TEXT,
    arrived_at TEXT,
    signed_at TEXT,
    pod_note TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(shipment_id) REFERENCES tms_shipments(id)
);

CREATE TABLE IF NOT EXISTS integration_events (
    id TEXT PRIMARY KEY,
    system_name TEXT NOT NULL,
    direction TEXT NOT NULL,
    event_type TEXT NOT NULL,
    object_type TEXT,
    object_id TEXT,
    status TEXT NOT NULL DEFAULT '待处理',
    message TEXT,
    payload TEXT,
    created_at TEXT NOT NULL,
    processed_at TEXT,
    operator TEXT
);

CREATE TABLE IF NOT EXISTS audit_packages (
    id TEXT PRIMARY KEY,
    package_type TEXT NOT NULL,
    ref_id TEXT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT '已生成',
    summary TEXT,
    payload TEXT,
    created_at TEXT NOT NULL,
    operator TEXT
);

CREATE TABLE IF NOT EXISTS channel_expiry_rules (
    id TEXT PRIMARY KEY,
    channel_code TEXT NOT NULL,
    channel_name TEXT NOT NULL,
    goods_id TEXT NOT NULL,
    min_remaining_days INTEGER NOT NULL DEFAULT 0,
    allow_near_expiry INTEGER NOT NULL DEFAULT 0,
    require_quality_release INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL,
    UNIQUE(channel_code, goods_id),
    FOREIGN KEY(goods_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS recall_orders (
    id TEXT PRIMARY KEY,
    goods_id TEXT NOT NULL,
    supplier_batch TEXT NOT NULL,
    reason TEXT,
    affected_inventory INTEGER NOT NULL DEFAULT 0,
    affected_shipments INTEGER NOT NULL DEFAULT 0,
    affected_sscc TEXT,
    affected_shipment_ids TEXT,
    status TEXT NOT NULL DEFAULT '已冻结',
    created_at TEXT NOT NULL,
    operator TEXT
);
"""


SOURCE_ANALYSIS = [
    {
        "module": "入库",
        "old_clues": "InstockInformList / InStockTbl / InStockConfirmList / SOP 6.2-6.4",
        "kept": "入库通知、收货、SSCC、上架合并为一张可追溯入库单",
    },
    {
        "module": "出库",
        "old_clues": "OutstockInformList / OutStockPickDt / RetriPickConfirm / SOP 6.6",
        "kept": "出库通知后按近效期和优先货位自动分配，确认后扣减库存",
    },
    {
        "module": "库内",
        "old_clues": "MoveEntryList / InventoryQry_c / StockChkDtTbl / StcAdjustList",
        "kept": "库存查询、移库、盘点差异和库存调整全部写入台账",
    },
    {
        "module": "RF",
        "old_clues": "手持上架、手持移库、RF盘点、SSCC Label",
        "kept": "保留 SSCC 扫描入口，适合手持枪或手机浏览器操作",
    },
    {
        "module": "成品",
        "old_clues": "成品盘点 / 出口出库操作 / 分拣单打印 / 退货入库操作",
        "kept": "增加成品完工入库、成品库存、客户发运、退货入库和近效期预警",
    },
]


FINISHED_PRODUCTS = [
    ("FG-DOG-ADULT-10KG", "犬成犬鲜粮 10kg", "成品", "bag", 900, 1200, 90, 0, 365),
    ("FG-CAT-KITTEN-3KG", "幼猫鲜粮 3kg", "成品", "bag", 700, 900, 90, 0, 365),
    ("FG-DOG-SENIOR-8KG", "犬老年鲜粮 8kg", "成品", "bag", 500, 700, 90, 0, 365),
]

FINISHED_LOCATIONS = [
    ("FG-A01-01", "成品仓", "A01 整托存储", "成品正常货位", 20, 18000),
    ("FG-A02-01", "成品仓", "A02 整托存储", "成品正常货位", 21, 18000),
    ("FG-STAGE-01", "成品仓", "发运暂存区", "成品发运暂存", 10, 6000),
    ("FG-RETURN-01", "成品仓", "退货待检区", "成品退货待检", 30, 3000),
]

FINISHED_STOCKS = [
    ("FGSSCC202606020001", "FG-DOG-ADULT-10KG", "MARS-FG", "FG-A01-01", 960, 0, "bag", "2026-05-28", "2027-05-28", "FGDA-0528-A", "MO260528-01", "合格"),
    ("FGSSCC202606020002", "FG-CAT-KITTEN-3KG", "MARS-FG", "FG-A02-01", 720, 0, "bag", "2026-05-30", "2027-05-30", "FGCK-0530-A", "MO260530-01", "合格"),
    ("FGSSCC202606020003", "FG-DOG-SENIOR-8KG", "MARS-FG", "FG-STAGE-01", 360, 0, "bag", "2026-05-22", "2027-05-22", "FGDS-0522-A", "MO260522-01", "合格"),
]

PACKAGING_PRODUCTS = [
    ("PKG-BAG", "包装袋", "包材", "pcs", 8000, 10000, 60, 0, 0),
    ("PKG-CARTON-10KG", "10kg 外箱", "包材", "pcs", 3000, 5000, 60, 0, 0),
    ("PKG-LABEL-TRACE", "追溯标签", "包材", "roll", 20, 40, 30, 0, 0),
]

PACKAGING_LOCATIONS = [
    ("PK-B01-01", "包材仓", "B01 袋膜货架", "包材货位", 5, 30000),
    ("PK-B02-01", "包材仓", "B02 外箱货架", "包材货位", 6, 24000),
    ("PK-HOLD-01", "包材仓", "暂扣/待判区", "包材暂扣", 8, 6000),
    ("PK-STAGE-01", "包材仓", "包装线暂存", "包材发料暂存", 4, 8000),
]

PACKAGING_STOCKS = [
    ("PKGSSCC202606020001", "PKG-BAG", "MARS-PKG", "PK-B01-01", 18000, 0, "pcs", "", "", "BAG-0601", "PO260602", "合格"),
    ("PKGSSCC202606020002", "PKG-CARTON-10KG", "MARS-PKG", "PK-B02-01", 4200, 0, "pcs", "", "", "CTN-0601", "PO260602", "合格"),
    ("PKGSSCC202606020003", "PKG-LABEL-TRACE", "MARS-PKG", "PK-HOLD-01", 8, 0, "roll", "", "", "LBL-0601", "PO260602", "暂扣"),
]

TMS_CARRIERS = [
    ("TMS-SF", "顺丰冷运/快运", "承运商客服", "95338", "冷链/快运", 1, 96),
    ("TMS-JD", "京东物流", "承运商客服", "950616", "仓配/快运", 1, 94),
    ("TMS-LTL", "区域零担承运商", "调度员", "13800000000", "零担", 0, 88),
]

TMS_LANES = [
    ("LANE-SZ-SH-COLD", "苏州工厂", "上海区域", "TMS-SF", 1, 2, 8, 180, 0.45),
    ("LANE-SZ-HZ-AMB", "苏州工厂", "杭州区域", "TMS-JD", 1, None, None, 150, 0.35),
    ("LANE-SZ-NATION-LTL", "苏州工厂", "全国零担", "TMS-LTL", 3, None, None, 260, 0.28),
]

CHANNEL_EXPIRY_RULES = [
    ("ECOM", "电商平台", "FG-DOG-ADULT-10KG", 120, 0, 1),
    ("ECOM", "电商平台", "FG-CAT-KITTEN-3KG", 120, 0, 1),
    ("ECOM", "电商平台", "FG-DOG-SENIOR-8KG", 120, 0, 1),
    ("DISTRIBUTOR", "经销商", "FG-DOG-ADULT-10KG", 90, 0, 1),
    ("DISTRIBUTOR", "经销商", "FG-CAT-KITTEN-3KG", 90, 0, 1),
    ("DISTRIBUTOR", "经销商", "FG-DOG-SENIOR-8KG", 90, 0, 1),
    ("KA", "KA商超", "FG-DOG-ADULT-10KG", 180, 0, 1),
    ("KA", "KA商超", "FG-CAT-KITTEN-3KG", 180, 0, 1),
    ("KA", "KA商超", "FG-DOG-SENIOR-8KG", 180, 0, 1),
    ("EXPORT", "出口", "FG-DOG-ADULT-10KG", 240, 0, 1),
    ("EXPORT", "出口", "FG-CAT-KITTEN-3KG", 240, 0, 1),
    ("EXPORT", "出口", "FG-DOG-SENIOR-8KG", 240, 0, 1),
]

SPARE_PARTS = [
    {
        "id": "SP-ME-EX01-0001", "name": "膨化机主轴轴承", "spec": "SKF 22220E", "brand": "SKF",
        "category": "机械类", "abc_class": "A", "unit": "个", "current_qty": 1, "min_qty": 1, "safety_qty": 2, "max_qty": 3,
        "lead_days": 45, "unit_price": 6800, "supplier": "原厂授权代理", "location": "SP-A-01-01",
        "equipment_name": "1号膨化线", "equipment_code": "EX01", "food_contact": 0, "imported": 1, "critical": 1,
        "expiry_date": "", "remark": "关键停机备件，低于安全库存优先采购",
    },
    {
        "id": "SP-FS-VC01-0002", "name": "食品级喷涂软管", "spec": "DN25 食品级耐油软管", "brand": "Trelleborg",
        "category": "食品接触类", "abc_class": "A", "unit": "米", "current_qty": 6, "min_qty": 4, "safety_qty": 8, "max_qty": 20,
        "lead_days": 20, "unit_price": 180, "supplier": "食品级材料供应商", "location": "SP-FS-01-02",
        "equipment_name": "真空喷涂机", "equipment_code": "VC01", "food_contact": 1, "imported": 0, "critical": 1,
        "expiry_date": "2027-06-30", "remark": "食品接触件，需保留合格证明并独立包装",
    },
    {
        "id": "SP-PK-PK01-0001", "name": "包装机切刀", "spec": "PK01-切刀组件", "brand": "原厂",
        "category": "包装类", "abc_class": "B", "unit": "把", "current_qty": 12, "min_qty": 6, "safety_qty": 10, "max_qty": 30,
        "lead_days": 15, "unit_price": 320, "supplier": "包装机原厂", "location": "SP-PK-02-01",
        "equipment_name": "1号包装机", "equipment_code": "PK01", "food_contact": 1, "imported": 0, "critical": 0,
        "expiry_date": "", "remark": "高频易损件，按月分析消耗",
    },
    {
        "id": "SP-EL-PK01-0025", "name": "伺服驱动器", "spec": "750W EtherCAT", "brand": "Panasonic",
        "category": "电气类", "abc_class": "A", "unit": "台", "current_qty": 0, "min_qty": 1, "safety_qty": 1, "max_qty": 2,
        "lead_days": 35, "unit_price": 5200, "supplier": "授权电气供应商", "location": "SP-EL-01-01",
        "equipment_name": "1号包装机", "equipment_code": "PK01", "food_contact": 0, "imported": 0, "critical": 1,
        "expiry_date": "", "remark": "红色预警：关键电气件缺货",
    },
    {
        "id": "SP-UT-AC01-0008", "name": "空压机油分芯", "spec": "AC01-OF-55KW", "brand": "Atlas",
        "category": "公用工程类", "abc_class": "B", "unit": "个", "current_qty": 3, "min_qty": 2, "safety_qty": 3, "max_qty": 8,
        "lead_days": 10, "unit_price": 950, "supplier": "空压机维保商", "location": "SP-UT-03-01",
        "equipment_name": "空压机", "equipment_code": "AC01", "food_contact": 0, "imported": 0, "critical": 1,
        "expiry_date": "", "remark": "按保养计划领用",
    },
    {
        "id": "SP-TL-MRO-0001", "name": "不锈钢扎带", "spec": "4.6x300mm", "brand": "国产",
        "category": "工具耗材类", "abc_class": "C", "unit": "包", "current_qty": 20, "min_qty": 5, "safety_qty": 10, "max_qty": 40,
        "lead_days": 3, "unit_price": 35, "supplier": "五金供应商", "location": "SP-TL-04-03",
        "equipment_name": "通用维修", "equipment_code": "MRO", "food_contact": 0, "imported": 0, "critical": 0,
        "expiry_date": "", "remark": "普通工具耗材，控制库存金额",
    },
]

ROLE_LABELS = {
    "admin": "系统管理员",
    "supervisor": "仓库主管",
    "raw_warehouse": "原料仓操作",
    "finished_warehouse": "成品仓操作",
    "packaging_warehouse": "包材仓操作",
    "equipment": "设备部备件",
    "logistics": "运输调度",
    "viewer": "只读查看",
}

ROLE_PERMISSIONS = {
    "admin": ["view", "inbound", "outbound", "finished", "packaging", "tms", "tms_admin", "tms_settle", "recall", "move", "count", "adjust", "status", "masters", "spares", "spares_master", "logs", "reset", "users"],
    "supervisor": ["view", "inbound", "outbound", "finished", "packaging", "tms", "tms_admin", "tms_settle", "recall", "move", "count", "adjust", "status", "masters", "spares", "spares_master", "logs", "reset"],
    "raw_warehouse": ["view", "inbound", "outbound", "move", "count", "status"],
    "finished_warehouse": ["view", "finished", "tms", "move", "count", "status"],
    "packaging_warehouse": ["view", "packaging", "move", "count", "status"],
    "equipment": ["view", "spares", "spares_master"],
    "logistics": ["view", "tms", "tms_admin", "tms_settle", "recall"],
    "viewer": ["view"],
}

DEFAULT_USERS = [
    ("admin", "系统管理员", "admin", "admin123"),
    ("supervisor", "仓库主管", "supervisor", "wms123"),
    ("raw", "原料仓操作", "raw_warehouse", "raw123"),
    ("fg", "成品仓操作", "finished_warehouse", "fg123"),
    ("pkg", "包材仓操作", "packaging_warehouse", "pkg123"),
    ("equip", "设备部备件", "equipment", "equip123"),
    ("tms", "运输调度", "logistics", "tms123"),
    ("view", "只读查看", "viewer", "view123"),
]

SESSION_COOKIE = "yuwms_session"
SESSION_DAYS = 1

EXPORT_DATASETS = {
    "inventory": "库存明细",
    "finished_inventory": "成品库存",
    "packaging_inventory": "包材库存",
    "packaging_warnings": "包材库存预警",
    "products": "货品主数据",
    "locations": "库位主数据",
    "inbounds": "入库单",
    "outbounds": "出库单",
    "ledger": "库存流水",
    "operation_logs": "系统操作日志",
    "label_prints": "标签打印记录",
    "stock_warnings": "安全库存预警",
    "expiry_warnings": "临期提醒",
    "spare_parts": "备件基础台账",
    "spare_transactions": "备件出入库流水",
    "spare_warnings": "备件库存预警",
    "tms_shipments": "TMS运输单",
    "tms_events": "TMS在途/温控事件",
    "tms_pods": "TMS签收POD",
    "tms_freight_bills": "TMS运费账单",
    "tms_performance": "TMS承运商绩效",
    "tms_iot_telemetry": "TMS IoT/GPS温控遥测",
    "tms_driver_tasks": "TMS司机任务",
    "integration_events": "外部系统接口日志",
    "audit_packages": "审计证据包",
    "channel_expiry_rules": "渠道效期规则",
    "recalls": "批次召回记录",
}

IMPORT_SCHEMAS = {
    "products": {
        "label": "货品主数据",
        "permission": "masters",
        "columns": [
            ("id", "GoodsID"),
            ("name", "名称"),
            ("category", "类别"),
            ("unit", "单位"),
            ("min_qty", "最低库存"),
            ("safety_qty", "安全库存"),
            ("expiry_alert_days", "临期提醒天数"),
            ("courbon", "MES"),
            ("shelf_days", "保质期天数"),
        ],
        "sample": {"id": "NEW-RM-001", "name": "新原料", "category": "原料", "unit": "kg", "min_qty": "300", "safety_qty": "500", "expiry_alert_days": "60", "courbon": "否", "shelf_days": "365"},
    },
    "locations": {
        "label": "库位主数据",
        "permission": "masters",
        "columns": [
            ("id", "库位编号"),
            ("area", "仓库"),
            ("zone", "库区"),
            ("type", "类型"),
            ("priority", "分配优先级"),
            ("capacity", "容量"),
        ],
        "sample": {"id": "RM-A03-01", "area": "原料仓", "zone": "A03 货架", "type": "正常货位", "priority": "5", "capacity": "12000"},
    },
    "inbounds": {
        "label": "入库批量导入",
        "permission": "inbound",
        "columns": [
            ("goods_id", "GoodsID"),
            ("qty", "数量"),
            ("location_id", "库位"),
            ("supplier", "供应商/来源"),
            ("supplier_batch", "批次"),
            ("production_date", "生产日期"),
            ("expiry_date", "BBD"),
            ("po_no", "PO/单号"),
            ("owner", "货主"),
            ("quality_status", "品质"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "3637", "qty": "100", "location_id": "RM-A01-01", "supplier": "现场收货", "supplier_batch": "BATCH-001", "production_date": "2026-06-02", "expiry_date": "2026-12-31", "po_no": "PO260603", "owner": "MARS-RMR", "quality_status": "合格", "remark": "Excel导入"},
    },
    "outbounds": {
        "label": "出库批量导入",
        "permission": "outbound",
        "columns": [
            ("goods_id", "GoodsID"),
            ("qty", "数量"),
            ("destination", "去向"),
            ("bin_no", "料仓/月台"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "3637", "qty": "100", "destination": "粉碎投料", "bin_no": "BIN-01", "remark": "Excel导入"},
    },
    "finished_receipts": {
        "label": "成品完工入库",
        "permission": "finished",
        "columns": [
            ("goods_id", "成品SKU"),
            ("qty", "数量"),
            ("location_id", "成品库位"),
            ("production_line", "产线/班组"),
            ("supplier_batch", "生产批次"),
            ("production_date", "生产日期"),
            ("expiry_date", "BBD"),
            ("po_no", "生产工单"),
            ("quality_status", "品质"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "FG-DOG-ADULT-10KG", "qty": "120", "location_id": "FG-A01-01", "production_line": "包装一线", "supplier_batch": "FG-BATCH-001", "production_date": "2026-06-02", "expiry_date": "2027-06-02", "po_no": "MO260603-01", "quality_status": "合格", "remark": "Excel导入"},
    },
    "finished_shipments": {
        "label": "成品客户发运",
        "permission": "finished",
        "columns": [
            ("goods_id", "成品SKU"),
            ("qty", "数量"),
            ("customer", "客户/渠道"),
            ("channel_code", "渠道编码"),
            ("order_no", "销售订单"),
            ("ship_dock", "月台/装车口"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "FG-DOG-ADULT-10KG", "qty": "120", "customer": "华东经销商", "channel_code": "DISTRIBUTOR", "order_no": "SO260603-01", "ship_dock": "DOCK-FG-01", "remark": "Excel导入"},
    },
    "packaging_receipts": {
        "label": "包材入库",
        "permission": "packaging",
        "columns": [
            ("goods_id", "包材编码"),
            ("qty", "数量"),
            ("location_id", "包材库位"),
            ("supplier", "供应商/来源"),
            ("supplier_batch", "批次"),
            ("production_date", "生产日期"),
            ("expiry_date", "BBD"),
            ("po_no", "采购单号"),
            ("quality_status", "品质"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "PKG-CARTON-10KG", "qty": "1000", "location_id": "PK-B02-01", "supplier": "包材供应商", "supplier_batch": "PKG-BATCH-001", "production_date": "2026-06-02", "expiry_date": "", "po_no": "PO-PKG-001", "quality_status": "合格", "remark": "外箱尺寸、印刷、条码已核对"},
    },
    "packaging_issues": {
        "label": "包材领用",
        "permission": "packaging",
        "columns": [
            ("goods_id", "包材编码"),
            ("qty", "数量"),
            ("destination", "领用去向"),
            ("bin_no", "包装线/月台"),
            ("remark", "备注"),
        ],
        "sample": {"goods_id": "PKG-BAG", "qty": "2000", "destination": "包装一线领用", "bin_no": "PK-LINE-01", "remark": "按生产工单发料"},
    },
    "spare_parts": {
        "label": "备件基础台账",
        "permission": "spares_master",
        "columns": [
            ("id", "备件编码"),
            ("name", "备件名称"),
            ("spec", "规格型号"),
            ("brand", "品牌"),
            ("category", "类别"),
            ("abc_class", "ABC等级"),
            ("unit", "单位"),
            ("current_qty", "当前库存"),
            ("min_qty", "最低库存"),
            ("safety_qty", "安全库存"),
            ("max_qty", "最高库存"),
            ("lead_days", "采购周期"),
            ("unit_price", "单价"),
            ("supplier", "供应商"),
            ("location", "货位"),
            ("equipment_name", "适用设备"),
            ("equipment_code", "设备编号"),
            ("food_contact", "食品接触"),
            ("imported", "进口件"),
            ("critical", "关键备件"),
            ("expiry_date", "有效期"),
            ("remark", "备注"),
        ],
        "sample": {"id": "SP-ME-EX01-0009", "name": "膨化机切刀", "spec": "EX01-刀片套件", "brand": "原厂", "category": "机械类", "abc_class": "A", "unit": "套", "current_qty": "2", "min_qty": "1", "safety_qty": "2", "max_qty": "4", "lead_days": "30", "unit_price": "2800", "supplier": "原厂供应商", "location": "SP-A-01-01", "equipment_name": "1号膨化线", "equipment_code": "EX01", "food_contact": "是", "imported": "否", "critical": "是", "expiry_date": "", "remark": "食品接触件，需保留合格证明"},
    },
    "spare_receipts": {
        "label": "备件入库",
        "permission": "spares",
        "columns": [
            ("part_id", "备件编码"),
            ("qty", "数量"),
            ("ref_no", "采购订单号"),
            ("supplier", "供应商"),
            ("location", "货位"),
            ("approver", "验收人"),
            ("keeper", "库管员"),
            ("note", "备注"),
        ],
        "sample": {"part_id": "SP-ME-EX01-0001", "qty": "2", "ref_no": "PO-SP-001", "supplier": "原厂供应商", "location": "SP-A-01-01", "approver": "设备工程师", "keeper": "备件库管", "note": "外观、型号、食品级证明已核对"},
    },
    "spare_issues": {
        "label": "备件领用",
        "permission": "spares",
        "columns": [
            ("part_id", "备件编码"),
            ("qty", "数量"),
            ("work_order", "工单号"),
            ("equipment_name", "设备名称"),
            ("equipment_code", "设备编号"),
            ("reason", "领用原因"),
            ("requester", "领用人"),
            ("approver", "审批人"),
            ("keeper", "发料人"),
            ("old_part_status", "旧件处理"),
            ("food_clearance", "清场确认"),
            ("note", "备注"),
        ],
        "sample": {"part_id": "SP-PK-PK01-0001", "qty": "1", "work_order": "WO-SP-001", "equipment_name": "1号包装机", "equipment_code": "PK01", "reason": "计划保养", "requester": "维修人员", "approver": "维修主管", "keeper": "备件库管", "old_part_status": "退库", "food_clearance": "是", "note": "更换后设备恢复正常"},
    },
}

HEADER_ALIASES = {
    "货品": "goods_id",
    "货品编号": "goods_id",
    "商品编号": "goods_id",
    "成品sku": "goods_id",
    "包材编码": "goods_id",
    "包材编号": "goods_id",
    "sku": "goods_id",
    "goodsid": "goods_id",
    "goods_id": "goods_id",
    "数量": "qty",
    "标准单位数量": "qty",
    "qty": "qty",
    "库位": "location_id",
    "上架库位": "location_id",
    "成品库位": "location_id",
    "包材库位": "location_id",
    "location": "location_id",
    "locationid": "location_id",
    "location_id": "location_id",
    "供应商": "supplier",
    "供应商/来源": "supplier",
    "来源": "supplier",
    "批次": "supplier_batch",
    "供应商批次": "supplier_batch",
    "生产批次": "supplier_batch",
    "batch": "supplier_batch",
    "生产日期": "production_date",
    "productiondate": "production_date",
    "production_date": "production_date",
    "过期日期": "expiry_date",
    "bbd": "expiry_date",
    "expirydate": "expiry_date",
    "expiry_date": "expiry_date",
    "po": "po_no",
    "po/单号": "po_no",
    "单号": "po_no",
    "生产工单": "po_no",
    "采购单号": "po_no",
    "pono": "po_no",
    "po_no": "po_no",
    "货主": "owner",
    "owner": "owner",
    "品质": "quality_status",
    "品质状态": "quality_status",
    "quality": "quality_status",
    "quality_status": "quality_status",
    "备注": "remark",
    "remark": "remark",
    "去向": "destination",
    "领用去向": "destination",
    "destination": "destination",
    "料仓": "bin_no",
    "料仓/月台": "bin_no",
    "bin": "bin_no",
    "bin_no": "bin_no",
    "月台": "ship_dock",
    "装车口": "ship_dock",
    "月台/装车口": "ship_dock",
    "ship_dock": "ship_dock",
    "客户": "customer",
    "客户/渠道": "customer",
    "customer": "customer",
    "渠道": "channel_code",
    "渠道编码": "channel_code",
    "channel": "channel_code",
    "channel_code": "channel_code",
    "最小剩余效期": "min_remaining_days",
    "最小剩余天数": "min_remaining_days",
    "min_remaining_days": "min_remaining_days",
    "销售订单": "order_no",
    "order_no": "order_no",
    "产线": "production_line",
    "产线/班组": "production_line",
    "production_line": "production_line",
    "名称": "name",
    "name": "name",
    "类别": "category",
    "category": "category",
    "单位": "unit",
    "unit": "unit",
    "最低库存": "min_qty",
    "最低库存量": "min_qty",
    "min_qty": "min_qty",
    "安全库存": "safety_qty",
    "安全库存量": "safety_qty",
    "safety_qty": "safety_qty",
    "临期提醒天数": "expiry_alert_days",
    "临期提前天数": "expiry_alert_days",
    "近效期提醒天数": "expiry_alert_days",
    "提前提醒天数": "expiry_alert_days",
    "expiry_alert_days": "expiry_alert_days",
    "courbon": "courbon",
    "mes": "courbon",
    "mes连接": "courbon",
    "mes物料": "courbon",
    "保质期天数": "shelf_days",
    "shelf_days": "shelf_days",
    "库位编号": "id",
    "编号": "id",
    "id": "id",
    "仓库": "area",
    "area": "area",
    "库区": "zone",
    "zone": "zone",
    "类型": "type",
    "type": "type",
    "分配优先级": "priority",
    "priority": "priority",
    "容量": "capacity",
    "capacity": "capacity",
    "备件编码": "part_id",
    "备件编号": "part_id",
    "备件": "part_id",
    "partid": "part_id",
    "part_id": "part_id",
    "备件名称": "name",
    "规格型号": "spec",
    "规格": "spec",
    "型号": "spec",
    "spec": "spec",
    "品牌": "brand",
    "brand": "brand",
    "abc等级": "abc_class",
    "等级": "abc_class",
    "abc_class": "abc_class",
    "当前库存": "current_qty",
    "current_qty": "current_qty",
    "最高库存": "max_qty",
    "max_qty": "max_qty",
    "采购周期": "lead_days",
    "lead_days": "lead_days",
    "单价": "unit_price",
    "unit_price": "unit_price",
    "适用设备": "equipment_name",
    "设备名称": "equipment_name",
    "equipment_name": "equipment_name",
    "设备编号": "equipment_code",
    "equipment_code": "equipment_code",
    "食品接触": "food_contact",
    "食品接触件": "food_contact",
    "food_contact": "food_contact",
    "进口件": "imported",
    "是否进口件": "imported",
    "imported": "imported",
    "关键备件": "critical",
    "是否关键备件": "critical",
    "critical": "critical",
    "有效期": "expiry_date",
    "工单号": "work_order",
    "维修工单": "work_order",
    "work_order": "work_order",
    "领用原因": "reason",
    "原因": "reason",
    "reason": "reason",
    "领用人": "requester",
    "申请人": "requester",
    "requester": "requester",
    "审批人": "approver",
    "验收人": "approver",
    "approver": "approver",
    "库管员": "keeper",
    "发料人": "keeper",
    "keeper": "keeper",
    "旧件处理": "old_part_status",
    "旧件状态": "old_part_status",
    "old_part_status": "old_part_status",
    "清场确认": "food_clearance",
    "food_clearance": "food_clearance",
}


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_id(prefix: str) -> str:
    return f"{prefix}{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        method, salt, expected = stored_hash.split("$", 2)
    except ValueError:
        return False
    if method != "pbkdf2_sha256":
        return False
    actual = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(actual, expected)


def role_permissions(role: str) -> list[str]:
    return ROLE_PERMISSIONS.get(role, ["view"])


def public_user(user: dict) -> dict:
    permissions = role_permissions(user["role"])
    return {
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
        "role_label": ROLE_LABELS.get(user["role"], user["role"]),
        "permissions": permissions,
    }


def row_to_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def ensure_schema_migrations(conn: sqlite3.Connection) -> None:
    product_columns = table_columns(conn, "products")
    if "safety_qty" not in product_columns:
        conn.execute("ALTER TABLE products ADD COLUMN safety_qty REAL NOT NULL DEFAULT 0")
        conn.execute("UPDATE products SET safety_qty = min_qty WHERE safety_qty = 0")
    if "expiry_alert_days" not in product_columns:
        conn.execute("ALTER TABLE products ADD COLUMN expiry_alert_days INTEGER NOT NULL DEFAULT 60")
    count_columns = table_columns(conn, "counts")
    if "count_type" not in count_columns:
        conn.execute("ALTER TABLE counts ADD COLUMN count_type TEXT NOT NULL DEFAULT '日常盘点'")
    if "scope" not in count_columns:
        conn.execute("ALTER TABLE counts ADD COLUMN scope TEXT")
    if "operator" not in count_columns:
        conn.execute("ALTER TABLE counts ADD COLUMN operator TEXT")
    if "adjusted" not in count_columns:
        conn.execute("ALTER TABLE counts ADD COLUMN adjusted INTEGER NOT NULL DEFAULT 0")
    outbound_columns = table_columns(conn, "outbound_orders")
    if "channel_code" not in outbound_columns:
        conn.execute("ALTER TABLE outbound_orders ADD COLUMN channel_code TEXT")
    if "min_remaining_days" not in outbound_columns:
        conn.execute("ALTER TABLE outbound_orders ADD COLUMN min_remaining_days INTEGER NOT NULL DEFAULT 0")
    recall_columns = table_columns(conn, "recall_orders")
    if recall_columns and "affected_sscc" not in recall_columns:
        conn.execute("ALTER TABLE recall_orders ADD COLUMN affected_sscc TEXT")
    if recall_columns and "affected_shipment_ids" not in recall_columns:
        conn.execute("ALTER TABLE recall_orders ADD COLUMN affected_shipment_ids TEXT")


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        ensure_schema_migrations(conn)
        ensure_default_users(conn)
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if product_count:
            ensure_finished_goods_data(conn)
            ensure_packaging_data(conn)
            ensure_spare_parts_data(conn)
            ensure_tms_data(conn)
            return
        seed_demo_data(conn)


def seed_demo_data(conn: sqlite3.Connection) -> None:
    products = [
        ("3637", "鸡肉粉", "原料", "kg", 800, 1000, 90, 1, 365),
        ("3726", "小麦蛋白粉", "原料", "kg", 600, 800, 90, 1, 365),
        ("7002", "普通返工料", "返工料", "kg", 300, 500, 30, 0, 180),
        ("OIL-EDL3", "鱼油 EDL3", "液体原料", "kg", 200, 300, 45, 0, 240),
    ] + PACKAGING_PRODUCTS + FINISHED_PRODUCTS
    conn.executemany(
        """
        INSERT INTO products(id, name, category, unit, min_qty, safety_qty, expiry_alert_days, courbon, shelf_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products,
    )

    locations = [
        ("RM-S01", "原料仓", "取样后优先使用区", "优先货位", 1, 8000),
        ("RB-S02", "红蓝通道", "投料待用区", "生产前置", 2, 6000),
        ("RM-A01-01", "原料仓", "A01 货架", "正常货位", 3, 12000),
        ("RM-A02-01", "原料仓", "A02 货架", "正常货位", 4, 12000),
        ("QC-HOLD", "质量区", "待检/隔离", "冻结货位", 9, 5000),
    ] + PACKAGING_LOCATIONS + FINISHED_LOCATIONS
    conn.executemany(
        "INSERT INTO locations(id, area, zone, type, priority, capacity) VALUES (?, ?, ?, ?, ?, ?)",
        locations,
    )

    stocks = [
        ("SSCC202606020001", "3637", "MARS-RMR", "RM-A01-01", 1250, 0, "kg", "2026-03-01", "2026-12-01", "C3637-0325", "PO260601", "合格"),
        ("SSCC202606020002", "3637", "MARS-RMR", "RM-S01", 900, 0, "kg", "2026-02-10", "2026-08-15", "C3637-0210", "PO260522", "合格"),
        ("SSCC202606020003", "3726", "MARS-RMR", "RM-A02-01", 680, 0, "kg", "2026-01-08", "2026-10-11", "W3726-0108", "PO260506", "合格"),
        ("SSCC202606020004", "7002", "MARS-RMR", "RB-S02", 420, 0, "kg", "2026-05-20", "2026-09-20", "RW7002-0520", "RW260520", "合格"),
        ("SSCC202606020005", "OIL-EDL3", "MARS-RMR", "RM-S01", 310, 0, "kg", "2026-01-12", "2026-07-31", "EDL3-0112", "PO260430", "合格"),
    ] + PACKAGING_STOCKS + FINISHED_STOCKS
    conn.executemany(
        """
        INSERT INTO stock_units(
            sscc, goods_id, owner, location_id, qty, reserved_qty, unit,
            production_date, expiry_date, supplier_batch, po_no, quality_status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [(*item, now_text()) for item in stocks],
    )

    for stock in stocks:
        conn.execute(
            """
            INSERT INTO ledger(ts, action, ref_id, sscc, goods_id, location_id, qty, before_qty, after_qty, note)
            VALUES (?, '初始化库存', 'SEED', ?, ?, ?, ?, 0, ?, ?)
            """,
            (now_text(), stock[0], stock[1], stock[3], stock[4], stock[4], "系统样例数据"),
        )
    seed_spare_parts_data(conn)
    ensure_tms_data(conn)


def ensure_finished_goods_data(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO products(id, name, category, unit, min_qty, safety_qty, expiry_alert_days, courbon, shelf_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        FINISHED_PRODUCTS,
    )
    conn.executemany(
        """
        INSERT INTO locations(id, area, zone, type, priority, capacity)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        FINISHED_LOCATIONS,
    )
    for stock in FINISHED_STOCKS:
        exists = conn.execute("SELECT 1 FROM stock_units WHERE sscc = ?", (stock[0],)).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO stock_units(
                sscc, goods_id, owner, location_id, qty, reserved_qty, unit,
                production_date, expiry_date, supplier_batch, po_no, quality_status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*stock, now_text()),
        )
        conn.execute(
            """
            INSERT INTO ledger(ts, action, ref_id, sscc, goods_id, location_id, qty, before_qty, after_qty, note)
            VALUES (?, '成品样例补齐', 'SEED-FG', ?, ?, ?, ?, 0, ?, ?)
            """,
            (now_text(), stock[0], stock[1], stock[3], stock[4], stock[4], "自动补齐成品WMS样例数据"),
        )


def ensure_packaging_data(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO products(id, name, category, unit, min_qty, safety_qty, expiry_alert_days, courbon, shelf_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        PACKAGING_PRODUCTS,
    )
    conn.executemany(
        """
        INSERT INTO locations(id, area, zone, type, priority, capacity)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        PACKAGING_LOCATIONS,
    )
    for stock in PACKAGING_STOCKS:
        exists = conn.execute("SELECT 1 FROM stock_units WHERE sscc = ?", (stock[0],)).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO stock_units(
                sscc, goods_id, owner, location_id, qty, reserved_qty, unit,
                production_date, expiry_date, supplier_batch, po_no, quality_status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (*stock, now_text()),
        )
        conn.execute(
            """
            INSERT INTO ledger(ts, action, ref_id, sscc, goods_id, location_id, qty, before_qty, after_qty, note)
            VALUES (?, '包材样例补齐', 'SEED-PKG', ?, ?, ?, ?, 0, ?, ?)
            """,
            (now_text(), stock[0], stock[1], stock[3], stock[4], stock[4], "自动补齐包材WMS样例数据"),
        )


def seed_spare_parts_data(conn: sqlite3.Connection) -> None:
    for part in SPARE_PARTS:
        save_spare_part(conn, part, seed=True)
        qty = float(part["current_qty"])
        if qty <= 0:
            continue
        log_spare_transaction(
            conn,
            action="初始化备件",
            part_id=part["id"],
            qty=qty,
            before_qty=0,
            after_qty=qty,
            unit_price=float(part["unit_price"]),
            location=str(part["location"]),
            ref_no="SEED-SP",
            note="系统样例备件库存",
        )


def ensure_tms_data(conn: sqlite3.Connection) -> None:
    now = now_text()
    for carrier in TMS_CARRIERS:
        conn.execute(
            """
            INSERT INTO tms_carriers(code, name, contact, phone, service_type, cold_chain, active, score, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(code) DO NOTHING
            """,
            (*carrier, now),
        )
    for lane in TMS_LANES:
        conn.execute(
            """
            INSERT INTO tms_lanes(code, origin, destination, carrier_code, transit_days, temp_min, temp_max, base_fee, fee_per_unit, active, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ON CONFLICT(code) DO NOTHING
            """,
            (*lane, now),
        )
    for rule in CHANNEL_EXPIRY_RULES:
        conn.execute(
            """
            INSERT INTO channel_expiry_rules(
                id, channel_code, channel_name, goods_id, min_remaining_days,
                allow_near_expiry, require_quality_release, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(channel_code, goods_id) DO UPDATE SET
                channel_name = excluded.channel_name,
                min_remaining_days = excluded.min_remaining_days,
                allow_near_expiry = excluded.allow_near_expiry,
                require_quality_release = excluded.require_quality_release,
                updated_at = excluded.updated_at
            """,
            (f"EXP-{rule[0]}-{rule[2]}", *rule, now),
        )


def ensure_spare_parts_data(conn: sqlite3.Connection) -> None:
    exists = conn.execute("SELECT COUNT(*) FROM spare_parts").fetchone()[0]
    if exists:
        return
    seed_spare_parts_data(conn)


def ensure_default_users(conn: sqlite3.Connection) -> None:
    for username, display_name, role, password in DEFAULT_USERS:
        exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO users(username, display_name, role, password_hash, active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (username, display_name, role, hash_password(password), now_text()),
        )


def fetch_all(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [row_to_dict(row) for row in conn.execute(sql, params).fetchall()]


def fetch_one(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> dict | None:
    row = conn.execute(sql, params).fetchone()
    return row_to_dict(row) if row else None


def authenticate_user(conn: sqlite3.Connection, username: str, password: str) -> dict | None:
    user = fetch_one(conn, "SELECT * FROM users WHERE username = ? AND active = 1", (username,))
    if not user or not verify_password(password, user["password_hash"]):
        return None
    conn.execute("UPDATE users SET last_login = ? WHERE username = ?", (now_text(), username))
    return user


def create_session(conn: sqlite3.Connection, username: str) -> str:
    token = secrets.token_urlsafe(32)
    created_at = now_text()
    expires_at = (datetime.now() + timedelta(days=SESSION_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO sessions(token, username, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, username, created_at, expires_at),
    )
    return token


def delete_session(conn: sqlite3.Connection, token: str | None) -> None:
    if token:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def user_from_session(conn: sqlite3.Connection, token: str | None) -> dict | None:
    if not token:
        return None
    session = fetch_one(conn, "SELECT * FROM sessions WHERE token = ?", (token,))
    if not session:
        return None
    try:
        expired = datetime.strptime(session["expires_at"], "%Y-%m-%d %H:%M:%S") < datetime.now()
    except ValueError:
        expired = True
    if expired:
        delete_session(conn, token)
        return None
    return fetch_one(conn, "SELECT * FROM users WHERE username = ? AND active = 1", (session["username"],))


def require_permission(user: dict | None, permission: str) -> None:
    if not user:
        raise PermissionError("请先登录")
    if permission not in role_permissions(user["role"]):
        raise PermissionError("当前账号没有该功能权限")


def positive_number(value: object, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} 必须是数字")
    if number <= 0:
        raise ValueError(f"{field_name} 必须大于 0")
    return number


def require_text(data: dict, field_name: str) -> str:
    value = str(data.get(field_name, "")).strip()
    if not value:
        raise ValueError(f"{field_name} 不能为空")
    return value


def nonnegative_int(value: object, default: int = 0) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(0, number)


def days_until_today(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return (date.fromisoformat(text[:10]) - date.today()).days
    except ValueError:
        return None


def channel_expiry_rule(conn: sqlite3.Connection, goods_id: str, channel_code: str) -> dict | None:
    if not channel_code:
        return None
    return fetch_one(
        conn,
        """
        SELECT *
        FROM channel_expiry_rules
        WHERE goods_id = ? AND UPPER(channel_code) = UPPER(?)
        """,
        (goods_id, channel_code),
    )


def stock_meets_remaining_days(expiry_date: object, min_remaining_days: int) -> bool:
    if min_remaining_days <= 0:
        return True
    remaining = days_until_today(expiry_date)
    return remaining is not None and remaining >= min_remaining_days


def log_ledger(
    conn: sqlite3.Connection,
    action: str,
    ref_id: str | None,
    sscc: str | None,
    goods_id: str | None,
    location_id: str | None,
    qty: float | None,
    before_qty: float | None,
    after_qty: float | None,
    note: str | None,
) -> None:
    conn.execute(
        """
        INSERT INTO ledger(ts, action, ref_id, sscc, goods_id, location_id, qty, before_qty, after_qty, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (now_text(), action, ref_id, sscc, goods_id, location_id, qty, before_qty, after_qty, note),
    )


def scrub_payload(value: object) -> str:
    if not isinstance(value, dict):
        return ""
    scrubbed = {}
    for key, item in value.items():
        if key.startswith("_"):
            continue
        if "password" in key.lower() or key == "token":
            scrubbed[key] = "***"
        else:
            scrubbed[key] = item
    return json.dumps(scrubbed, ensure_ascii=False, default=str)[:2000]


def log_operation(
    conn: sqlite3.Connection,
    method: str,
    path: str,
    status_code: int,
    user: dict | None = None,
    action: str = "",
    message: str = "",
    payload: dict | None = None,
    ip: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO operation_logs(ts, username, display_name, role, method, path, status_code, action, message, payload, ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now_text(),
            user["username"] if user else None,
            user["display_name"] if user else None,
            user["role"] if user else None,
            method,
            path,
            status_code,
            action,
            message,
            scrub_payload(payload),
            ip,
        ),
    )


def excel_col_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def xlsx_cell(value: object, row_index: int, col_index: int) -> str:
    ref = f"{excel_col_name(col_index)}{row_index}"
    text = "" if value is None else str(value)
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>'


def make_xlsx(sheet_name: str, columns: list[tuple[str, str]], rows: list[dict]) -> bytes:
    safe_sheet_name = re.sub(r"[\[\]:*?/\\]", "", sheet_name)[:31] or "Sheet1"
    matrix = [[label for _, label in columns]]
    matrix.extend([[row.get(key, "") for key, _ in columns] for row in rows])
    sheet_rows = []
    for row_index, row in enumerate(matrix, start=1):
        cells = "".join(xlsx_cell(value, row_index, col_index) for col_index, value in enumerate(row, start=1))
        sheet_rows.append(f'<row r="{row_index}">{cells}</row>')
    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetData>{''.join(sheet_rows)}</sheetData>
</worksheet>'''
    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="{escape(safe_sheet_name)}" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>'''
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return output.getvalue()


def parse_csv(content: bytes) -> list[dict]:
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = content.decode("utf-8", errors="ignore")
    rows = list(csv.reader(io.StringIO(text)))
    return matrix_to_dicts(rows)


def cell_ref_to_col(ref: str) -> int:
    letters = "".join(ch for ch in ref if ch.isalpha())
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter.upper()) - 64)
    return max(index, 1)


def parse_xlsx(content: bytes) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                shared_strings.append("".join(text.text or "" for text in item.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in archive.namelist():
            sheet_name = next((name for name in archive.namelist() if name.startswith("xl/worksheets/") and name.endswith(".xml")), "")
        if not sheet_name:
            raise ValueError("Excel 文件中没有工作表")
        root = ET.fromstring(archive.read(sheet_name))
    matrix: list[list[str]] = []
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    for row in root.findall(f".//{ns}row"):
        values: dict[int, str] = {}
        for cell in row.findall(f"{ns}c"):
            ref = cell.attrib.get("r", "A1")
            col_index = cell_ref_to_col(ref)
            cell_type = cell.attrib.get("t", "")
            value = ""
            if cell_type == "inlineStr":
                value = "".join(text.text or "" for text in cell.findall(f".//{ns}t"))
            else:
                raw = cell.find(f"{ns}v")
                raw_value = raw.text if raw is not None else ""
                if cell_type == "s" and raw_value != "":
                    value = shared_strings[int(float(raw_value))]
                else:
                    value = raw_value or ""
            values[col_index] = value
        if values:
            max_col = max(values)
            matrix.append([values.get(index, "") for index in range(1, max_col + 1)])
    return matrix_to_dicts(matrix)


def matrix_to_dicts(matrix: list[list[str]]) -> list[dict]:
    cleaned = [[str(cell).strip() for cell in row] for row in matrix if any(str(cell).strip() for cell in row)]
    if not cleaned:
        return []
    headers = [normalize_header(header) for header in cleaned[0]]
    records = []
    for row in cleaned[1:]:
        record = {}
        for index, header in enumerate(headers):
            if not header:
                continue
            record[header] = row[index].strip() if index < len(row) else ""
        if any(value != "" for value in record.values()):
            records.append(normalize_import_record(record))
    return records


def normalize_header(header: str) -> str:
    key = re.sub(r"[\s　:/\\\-]+", "", header.strip().lower())
    return HEADER_ALIASES.get(key, HEADER_ALIASES.get(header.strip().lower(), header.strip()))


def normalize_import_record(record: dict) -> dict:
    normalized = {}
    for key, value in record.items():
        normalized_key = HEADER_ALIASES.get(key.lower(), key)
        normalized[normalized_key] = normalize_cell_value(normalized_key, value)
    return normalized


def normalize_cell_value(key: str, value: object) -> str:
    text = "" if value is None else str(value).strip()
    if key in {"production_date", "expiry_date"} and re.fullmatch(r"\d+(\.0+)?", text):
        serial = int(float(text))
        if serial > 20000:
            return (date(1899, 12, 30) + timedelta(days=serial)).isoformat()
    if key in {"qty", "min_qty", "safety_qty", "max_qty", "capacity", "current_qty", "lead_days", "unit_price", "actual_qty", "expiry_alert_days", "min_remaining_days"} and re.fullmatch(r"-?\d+\.0+", text):
        return str(int(float(text)))
    return text


def parse_spreadsheet(filename: str, content: bytes) -> list[dict]:
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return parse_csv(content)
    if lower_name.endswith(".xlsx"):
        return parse_xlsx(content)
    raise ValueError("只支持 .xlsx 或 .csv 文件")


def truthy_excel(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是", "启用", "连接"}


def export_rows(conn: sqlite3.Connection, dataset: str) -> tuple[str, list[tuple[str, str]], list[dict]]:
    if dataset.startswith("template_"):
        import_type = dataset.replace("template_", "", 1)
        schema = IMPORT_SCHEMAS.get(import_type)
        if not schema:
            raise ValueError("导出模板不存在")
        return f"{schema['label']}模板", schema["columns"], [schema["sample"]]
    if dataset == "inventory":
        columns = [
            ("sscc", "SSCC"), ("goods_id", "GoodsID"), ("goods_name", "名称"), ("category", "类别"),
            ("location_id", "库位"), ("area", "仓库"), ("zone", "库区"), ("qty", "在库"),
            ("reserved_qty", "保留"), ("available_qty", "可用"), ("unit", "单位"), ("quality_status", "品质"),
            ("production_date", "生产日期"), ("expiry_date", "BBD"), ("supplier_batch", "批次"), ("po_no", "单号"),
        ]
        rows = fetch_all(conn, """
            SELECT s.*, ROUND(s.qty - s.reserved_qty, 3) AS available_qty, p.name AS goods_name, p.category, l.area, l.zone
            FROM stock_units s JOIN products p ON p.id = s.goods_id JOIN locations l ON l.id = s.location_id
            WHERE s.qty > 0 ORDER BY l.priority, s.goods_id, s.sscc
        """)
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "finished_inventory":
        title, columns, rows = export_rows(conn, "inventory")
        return EXPORT_DATASETS[dataset], columns, [row for row in rows if row["category"] == "成品"]
    if dataset == "packaging_inventory":
        title, columns, rows = export_rows(conn, "inventory")
        return EXPORT_DATASETS[dataset], columns, [row for row in rows if row["category"] == "包材"]
    if dataset == "packaging_warnings":
        columns = [
            ("id", "包材编码"), ("name", "名称"), ("available", "可用库存"), ("min_qty", "最低库存"),
            ("safety_qty", "安全库存"), ("reorder_qty", "建议补足"), ("unit", "单位"), ("stock_status_label", "预警状态"),
        ]
        return EXPORT_DATASETS[dataset], columns, bootstrap_payload(conn)["packaging"]["low_stock"]
    if dataset == "products":
        columns = [
            ("id", "GoodsID"), ("name", "名称"), ("category", "类别"), ("unit", "单位"),
            ("min_qty", "最低库存"), ("safety_qty", "安全库存"), ("expiry_alert_days", "临期提醒天数"),
            ("courbon", "MES"), ("shelf_days", "保质期天数"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM products ORDER BY category, id")
    if dataset == "locations":
        columns = [("id", "库位编号"), ("area", "仓库"), ("zone", "库区"), ("type", "类型"), ("priority", "分配优先级"), ("capacity", "容量")]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM locations ORDER BY priority, id")
    if dataset == "inbounds":
        columns = [("id", "入库单"), ("goods_id", "GoodsID"), ("goods_name", "名称"), ("category", "类别"), ("received_qty", "数量"), ("unit", "单位"), ("sscc", "SSCC"), ("location_id", "库位"), ("supplier", "来源"), ("supplier_batch", "批次"), ("production_date", "生产日期"), ("expiry_date", "BBD"), ("created_at", "时间"), ("remark", "备注")]
        rows = fetch_all(conn, "SELECT i.*, p.name AS goods_name, p.category, p.unit FROM inbound_orders i JOIN products p ON p.id = i.goods_id ORDER BY i.created_at DESC")
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "outbounds":
        columns = [("id", "出库单"), ("goods_id", "GoodsID"), ("goods_name", "名称"), ("category", "类别"), ("qty", "需求"), ("allocated_qty", "分配"), ("shortage_qty", "欠品"), ("unit", "单位"), ("status", "状态"), ("destination", "去向"), ("channel_code", "渠道"), ("min_remaining_days", "最小剩余效期"), ("bin_no", "料仓/月台"), ("created_at", "创建时间"), ("confirmed_at", "确认时间"), ("remark", "备注")]
        rows = fetch_all(conn, "SELECT o.*, p.name AS goods_name, p.category, p.unit FROM outbound_orders o JOIN products p ON p.id = o.goods_id ORDER BY o.created_at DESC")
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "ledger":
        columns = [("ts", "时间"), ("action", "动作"), ("ref_id", "来源单"), ("sscc", "SSCC"), ("goods_id", "GoodsID"), ("location_id", "库位"), ("qty", "数量"), ("before_qty", "前值"), ("after_qty", "后值"), ("note", "备注")]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM ledger ORDER BY id DESC")
    if dataset == "operation_logs":
        columns = [
            ("ts", "时间"), ("username", "账号"), ("display_name", "姓名"), ("role", "角色"),
            ("method", "方法"), ("path", "接口"), ("status_code", "状态码"), ("action", "动作"),
            ("message", "结果"), ("payload", "请求内容"), ("ip", "IP"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM operation_logs ORDER BY id DESC LIMIT 1000")
    if dataset == "label_prints":
        columns = [
            ("ts", "时间"), ("label_type", "标签类型"), ("template_name", "模板"), ("goods_id", "GoodsID"),
            ("goods_name", "名称"), ("category", "类别"), ("batch_no", "批号"), ("supplier_batch", "供应商批次"),
            ("production_date", "生产日期"), ("expiry_date", "BBD/效期"), ("qty", "数量"), ("unit", "单位"),
            ("location_id", "库位"), ("sscc", "SSCC"), ("quality_status", "品质"), ("code_type", "码制"),
            ("barcode_value", "条码值"), ("qr_value", "二维码值"), ("copies", "份数"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM label_prints ORDER BY ts DESC LIMIT 1000")
    if dataset == "stock_warnings":
        columns = [
            ("id", "GoodsID"), ("name", "名称"), ("category", "类别"), ("available", "可用库存"),
            ("min_qty", "最低库存"), ("safety_qty", "安全库存"), ("reorder_qty", "建议补足"),
            ("unit", "单位"), ("stock_status_label", "预警状态"),
        ]
        return EXPORT_DATASETS[dataset], columns, bootstrap_payload(conn)["stock_warnings"]
    if dataset == "expiry_warnings":
        columns = [
            ("sscc", "SSCC"), ("goods_id", "GoodsID"), ("goods_name", "名称"), ("category", "类别"),
            ("location_id", "库位"), ("qty", "在库"), ("unit", "单位"), ("quality_status", "品质"),
            ("production_date", "生产日期"), ("expiry_date", "BBD"), ("days_left", "剩余天数"),
            ("expiry_alert_days", "提醒天数"), ("expiry_status_label", "临期状态"), ("supplier_batch", "批次"),
        ]
        return EXPORT_DATASETS[dataset], columns, bootstrap_payload(conn)["expiry_warnings"]
    if dataset in {"spare_parts", "spare_warnings"}:
        columns = [
            ("id", "备件编码"), ("name", "备件名称"), ("spec", "规格型号"), ("brand", "品牌"), ("category", "类别"),
            ("abc_class", "ABC等级"), ("unit", "单位"), ("current_qty", "当前库存"), ("min_qty", "最低库存"),
            ("safety_qty", "安全库存"), ("max_qty", "最高库存"), ("stock_status_label", "预警状态"), ("stock_value", "库存金额"),
            ("lead_days", "采购周期"), ("unit_price", "单价"), ("supplier", "供应商"), ("location", "货位"),
            ("equipment_name", "适用设备"), ("equipment_code", "设备编号"), ("food_contact", "食品接触"),
            ("imported", "进口件"), ("critical", "关键备件"), ("expiry_date", "有效期"), ("remark", "备注"),
        ]
        rows = spare_parts_with_status(conn)
        if dataset == "spare_warnings":
            rows = [row for row in rows if row["stock_status"] != "ok"]
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "spare_transactions":
        columns = [
            ("ts", "时间"), ("action", "动作"), ("part_id", "备件编码"), ("part_name", "备件名称"), ("spec", "规格型号"),
            ("qty", "数量"), ("before_qty", "前值"), ("after_qty", "后值"), ("unit_price", "单价"), ("amount", "金额"),
            ("location", "货位"), ("ref_no", "来源单/采购单"), ("work_order", "工单号"), ("equipment_name", "设备名称"),
            ("equipment_code", "设备编号"), ("reason", "原因"), ("requester", "领用人"), ("approver", "审批/验收人"),
            ("keeper", "库管员"), ("old_part_status", "旧件处理"), ("food_clearance", "清场确认"), ("note", "备注"),
        ]
        rows = fetch_all(
            conn,
            """
            SELECT t.*, p.name AS part_name, p.spec
            FROM spare_transactions t
            JOIN spare_parts p ON p.id = t.part_id
            ORDER BY t.ts DESC, t.id DESC
            """,
        )
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "tms_shipments":
        columns = [
            ("id", "运单号"), ("status", "状态"), ("source_outbound_id", "WMS发货单"), ("wave_id", "波次"),
            ("carrier_name", "承运商"), ("lane_code", "线路"), ("customer", "客户"), ("destination", "目的地"),
            ("vehicle_no", "车牌"), ("driver", "司机"), ("seal_no", "封签"), ("planned_departure", "计划发车"),
            ("actual_departure", "实际发车"), ("eta", "ETA"), ("actual_arrival", "实际到达"),
            ("temp_min", "温控下限"), ("temp_max", "温控上限"), ("exception_note", "异常"),
            ("estimated_fee", "预估运费"), ("actual_fee", "实际运费"), ("billing_status", "对账状态"),
        ]
        rows = fetch_all(
            conn,
            """
            SELECT s.*, c.name AS carrier_name
            FROM tms_shipments s
            JOIN tms_carriers c ON c.code = s.carrier_code
            ORDER BY s.created_at DESC
            """,
        )
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "tms_events":
        columns = [
            ("event_time", "时间"), ("shipment_id", "运单号"), ("event_type", "事件"),
            ("location_text", "位置"), ("temperature", "温度"), ("humidity", "湿度"),
            ("door_open", "开门"), ("risk_level", "风险"), ("note", "备注"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM tms_events ORDER BY event_time DESC")
    if dataset == "tms_pods":
        columns = [
            ("shipment_id", "运单号"), ("signed_by", "签收人"), ("signed_at", "签收时间"),
            ("received_qty", "实收"), ("damaged_qty", "破损"), ("shortage_qty", "短少"),
            ("note", "备注"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM tms_pods ORDER BY signed_at DESC")
    if dataset == "tms_freight_bills":
        columns = [
            ("id", "运费账单"), ("shipment_id", "运单号"), ("carrier_code", "承运商"),
            ("estimated_fee", "预估运费"), ("actual_fee", "实际运费"), ("difference", "差异"),
            ("billing_status", "对账状态"), ("exception_reason", "差异原因"),
            ("confirmed_by", "确认人"), ("confirmed_at", "确认时间"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM tms_freight_bills ORDER BY updated_at DESC")
    if dataset == "tms_performance":
        columns = [
            ("carrier_code", "承运商编码"), ("carrier_name", "承运商"), ("shipment_count", "运单数"),
            ("otif_rate", "OTIF%"), ("pod_rate", "POD及时率%"), ("temperature_exception_rate", "温控异常率%"),
            ("fee_variance_rate", "费用偏差率%"), ("score", "综合评分"),
        ]
        return EXPORT_DATASETS[dataset], columns, tms_carrier_performance(conn)
    if dataset == "tms_iot_telemetry":
        columns = [
            ("telemetry_time", "时间"), ("shipment_id", "运单号"), ("device_id", "设备号"),
            ("latitude", "纬度"), ("longitude", "经度"), ("location_text", "位置"),
            ("temperature", "温度"), ("humidity", "湿度"), ("door_open", "开门"),
            ("reefer_status", "冷机状态"), ("speed", "速度"), ("risk_level", "风险"), ("note", "备注"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM tms_iot_telemetry ORDER BY telemetry_time DESC")
    if dataset == "tms_driver_tasks":
        columns = [
            ("id", "司机任务"), ("shipment_id", "运单号"), ("driver", "司机"), ("driver_phone", "司机电话"),
            ("vehicle_no", "车牌"), ("task_status", "任务状态"), ("pickup_location", "提货点"),
            ("delivery_location", "送达点"), ("pin_code", "签收码"), ("assigned_at", "派单时间"),
            ("accepted_at", "接单时间"), ("departed_at", "发车时间"), ("arrived_at", "到达时间"),
            ("signed_at", "签收时间"), ("pod_note", "POD备注"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM tms_driver_tasks ORDER BY updated_at DESC")
    if dataset == "integration_events":
        columns = [
            ("created_at", "时间"), ("system_name", "系统"), ("direction", "方向"), ("event_type", "事件"),
            ("object_type", "对象类型"), ("object_id", "对象ID"), ("status", "状态"),
            ("message", "消息"), ("processed_at", "处理时间"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM integration_events ORDER BY created_at DESC LIMIT 2000")
    if dataset == "audit_packages":
        columns = [
            ("id", "审计包"), ("package_type", "类型"), ("ref_id", "对象"), ("title", "标题"),
            ("status", "状态"), ("summary", "摘要"), ("created_at", "时间"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT id, package_type, ref_id, title, status, summary, created_at, operator FROM audit_packages ORDER BY created_at DESC")
    if dataset == "channel_expiry_rules":
        columns = [
            ("channel_code", "渠道编码"), ("channel_name", "渠道"), ("goods_id", "GoodsID"),
            ("goods_name", "名称"), ("min_remaining_days", "最小剩余效期"),
            ("allow_near_expiry", "允许临期"), ("require_quality_release", "必须放行"),
            ("updated_at", "更新时间"),
        ]
        rows = fetch_all(conn, "SELECT r.*, p.name AS goods_name FROM channel_expiry_rules r JOIN products p ON p.id = r.goods_id ORDER BY r.channel_code, r.goods_id")
        return EXPORT_DATASETS[dataset], columns, rows
    if dataset == "recalls":
        columns = [
            ("id", "召回单"), ("goods_id", "GoodsID"), ("supplier_batch", "批次"), ("reason", "原因"),
            ("affected_inventory", "在库影响"), ("affected_shipments", "运单影响"),
            ("affected_sscc", "命中SSCC"), ("affected_shipment_ids", "命中运单"),
            ("status", "状态"),
            ("created_at", "时间"), ("operator", "操作人"),
        ]
        return EXPORT_DATASETS[dataset], columns, fetch_all(conn, "SELECT * FROM recall_orders ORDER BY created_at DESC")
    raise ValueError("导出数据集不存在")


def import_rows(conn: sqlite3.Connection, import_type: str, rows: list[dict], user: dict) -> int:
    schema = IMPORT_SCHEMAS.get(import_type)
    if not schema:
        raise ValueError("导入类型不存在")
    require_permission(user, schema["permission"])
    if not rows:
        raise ValueError("Excel 中没有可导入的数据行")
    imported = 0
    for index, row in enumerate(rows, start=2):
        payload = {key: value for key, value in row.items() if value != ""}
        try:
            if import_type == "products":
                if "id" not in payload and "goods_id" in payload:
                    payload["id"] = payload["goods_id"]
                payload["courbon"] = truthy_excel(payload.get("courbon", ""))
                add_product(conn, payload)
            elif import_type == "locations":
                if "id" not in payload and "location_id" in payload:
                    payload["id"] = payload["location_id"]
                add_location(conn, payload)
            elif import_type == "inbounds":
                create_inbound(conn, payload)
            elif import_type == "outbounds":
                create_outbound(conn, payload)
            elif import_type == "finished_receipts":
                create_finished_receipt(conn, payload)
            elif import_type == "finished_shipments":
                create_finished_shipment(conn, payload)
            elif import_type == "packaging_receipts":
                create_packaging_receipt(conn, payload)
            elif import_type == "packaging_issues":
                create_packaging_issue(conn, payload)
            elif import_type == "spare_parts":
                if "id" not in payload and "part_id" in payload:
                    payload["id"] = payload["part_id"]
                save_spare_part(conn, payload)
            elif import_type == "spare_receipts":
                create_spare_receipt(conn, payload)
            elif import_type == "spare_issues":
                create_spare_issue(conn, payload)
            else:
                raise ValueError("导入类型不存在")
        except Exception as exc:
            raise ValueError(f"第 {index} 行导入失败：{exc}") from exc
        imported += 1
    return imported


def days_until(expiry_date: object, today: date) -> int | None:
    value = str(expiry_date or "").strip()
    if not value:
        return None
    try:
        expiry = date.fromisoformat(value[:10])
    except ValueError:
        return None
    return (expiry - today).days


def enrich_expiry_status(rows: list[dict], today: date) -> list[dict]:
    for item in rows:
        try:
            alert_days = int(float(item.get("expiry_alert_days") or 60))
        except (TypeError, ValueError):
            alert_days = 60
        days_left = days_until(item.get("expiry_date"), today)
        item["expiry_alert_days"] = alert_days
        item["days_left"] = days_left
        item["expiry_alert"] = 0
        item["expiry_status"] = "ok"
        item["expiry_status_label"] = "正常"
        if days_left is None:
            item["expiry_status"] = ""
            item["expiry_status_label"] = ""
        elif days_left < 0:
            item["expiry_alert"] = 1
            item["expiry_status"] = "bad"
            item["expiry_status_label"] = f"已过期 {abs(days_left)} 天"
        elif days_left <= alert_days:
            item["expiry_alert"] = 1
            item["expiry_status"] = "warn"
            item["expiry_status_label"] = f"剩余 {days_left} 天"
    return rows


def enrich_stock_status(rows: list[dict]) -> list[dict]:
    for item in rows:
        available = float(item.get("available") or 0)
        min_qty = float(item.get("min_qty") or 0)
        safety_qty = float(item.get("safety_qty") or min_qty)
        if safety_qty < min_qty:
            safety_qty = min_qty
            item["safety_qty"] = safety_qty
        reorder_qty = max(safety_qty - available, 0)
        item["reorder_qty"] = round(reorder_qty, 3)
        item["stock_status"] = "ok"
        item["stock_status_label"] = "正常"
        if min_qty > 0 and available <= 0:
            item["stock_status"] = "red"
            item["stock_status_label"] = "红色：缺货"
        elif min_qty > 0 and available < min_qty:
            item["stock_status"] = "red"
            item["stock_status_label"] = "红色：低于最低库存"
        elif safety_qty > 0 and available < safety_qty:
            item["stock_status"] = "yellow"
            item["stock_status_label"] = "黄色：低于安全库存"
    return rows


def location_model(conn: sqlite3.Connection) -> list[dict]:
    rows = fetch_all(
        conn,
        """
        SELECT
            l.id,
            l.area,
            l.zone,
            l.type,
            l.priority,
            l.capacity,
            ROUND(COALESCE(SUM(CASE WHEN s.qty > 0 THEN s.qty ELSE 0 END), 3), 3) AS occupied_qty,
            COUNT(CASE WHEN s.qty > 0 THEN 1 END) AS pallet_count,
            COUNT(CASE WHEN s.qty > 0 AND s.quality_status = '暂扣' THEN 1 END) AS hold_count,
            COUNT(CASE WHEN s.qty > 0 AND s.quality_status IN ('冻结', '隔离', '待检') THEN 1 END) AS blocked_count,
            MAX(cs.ts) AS last_camera_scan
        FROM locations l
        LEFT JOIN stock_units s ON s.location_id = l.id AND s.qty > 0
        LEFT JOIN camera_scans cs ON cs.location_id = l.id
        GROUP BY l.id
        ORDER BY l.priority, l.id
        """,
    )
    for row in rows:
        capacity = float(row.get("capacity") or 0)
        occupied = float(row.get("occupied_qty") or 0)
        row["available_capacity"] = round(max(0.0, capacity - occupied), 3) if capacity > 0 else 0
        row["occupancy_pct"] = round(min(100.0, occupied / capacity * 100), 1) if capacity > 0 else 0
        if row["blocked_count"]:
            row["model_status"] = "需复核"
        elif row["hold_count"]:
            row["model_status"] = "暂扣"
        elif row["occupancy_pct"] >= 90:
            row["model_status"] = "高占用"
        elif row["occupancy_pct"] <= 20:
            row["model_status"] = "空闲"
        else:
            row["model_status"] = "正常"
    return rows


def preferred_areas(category: str, quality_status: str) -> set[str]:
    quality_status = quality_status.strip()
    if quality_status in {"待检", "暂扣", "隔离", "冻结"}:
        return {"质量区", "包材仓" if category == "包材" else "原料仓"}
    if category == "成品":
        return {"成品仓"}
    if category == "包材":
        return {"包材仓"}
    if category == "返工料":
        return {"红蓝通道", "原料仓"}
    return {"原料仓", "红蓝通道"}


def recommend_locations(conn: sqlite3.Connection, data: dict) -> list[dict]:
    goods_id = require_text(data, "goods_id")
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (goods_id,))
    if not product:
        raise ValueError("货品不存在")
    qty = positive_number(data.get("qty") or 1, "数量")
    quality_status = str(data.get("quality_status") or "合格").strip()
    areas = preferred_areas(str(product["category"]), quality_status)
    rows = fetch_all(
        conn,
        """
        SELECT
            l.id,
            l.area,
            l.zone,
            l.type,
            l.priority,
            l.capacity,
            ROUND(COALESCE(SUM(CASE WHEN s.qty > 0 THEN s.qty ELSE 0 END), 0), 3) AS occupied_qty,
            ROUND(COALESCE(SUM(CASE WHEN s.goods_id = ? AND s.qty > 0 THEN s.qty ELSE 0 END), 0), 3) AS same_goods_qty,
            COUNT(CASE WHEN s.qty > 0 THEN 1 END) AS pallet_count
        FROM locations l
        LEFT JOIN stock_units s ON s.location_id = l.id
        GROUP BY l.id
        ORDER BY l.priority, l.id
        """,
        (goods_id,),
    )
    recommendations = []
    for row in rows:
        capacity = float(row["capacity"] or 0)
        occupied = float(row["occupied_qty"] or 0)
        available = capacity - occupied if capacity > 0 else qty
        occupancy_pct = occupied / capacity * 100 if capacity > 0 else 0
        is_quality_location = row["area"] == "质量区" or row["type"] in {"冻结货位", "暂扣货位"}
        score = 100 - int(row["priority"]) * 4
        reasons = []
        if row["area"] in areas:
            score += 36
            reasons.append("仓别匹配")
        if quality_status in {"待检", "暂扣", "隔离", "冻结"} and is_quality_location:
            score += 60
            reasons.append("质量状态匹配")
        if quality_status == "合格" and is_quality_location:
            score -= 45
            reasons.append("非合格常规库位")
        if available >= qty or capacity <= 0:
            score += 25
            reasons.append("容量满足")
        else:
            score -= 60
            reasons.append("容量不足")
        if float(row["same_goods_qty"] or 0) > 0:
            score += 15
            reasons.append("同品邻近")
        if occupancy_pct < 80:
            score += 8
            reasons.append("占用可控")
        if str(product["category"]) == "液体原料" and "液体" not in row["zone"] and row["area"] != "质量区":
            score -= 10
        item = dict(row)
        item["score"] = round(score, 1)
        item["available_capacity"] = round(max(0.0, available), 3) if capacity > 0 else 0
        item["occupancy_pct"] = round(min(100.0, occupancy_pct), 1)
        item["recommended"] = score >= 80
        item["reason"] = "、".join(reasons) if reasons else "按优先级候选"
        item["goods_id"] = goods_id
        item["goods_name"] = product["name"]
        item["requested_qty"] = qty
        item["quality_status"] = quality_status
        recommendations.append(item)
    recommendations.sort(key=lambda item: (-item["score"], int(item["priority"]), item["id"]))
    return recommendations[:8]


def parse_scan_code(conn: sqlite3.Connection, data: dict) -> dict:
    code = require_text(data, "code")
    scan_type = str(data.get("scan_type") or "RF/QR").strip()
    action = str(data.get("action") or "查询").strip()
    operator = str(data.get("_operator") or "").strip()
    normalized = code.strip()
    tokens = {}
    for part in re.split(r"[;|,\n]+", normalized):
        if "=" in part:
            key, value = part.split("=", 1)
            tokens[key.strip().upper()] = value.strip()
    lookup_code = tokens.get("SSCC") or tokens.get("LOC") or tokens.get("LOCATION") or tokens.get("GOODS") or normalized
    stock = fetch_one(
        conn,
        """
        SELECT s.*, p.name AS goods_name, p.category, l.area, l.zone
        FROM stock_units s
        JOIN products p ON p.id = s.goods_id
        JOIN locations l ON l.id = s.location_id
        WHERE s.sscc = ?
        """,
        (lookup_code,),
    )
    location = fetch_one(conn, "SELECT * FROM locations WHERE id = ?", (lookup_code,))
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (lookup_code,))
    parsed_type = "UNKNOWN"
    ref_id = None
    location_id = None
    goods_id = None
    detail = {}
    if stock:
        parsed_type = "SSCC"
        ref_id = stock["sscc"]
        location_id = stock["location_id"]
        goods_id = stock["goods_id"]
        detail = dict(stock)
    elif location:
        parsed_type = "LOCATION"
        ref_id = location["id"]
        location_id = location["id"]
        detail = dict(location)
    elif product:
        parsed_type = "GOODS"
        ref_id = product["id"]
        goods_id = product["id"]
        detail = dict(product)
    scan_id = new_id("SCN")
    result = "已识别" if parsed_type != "UNKNOWN" else "未匹配"
    payload = {
        "raw": normalized,
        "tokens": tokens,
        "detail": detail,
    }
    conn.execute(
        """
        INSERT INTO scan_events(id, ts, scan_type, code, parsed_type, ref_id, location_id, goods_id, action, result, operator, payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan_id,
            now_text(),
            scan_type,
            normalized,
            parsed_type,
            ref_id,
            location_id,
            goods_id,
            action,
            result,
            operator,
            scrub_payload(payload),
        ),
    )
    return {
        "id": scan_id,
        "scan_type": scan_type,
        "code": normalized,
        "parsed_type": parsed_type,
        "ref_id": ref_id,
        "location_id": location_id,
        "goods_id": goods_id,
        "action": action,
        "result": result,
        "detail": detail,
    }


def record_camera_scan(conn: sqlite3.Connection, data: dict) -> str:
    location_id = str(data.get("location_id") or "").strip()
    if location_id and not fetch_one(conn, "SELECT id FROM locations WHERE id = ?", (location_id,)):
        raise ValueError("库位不存在")
    camera_name = str(data.get("camera_name") or "在线摄像头").strip()
    image_note = str(data.get("image_note") or "").strip()
    operator = str(data.get("_operator") or "").strip()
    scan_id = new_id("CAM")
    confidence = float(data.get("confidence") or 0.86)
    payload = {
        "capture_mode": str(data.get("capture_mode") or "browser"),
        "source": str(data.get("source") or "camera"),
    }
    conn.execute(
        """
        INSERT INTO camera_scans(id, ts, location_id, camera_name, model_status, confidence, image_note, operator, payload)
        VALUES (?, ?, ?, ?, '已采集', ?, ?, ?, ?)
        """,
        (scan_id, now_text(), location_id or None, camera_name, confidence, image_note, operator, scrub_payload(payload)),
    )
    log_ledger(conn, "库位建模采集", scan_id, None, None, location_id or None, 1, None, None, image_note or camera_name)
    return scan_id


def generate_label(conn: sqlite3.Connection, data: dict) -> dict:
    goods_id = require_text(data, "goods_id")
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (goods_id,))
    if not product:
        raise ValueError("货品不存在")
    category = str(product["category"])
    label_type = str(data.get("label_type") or ("产品标签" if category == "成品" else "原料标签")).strip()
    if label_type not in {"原料标签", "产品标签"}:
        raise ValueError("标签类型必须是原料标签或产品标签")
    batch_no = require_text(data, "batch_no")
    supplier_batch = str(data.get("supplier_batch") or "").strip()
    production_date = str(data.get("production_date") or "").strip()
    expiry_date = str(data.get("expiry_date") or "").strip()
    location_id = str(data.get("location_id") or "").strip()
    if location_id and not fetch_one(conn, "SELECT id FROM locations WHERE id = ?", (location_id,)):
        raise ValueError("库位不存在")
    sscc = str(data.get("sscc") or "").strip()
    qty_value = data.get("qty")
    qty = positive_number(qty_value, "数量") if qty_value not in (None, "") else None
    quality_status = str(data.get("quality_status") or "合格").strip()
    code_type = str(data.get("code_type") or "条码+二维码").strip()
    if code_type not in {"条码", "二维码", "条码+二维码"}:
        raise ValueError("码制必须是条码、二维码或条码+二维码")
    copies_raw = data.get("copies") or 1
    try:
        copies = max(1, min(99, int(float(copies_raw))))
    except (TypeError, ValueError):
        raise ValueError("打印份数必须是数字") from None
    template_name = "原料批次标签 v1" if label_type == "原料标签" else "产品成品标签 v1"
    label_id = new_id("LBL")
    operator = str(data.get("_operator") or "").strip()
    barcode_value = sscc or f"{goods_id}-{batch_no}"
    qr_fields = {
        "TYPE": "RAW" if label_type == "原料标签" else "FG",
        "GOODS": goods_id,
        "BATCH": batch_no,
        "SSCC": sscc,
        "QTY": "" if qty is None else str(qty),
        "UNIT": product["unit"],
        "BBD": expiry_date,
        "LOC": location_id,
    }
    qr_value = "WMS|" + "|".join(f"{key}={value}" for key, value in qr_fields.items() if value)
    label = {
        "id": label_id,
        "ts": now_text(),
        "label_type": label_type,
        "template_name": template_name,
        "goods_id": goods_id,
        "goods_name": product["name"],
        "category": category,
        "batch_no": batch_no,
        "supplier_batch": supplier_batch,
        "production_date": production_date,
        "expiry_date": expiry_date,
        "qty": qty,
        "unit": product["unit"],
        "location_id": location_id,
        "sscc": sscc,
        "quality_status": quality_status,
        "code_type": code_type,
        "barcode_value": barcode_value,
        "qr_value": qr_value,
        "copies": copies,
        "operator": operator,
    }
    conn.execute(
        """
        INSERT INTO label_prints(
            id, ts, label_type, template_name, goods_id, goods_name, category, batch_no, supplier_batch,
            production_date, expiry_date, qty, unit, location_id, sscc, quality_status, code_type,
            barcode_value, qr_value, copies, operator, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            label["id"], label["ts"], label_type, template_name, goods_id, product["name"], category, batch_no, supplier_batch,
            production_date, expiry_date, qty, product["unit"], location_id, sscc, quality_status, code_type,
            barcode_value, qr_value, copies, operator, scrub_payload(label),
        ),
    )
    return label


def bootstrap_payload(conn: sqlite3.Connection, user: dict | None = None) -> dict:
    inventory = fetch_all(
        conn,
        """
        SELECT
            s.*,
            ROUND(s.qty - s.reserved_qty, 3) AS available_qty,
            p.name AS goods_name,
            p.category,
            p.min_qty,
            p.safety_qty,
            p.expiry_alert_days,
            p.courbon,
            l.area,
            l.zone,
            l.type AS location_type,
            l.priority AS location_priority
        FROM stock_units s
        JOIN products p ON p.id = s.goods_id
        JOIN locations l ON l.id = s.location_id
        WHERE s.qty > 0
        ORDER BY l.priority, date(NULLIF(s.expiry_date, '')), s.sscc
        """,
    )
    outbounds = fetch_all(
        conn,
        """
        SELECT o.*, p.name AS goods_name, p.unit, p.category
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        ORDER BY o.created_at DESC
        LIMIT 60
        """,
    )
    outbound_lines = fetch_all(
        conn,
        """
        SELECT l.*, p.name AS goods_name
        FROM outbound_lines l
        JOIN stock_units s ON s.sscc = l.sscc
        JOIN products p ON p.id = s.goods_id
        ORDER BY l.id ASC
        LIMIT 120
        """,
    )
    for outbound in outbounds:
        outbound["lines"] = [line for line in outbound_lines if line["outbound_id"] == outbound["id"]]

    today = date.today()
    enrich_expiry_status(inventory, today)
    active_stock = [item for item in inventory if item["quality_status"] != "已出库"]
    expiry_warnings = [item for item in active_stock if item.get("expiry_alert")]

    product_summary = fetch_all(
        conn,
        """
        SELECT
            p.id,
            p.name,
            p.category,
            p.unit,
            p.min_qty,
            p.safety_qty,
            p.expiry_alert_days,
            p.courbon,
            ROUND(COALESCE(SUM(s.qty), 0), 3) AS on_hand,
            ROUND(COALESCE(SUM(s.reserved_qty), 0), 3) AS reserved,
            ROUND(COALESCE(SUM(s.qty - s.reserved_qty), 0), 3) AS available
        FROM products p
        LEFT JOIN stock_units s ON s.goods_id = p.id AND s.qty > 0 AND s.quality_status = '合格'
        GROUP BY p.id
        ORDER BY p.category, p.id
        """,
    )
    enrich_stock_status(product_summary)
    stock_warnings = [item for item in product_summary if item["stock_status"] != "ok"]
    finished_inventory = [item for item in inventory if item["category"] == "成品"]
    finished_summary = [item for item in product_summary if item["category"] == "成品"]
    finished_low_stock = [item for item in finished_summary if item["stock_status"] != "ok"]
    finished_expiry_warnings = [item for item in finished_inventory if item.get("expiry_alert")]
    packaging_inventory = [item for item in inventory if item["category"] == "包材"]
    packaging_summary = [item for item in product_summary if item["category"] == "包材"]
    packaging_low_stock = [item for item in packaging_summary if item["stock_status"] != "ok"]
    packaging_expiry_warnings = [item for item in packaging_inventory if item.get("expiry_alert")]
    packaging_hold_count = sum(1 for item in packaging_inventory if item["quality_status"] == "暂扣")
    finished_outbound_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        WHERE p.category = '成品' AND o.status IN ('已分配', '欠品', '效期不足')
        """
    ).fetchone()[0]
    packaging_outbound_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        WHERE p.category = '包材' AND o.status IN ('已分配', '欠品')
        """
    ).fetchone()[0]
    spare_parts = spare_parts_with_status(conn)
    spare_transactions = fetch_all(
        conn,
        """
        SELECT t.*, p.name AS part_name, p.spec, p.category, p.abc_class, p.unit, p.critical, p.food_contact
        FROM spare_transactions t
        JOIN spare_parts p ON p.id = t.part_id
        ORDER BY t.ts DESC, t.id DESC
        LIMIT 120
        """,
    )
    spare_warnings = [part for part in spare_parts if part["stock_status"] != "ok"]
    spare_stock_value = round(sum(float(part["stock_value"]) for part in spare_parts), 2)
    spare_issue_amount = round(sum(float(item["amount"]) for item in spare_transactions if item["action"] == "备件领用"), 2)
    inbounds = fetch_all(
        conn,
        """
        SELECT i.*, p.name AS goods_name, p.unit, p.category
        FROM inbound_orders i
        JOIN products p ON p.id = i.goods_id
        ORDER BY i.created_at DESC
        LIMIT 60
        """,
    )
    operation_logs = []
    if user and "logs" in role_permissions(user["role"]):
        operation_logs = fetch_all(conn, "SELECT * FROM operation_logs ORDER BY id DESC LIMIT 200")
    model_rows = location_model(conn)
    scan_events = fetch_all(conn, "SELECT * FROM scan_events ORDER BY ts DESC LIMIT 80")
    camera_scans = fetch_all(conn, "SELECT * FROM camera_scans ORDER BY ts DESC LIMIT 60")
    label_prints = fetch_all(conn, "SELECT * FROM label_prints ORDER BY ts DESC LIMIT 80")
    finished_waves = finished_waves_payload(conn)
    tms = tms_payload(conn)
    smart_alerts = build_smart_alerts(stock_warnings, expiry_warnings, outbounds, inventory, fetch_all(conn, "SELECT * FROM counts ORDER BY created_at DESC LIMIT 60"), finished_waves)
    safety_recommendations = dynamic_safety_recommendations(conn, product_summary)
    wave_suggestions = smart_wave_suggestions(conn)

    return {
        "auth": {
            "user": public_user(user) if user else None,
            "roles": ROLE_LABELS,
            "permissions": ROLE_PERMISSIONS,
        },
        "source_analysis": SOURCE_ANALYSIS,
        "stats": {
            "sku_count": len(product_summary),
            "pallet_count": len(active_stock),
            "on_hand_qty": round(sum(float(item["qty"]) for item in active_stock), 3),
            "reserved_qty": round(sum(float(item["reserved_qty"]) for item in active_stock), 3),
            "stock_warning_count": len(stock_warnings),
            "stock_red_count": sum(1 for item in stock_warnings if item["stock_status"] == "red"),
            "expiring_count": len(expiry_warnings),
            "expired_count": sum(1 for item in expiry_warnings if item["days_left"] is not None and item["days_left"] < 0),
            "shortage_count": conn.execute("SELECT COUNT(*) FROM outbound_orders WHERE status IN ('欠品', '效期不足')").fetchone()[0],
            "open_outbound_count": conn.execute("SELECT COUNT(*) FROM outbound_orders WHERE status IN ('已分配', '欠品', '效期不足')").fetchone()[0],
            "finished_sku_count": len(finished_summary),
            "finished_pallet_count": len(finished_inventory),
            "finished_on_hand_qty": round(sum(float(item["qty"]) for item in finished_inventory), 3),
            "finished_reserved_qty": round(sum(float(item["reserved_qty"]) for item in finished_inventory), 3),
            "finished_stock_warning_count": len(finished_low_stock),
            "finished_expiring_count": len(finished_expiry_warnings),
            "finished_shipping_count": finished_outbound_count,
            "finished_wave_count": len(finished_waves),
            "finished_active_wave_count": sum(1 for wave in finished_waves if wave["status"] != "已完成"),
            "packaging_sku_count": len(packaging_summary),
            "packaging_pallet_count": len(packaging_inventory),
            "packaging_on_hand_qty": round(sum(float(item["qty"]) for item in packaging_inventory), 3),
            "packaging_reserved_qty": round(sum(float(item["reserved_qty"]) for item in packaging_inventory), 3),
            "packaging_stock_warning_count": len(packaging_low_stock),
            "packaging_hold_count": packaging_hold_count,
            "packaging_issue_count": packaging_outbound_count,
            "packaging_expiring_count": len(packaging_expiry_warnings),
            "spare_sku_count": len(spare_parts),
            "spare_stock_value": spare_stock_value,
            "spare_warning_count": len(spare_warnings),
            "spare_critical_shortage_count": sum(1 for part in spare_warnings if part["stock_status"] == "red"),
            "spare_food_contact_count": sum(1 for part in spare_parts if part["food_contact"]),
            "spare_issue_amount": spare_issue_amount,
            "rf_scan_count": len(scan_events),
            "camera_scan_count": len(camera_scans),
            "modeled_location_count": sum(1 for item in model_rows if item.get("last_camera_scan")),
            "label_print_count": len(label_prints),
            "smart_risk_count": len(smart_alerts),
            "smart_high_risk_count": sum(1 for item in smart_alerts if item["severity"] == "高"),
            "smart_wave_suggestion_count": len(wave_suggestions),
            "smart_safety_adjust_count": sum(1 for item in safety_recommendations if item["action"] != "保持"),
            "tms_shipment_count": len(tms["shipments"]),
            "tms_active_count": sum(1 for item in tms["shipments"] if item["status"] in {"待发车", "已发车", "在途", "到达"}),
            "tms_exception_count": sum(1 for item in tms["shipments"] if item["exception_flag"]),
            "tms_pending_pod_count": sum(1 for item in tms["shipments"] if item["status"] in {"已发车", "在途", "到达"}),
            "tms_recall_count": len(tms["recalls"]),
            "tms_freight_bill_count": len(tms["freight_bills"]),
            "tms_freight_diff_count": sum(1 for item in tms["freight_bills"] if item["billing_status"] == "差异"),
            "channel_expiry_rule_count": len(tms["channel_rules"]),
            "tms_iot_high_risk_count": tms["control_tower"]["high_risk_telemetry"],
            "tms_pending_driver_count": tms["control_tower"]["pending_driver_tasks"],
            "integration_pending_count": tms["control_tower"]["pending_integrations"],
            "audit_package_count": len(tms["audit_packages"]),
        },
        "products": fetch_all(conn, "SELECT * FROM products ORDER BY category, id"),
        "locations": fetch_all(conn, "SELECT * FROM locations ORDER BY priority, id"),
        "inventory": inventory,
        "product_summary": product_summary,
        "low_stock": stock_warnings,
        "stock_warnings": stock_warnings,
        "expiry_warnings": expiry_warnings,
        "inbounds": inbounds,
        "outbounds": outbounds,
        "moves": fetch_all(conn, "SELECT * FROM moves ORDER BY created_at DESC LIMIT 60"),
        "counts": fetch_all(conn, "SELECT * FROM counts ORDER BY created_at DESC LIMIT 60"),
        "ledger": fetch_all(conn, "SELECT * FROM ledger ORDER BY id DESC LIMIT 100"),
        "operation_logs": operation_logs,
        "recent_scans": scan_events,
        "camera_scans": camera_scans,
        "location_model": model_rows,
        "scan_result": None,
        "location_recommendations": [],
        "current_label": None,
        "label_prints": label_prints,
        "finished": {
            "inventory": finished_inventory,
            "summary": finished_summary,
            "low_stock": finished_low_stock,
            "expiry_warnings": finished_expiry_warnings,
            "inbounds": [item for item in inbounds if item["category"] == "成品"],
            "outbounds": [item for item in outbounds if item["category"] == "成品"],
            "waves": finished_waves,
        },
        "packaging": {
            "inventory": packaging_inventory,
            "summary": packaging_summary,
            "low_stock": packaging_low_stock,
            "expiry_warnings": packaging_expiry_warnings,
            "inbounds": [item for item in inbounds if item["category"] == "包材"],
            "outbounds": [item for item in outbounds if item["category"] == "包材"],
        },
        "spares": {
            "parts": spare_parts,
            "warnings": spare_warnings,
            "transactions": spare_transactions,
        },
        "tms": tms,
        "smart": {
            "alerts": smart_alerts,
            "wave_suggestions": wave_suggestions,
            "safety_recommendations": safety_recommendations,
        },
    }


def create_inbound(conn: sqlite3.Connection, data: dict) -> str:
    goods_id = require_text(data, "goods_id")
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (goods_id,))
    if not product:
        raise ValueError("货品不存在")
    location_id = require_text(data, "location_id")
    if not fetch_one(conn, "SELECT * FROM locations WHERE id = ?", (location_id,)):
        raise ValueError("库位不存在")

    qty = positive_number(data.get("qty"), "入库数量")
    sscc = str(data.get("sscc") or f"SSCC{datetime.now().strftime('%Y%m%d%H%M%S%f')[-16:]}").strip()
    if fetch_one(conn, "SELECT sscc FROM stock_units WHERE sscc = ?", (sscc,)):
        raise ValueError("SSCC 已存在")

    inbound_id = new_id("IN")
    created_at = now_text()
    quality = str(data.get("quality_status") or "合格").strip()
    owner = str(data.get("owner") or "MARS-RMR").strip()
    supplier = str(data.get("supplier") or "现场收货").strip()
    supplier_batch = str(data.get("supplier_batch") or "").strip()
    production_date = str(data.get("production_date") or "").strip()
    expiry_date = str(data.get("expiry_date") or "").strip()
    po_no = str(data.get("po_no") or "").strip()
    remark = str(data.get("remark") or "").strip()
    ledger_action = str(data.get("_ledger_action") or "入库上架")
    operator = str(data.get("_operator") or "").strip()

    conn.execute(
        """
        INSERT INTO inbound_orders(
            id, goods_id, qty, received_qty, status, supplier, supplier_batch,
            production_date, expiry_date, location_id, sscc, created_at, remark
        ) VALUES (?, ?, ?, ?, '已上架', ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (inbound_id, goods_id, qty, qty, supplier, supplier_batch, production_date, expiry_date, location_id, sscc, created_at, remark),
    )
    conn.execute(
        """
        INSERT INTO stock_units(
            sscc, goods_id, owner, location_id, qty, reserved_qty, unit,
            production_date, expiry_date, supplier_batch, po_no, quality_status, updated_at
        ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
        """,
        (sscc, goods_id, owner, location_id, qty, product["unit"], production_date, expiry_date, supplier_batch, po_no, quality, created_at),
    )
    note = remark or supplier
    if operator:
        note = f"{note}；操作人：{operator}"
    log_ledger(conn, ledger_action, inbound_id, sscc, goods_id, location_id, qty, 0, qty, note)
    return inbound_id


def create_outbound(conn: sqlite3.Connection, data: dict) -> str:
    goods_id = require_text(data, "goods_id")
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (goods_id,))
    if not product:
        raise ValueError("货品不存在")
    qty = positive_number(data.get("qty"), "出库数量")
    destination = require_text(data, "destination")
    channel_code = str(data.get("channel_code") or data.get("channel") or "").strip().upper()
    min_remaining_days = nonnegative_int(data.get("min_remaining_days"), 0)
    rule = channel_expiry_rule(conn, goods_id, channel_code)
    if rule:
        min_remaining_days = max(min_remaining_days, int(rule["min_remaining_days"] or 0))
    bin_no = str(data.get("bin_no") or "").strip()
    remark = str(data.get("remark") or "").strip()
    courbon_connected = 1 if data.get("courbon_connected", True) else 0
    ledger_action = str(data.get("_ledger_action") or "出库分配")
    operator = str(data.get("_operator") or "").strip()

    rows = fetch_all(
        conn,
        """
        SELECT s.*, l.priority
        FROM stock_units s
        JOIN locations l ON l.id = s.location_id
        WHERE s.goods_id = ?
          AND s.quality_status = '合格'
          AND s.qty - s.reserved_qty > 0
        ORDER BY l.priority, date(NULLIF(s.expiry_date, '')), s.sscc
        """,
        (goods_id,),
    )
    blocked_by_expiry_qty = 0.0
    if min_remaining_days > 0:
        eligible_rows = []
        for row in rows:
            available = float(row["qty"]) - float(row["reserved_qty"])
            if available <= 0:
                continue
            if stock_meets_remaining_days(row["expiry_date"], min_remaining_days):
                eligible_rows.append(row)
            else:
                blocked_by_expiry_qty += available
        rows = eligible_rows
    outbound_id = new_id("OUT")
    needed = qty
    allocated = 0.0
    created_at = now_text()
    conn.execute(
        """
        INSERT INTO outbound_orders(
            id, goods_id, qty, allocated_qty, shortage_qty, status, destination,
            channel_code, min_remaining_days, bin_no, courbon_connected, created_at, confirmed_at, remark
        ) VALUES (?, ?, ?, 0, ?, '分配中', ?, ?, ?, ?, ?, ?, NULL, ?)
        """,
        (outbound_id, goods_id, qty, qty, destination, channel_code or None, min_remaining_days, bin_no, courbon_connected, created_at, remark),
    )

    for row in rows:
        if needed <= 0:
            break
        available = float(row["qty"]) - float(row["reserved_qty"])
        pick_qty = min(available, needed)
        if pick_qty <= 0:
            continue
        conn.execute(
            "UPDATE stock_units SET reserved_qty = reserved_qty + ?, updated_at = ? WHERE sscc = ?",
            (pick_qty, created_at, row["sscc"]),
        )
        conn.execute(
            """
            INSERT INTO outbound_lines(outbound_id, sscc, location_id, qty, status)
            VALUES (?, ?, ?, ?, '已分配')
            """,
            (outbound_id, row["sscc"], row["location_id"], pick_qty),
        )
        allocated += pick_qty
        needed -= pick_qty
        log_ledger(
            conn,
            ledger_action,
            outbound_id,
            row["sscc"],
            goods_id,
            row["location_id"],
            pick_qty,
            row["qty"],
            row["qty"],
            f"按近效期和优先货位分配；渠道 {channel_code or '-'}；最小剩余效期 {min_remaining_days} 天；操作人：{operator}" if operator else f"按近效期和优先货位分配；渠道 {channel_code or '-'}；最小剩余效期 {min_remaining_days} 天",
        )

    shortage = max(0.0, needed)
    if shortage == 0:
        status = "已分配"
    elif min_remaining_days > 0 and blocked_by_expiry_qty > 0:
        status = "效期不足"
    else:
        status = "欠品"
    conn.execute(
        """
        UPDATE outbound_orders
        SET allocated_qty = ?, shortage_qty = ?, status = ?
        WHERE id = ?
        """,
        (allocated, shortage, status, outbound_id),
    )
    return outbound_id


def create_finished_receipt(conn: sqlite3.Connection, data: dict) -> str:
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (require_text(data, "goods_id"),))
    if not product or product["category"] != "成品":
        raise ValueError("请选择成品货品")
    payload = dict(data)
    payload.setdefault("supplier", data.get("production_line") or "包装完工")
    payload.setdefault("owner", "MARS-FG")
    payload.setdefault("location_id", "FG-A01-01")
    payload.setdefault("quality_status", "合格")
    payload.setdefault("remark", "成品完工入库，外箱、码垛、标签已核对")
    payload["_ledger_action"] = "成品完工入库"
    return create_inbound(conn, payload)


def create_finished_shipment(conn: sqlite3.Connection, data: dict) -> str:
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (require_text(data, "goods_id"),))
    if not product or product["category"] != "成品":
        raise ValueError("请选择成品货品")
    customer = require_text(data, "customer")
    order_no = str(data.get("order_no") or "").strip()
    channel_code = str(data.get("channel_code") or data.get("channel") or "ECOM").strip().upper()
    payload = dict(data)
    payload["destination"] = f"客户发运：{customer}"
    payload["channel_code"] = channel_code
    payload.setdefault("bin_no", data.get("ship_dock") or "DOCK-01")
    payload["courbon_connected"] = False
    payload.setdefault(
        "remark",
        f"销售订单 {order_no}，渠道 {channel_code}，成品客户订单发运，按渠道剩余效期、BBD 和库位优先级分配" if order_no else f"渠道 {channel_code}，成品客户订单发运，按渠道剩余效期、BBD 和库位优先级分配",
    )
    payload["_ledger_action"] = "成品发运分配"
    return create_outbound(conn, payload)


def create_packaging_receipt(conn: sqlite3.Connection, data: dict) -> str:
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (require_text(data, "goods_id"),))
    if not product or product["category"] != "包材":
        raise ValueError("请选择包材货品")
    payload = dict(data)
    payload.setdefault("supplier", "包材收货")
    payload.setdefault("owner", "MARS-PKG")
    payload.setdefault("location_id", "PK-B01-01")
    payload.setdefault("quality_status", "合格")
    payload.setdefault("remark", "包材入库，外观、印刷、条码和数量已核对")
    payload["_ledger_action"] = "包材入库"
    return create_inbound(conn, payload)


def create_packaging_issue(conn: sqlite3.Connection, data: dict) -> str:
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (require_text(data, "goods_id"),))
    if not product or product["category"] != "包材":
        raise ValueError("请选择包材货品")
    payload = dict(data)
    payload["destination"] = str(payload.get("destination") or "包装线领用").strip()
    payload.setdefault("bin_no", "PK-LINE-01")
    payload["courbon_connected"] = False
    payload.setdefault("remark", "包材领用，暂扣/待检库存不可分配")
    payload["_ledger_action"] = "包材领用分配"
    return create_outbound(conn, payload)


def confirm_outbound(conn: sqlite3.Connection, outbound_id: str, operator: str = "") -> None:
    order = fetch_one(conn, "SELECT * FROM outbound_orders WHERE id = ?", (outbound_id,))
    if not order:
        raise ValueError("出库单不存在")
    if order["status"] == "已完成":
        raise ValueError("出库单已完成")
    if float(order["shortage_qty"]) > 0:
        if order["status"] == "效期不足":
            raise ValueError("出库单仍有效期不足，不能确认")
        raise ValueError("出库单仍有欠品，不能确认")

    lines = fetch_all(conn, "SELECT * FROM outbound_lines WHERE outbound_id = ?", (outbound_id,))
    if not lines:
        raise ValueError("没有可确认的分配明细")

    product = fetch_one(conn, "SELECT category FROM products WHERE id = ?", (order["goods_id"],))
    if product and product["category"] == "成品":
        confirm_action = "成品发运确认"
    elif product and product["category"] == "包材":
        confirm_action = "包材领用确认"
    else:
        confirm_action = "出库确认"
    confirmed_at = now_text()
    for line in lines:
        stock = fetch_one(conn, "SELECT * FROM stock_units WHERE sscc = ?", (line["sscc"],))
        if not stock:
            raise ValueError(f"{line['sscc']} 库存不存在")
        before_qty = float(stock["qty"])
        line_qty = float(line["qty"])
        after_qty = before_qty - line_qty
        if after_qty < -0.0001:
            raise ValueError(f"{line['sscc']} 库存不足")
        new_reserved = max(0.0, float(stock["reserved_qty"]) - line_qty)
        new_status = "已出库" if after_qty <= 0.0001 else stock["quality_status"]
        conn.execute(
            """
            UPDATE stock_units
            SET qty = ?, reserved_qty = ?, quality_status = ?, updated_at = ?
            WHERE sscc = ?
            """,
            (max(0.0, after_qty), new_reserved, new_status, confirmed_at, line["sscc"]),
        )
        conn.execute("UPDATE outbound_lines SET status = '已确认' WHERE id = ?", (line["id"],))
        log_ledger(
            conn,
            confirm_action,
            outbound_id,
            line["sscc"],
            order["goods_id"],
            line["location_id"],
            line_qty,
            before_qty,
            max(0.0, after_qty),
            f"{order['destination']}；操作人：{operator}" if operator else order["destination"],
        )

    conn.execute(
        "UPDATE outbound_orders SET status = '已完成', confirmed_at = ? WHERE id = ?",
        (confirmed_at, outbound_id),
    )


def parse_id_list(value: object) -> list[str]:
    if isinstance(value, list):
        parts = value
    else:
        parts = re.split(r"[\s,，;；]+", str(value or ""))
    seen = set()
    result = []
    for part in parts:
        item = str(part or "").strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def create_finished_wave(conn: sqlite3.Connection, data: dict) -> str:
    order_ids = parse_id_list(data.get("order_ids"))
    operator = str(data.get("_operator") or "").strip()
    params: list[object] = []
    where = [
        "p.category = '成品'",
        "o.status = '已分配'",
        "o.shortage_qty = 0",
        """
        NOT EXISTS (
            SELECT 1
            FROM finished_wave_orders wo
            WHERE wo.outbound_id = o.id
              AND wo.status NOT IN ('已发货', '取消')
        )
        """,
    ]
    if order_ids:
        where.append(f"o.id IN ({','.join('?' for _ in order_ids)})")
        params.extend(order_ids)
    orders = fetch_all(
        conn,
        f"""
        SELECT o.*, p.name AS goods_name, p.unit
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        WHERE {' AND '.join(where)}
        ORDER BY o.bin_no, o.created_at, o.id
        """,
        tuple(params),
    )
    if not orders:
        raise ValueError("没有可创建波次的成品发货单")
    if order_ids and len(orders) != len(order_ids):
        found = {order["id"] for order in orders}
        missing = [item for item in order_ids if item not in found]
        raise ValueError(f"以下发货单不可加入波次：{', '.join(missing)}")

    wave_id = new_id("WV")
    created_at = now_text()
    dock = str(data.get("dock") or data.get("ship_dock") or "").strip()
    route = str(data.get("route") or "").strip()
    ship_date = str(data.get("ship_date") or date.today().isoformat()).strip()
    remark = str(data.get("remark") or "").strip()
    conn.execute(
        """
        INSERT INTO finished_waves(id, status, ship_date, dock, route, created_at, created_by, remark)
        VALUES (?, '已创建', ?, ?, ?, ?, ?, ?)
        """,
        (wave_id, ship_date, dock, route, created_at, operator, remark),
    )
    for index, order in enumerate(orders, start=1):
        staging_location = str(data.get("staging_location") or f"STAGE-{index:02d}").strip()
        conn.execute(
            """
            INSERT INTO finished_wave_orders(wave_id, outbound_id, status, staging_location, remark)
            VALUES (?, ?, '已分配', ?, ?)
            """,
            (wave_id, order["id"], staging_location, order["destination"]),
        )
        conn.execute("UPDATE outbound_orders SET status = '波次拣货中' WHERE id = ?", (order["id"],))

    merged_lines = fetch_all(
        conn,
        f"""
        SELECT o.goods_id, ol.sscc, ol.location_id, ROUND(SUM(ol.qty), 3) AS total_qty
        FROM outbound_lines ol
        JOIN outbound_orders o ON o.id = ol.outbound_id
        WHERE ol.outbound_id IN ({','.join('?' for _ in orders)})
        GROUP BY o.goods_id, ol.sscc, ol.location_id
        ORDER BY ol.location_id, o.goods_id, ol.sscc
        """,
        tuple(order["id"] for order in orders),
    )
    if not merged_lines:
        raise ValueError("波次没有可拣货明细")
    for line in merged_lines:
        conn.execute(
            """
            INSERT INTO finished_wave_lines(wave_id, goods_id, sscc, location_id, total_qty, picked_qty, status)
            VALUES (?, ?, ?, ?, ?, 0, '待拣货')
            """,
            (wave_id, line["goods_id"], line["sscc"], line["location_id"], line["total_qty"]),
        )
    log_ledger(conn, "成品波次创建", wave_id, None, None, dock or None, len(orders), None, None, f"{len(orders)} 单，{len(merged_lines)} 条合并拣货；操作人：{operator}")
    return wave_id


def pick_finished_wave(conn: sqlite3.Connection, wave_id: str, data: dict) -> str:
    wave = fetch_one(conn, "SELECT * FROM finished_waves WHERE id = ?", (wave_id,))
    if not wave:
        raise ValueError("波次不存在")
    if wave["status"] == "已完成":
        raise ValueError("波次已完成")
    sscc = require_text(data, "sscc")
    line = fetch_one(conn, "SELECT * FROM finished_wave_lines WHERE wave_id = ? AND sscc = ?", (wave_id, sscc))
    if not line:
        raise ValueError("SSCC 不属于当前波次")
    remaining = float(line["total_qty"]) - float(line["picked_qty"])
    if remaining <= 0.0001:
        raise ValueError("该 SSCC 已拣货完成")
    qty = positive_number(data.get("qty") or remaining, "拣货数量")
    if qty > remaining + 0.0001:
        raise ValueError("拣货数量超过当前波次待拣数量")
    operator = str(data.get("picker") or data.get("_operator") or "").strip()
    now = now_text()
    picked_qty = float(line["picked_qty"]) + qty
    status = "已拣货" if picked_qty >= float(line["total_qty"]) - 0.0001 else "拣货中"
    conn.execute(
        """
        UPDATE finished_wave_lines
        SET picked_qty = ?, status = ?, picker = ?, picked_at = ?
        WHERE id = ?
        """,
        (picked_qty, status, operator, now, line["id"]),
    )
    if status == "已拣货":
        conn.execute(
            """
            UPDATE outbound_lines
            SET status = '已拣货'
            WHERE outbound_id IN (SELECT outbound_id FROM finished_wave_orders WHERE wave_id = ?)
              AND sscc = ?
              AND location_id = ?
            """,
            (wave_id, line["sscc"], line["location_id"]),
        )
    unfinished = conn.execute(
        "SELECT COUNT(*) FROM finished_wave_lines WHERE wave_id = ? AND status != '已拣货'",
        (wave_id,),
    ).fetchone()[0]
    if unfinished:
        conn.execute("UPDATE finished_waves SET status = '拣货中' WHERE id = ?", (wave_id,))
    else:
        conn.execute("UPDATE finished_waves SET status = '已拣货', picked_at = ? WHERE id = ?", (now, wave_id))
        conn.execute("UPDATE finished_wave_orders SET status = '已拣货', picker = ?, picked_at = ? WHERE wave_id = ?", (operator, now, wave_id))
        conn.execute(
            "UPDATE outbound_orders SET status = '已拣货' WHERE id IN (SELECT outbound_id FROM finished_wave_orders WHERE wave_id = ?)",
            (wave_id,),
        )
    log_ledger(conn, "成品波次拣货", wave_id, sscc, line["goods_id"], line["location_id"], qty, float(line["picked_qty"]), picked_qty, f"操作人：{operator}")
    return str(line["id"])


def review_finished_wave_order(conn: sqlite3.Connection, wave_id: str, data: dict) -> str:
    outbound_id = require_text(data, "outbound_id")
    wave_order = fetch_one(conn, "SELECT * FROM finished_wave_orders WHERE wave_id = ? AND outbound_id = ?", (wave_id, outbound_id))
    if not wave_order:
        raise ValueError("发货单不属于当前波次")
    if wave_order["status"] in {"已发货", "已装车"}:
        raise ValueError("发货单已完成装车/发货")
    unpicked = conn.execute(
        """
        SELECT COUNT(*)
        FROM outbound_lines ol
        JOIN outbound_orders o ON o.id = ol.outbound_id
        JOIN finished_wave_lines wl
          ON wl.wave_id = ?
         AND wl.sscc = ol.sscc
         AND wl.location_id = ol.location_id
         AND wl.goods_id = o.goods_id
        WHERE ol.outbound_id = ?
          AND wl.status != '已拣货'
        """,
        (wave_id, outbound_id),
    ).fetchone()[0]
    if unpicked:
        raise ValueError("该订单仍有未完成拣货的明细")
    reviewer = str(data.get("reviewer") or data.get("_operator") or "").strip()
    staging_location = str(data.get("staging_location") or wave_order["staging_location"] or "").strip()
    remark = str(data.get("remark") or "").strip()
    now = now_text()
    conn.execute(
        """
        UPDATE finished_wave_orders
        SET status = '已复核', staging_location = ?, reviewer = ?, reviewed_at = ?, remark = ?
        WHERE wave_id = ? AND outbound_id = ?
        """,
        (staging_location, reviewer, now, remark, wave_id, outbound_id),
    )
    conn.execute("UPDATE outbound_orders SET status = '已复核' WHERE id = ?", (outbound_id,))
    conn.execute("UPDATE finished_waves SET status = '复核中' WHERE id = ? AND status != '已完成'", (wave_id,))
    log_ledger(conn, "成品订单复核", outbound_id, None, None, staging_location or None, 1, None, None, f"波次 {wave_id}；复核人：{reviewer}")
    return outbound_id


def ship_finished_wave_order(conn: sqlite3.Connection, wave_id: str, data: dict) -> str:
    outbound_id = require_text(data, "outbound_id")
    wave_order = fetch_one(conn, "SELECT * FROM finished_wave_orders WHERE wave_id = ? AND outbound_id = ?", (wave_id, outbound_id))
    if not wave_order:
        raise ValueError("发货单不属于当前波次")
    if wave_order["status"] != "已复核":
        raise ValueError("发货单必须先完成订单复核")
    operator = str(data.get("_operator") or "").strip()
    truck_no = str(data.get("truck_no") or "").strip()
    driver = str(data.get("driver") or "").strip()
    seal_no = str(data.get("seal_no") or "").strip()
    dock = str(data.get("dock") or "").strip()
    now = now_text()
    confirm_outbound(conn, outbound_id, operator)
    shipment_id = create_tms_shipment(conn, {
        "outbound_id": outbound_id,
        "wave_id": wave_id,
        "truck_no": truck_no,
        "driver": driver,
        "seal_no": seal_no,
        "_operator": operator,
    })
    conn.execute(
        """
        UPDATE finished_wave_orders
        SET status = '已发货', truck_no = ?, driver = ?, seal_no = ?, loaded_at = ?, shipped_at = ?
        WHERE wave_id = ? AND outbound_id = ?
        """,
        (truck_no, driver, seal_no, now, now, wave_id, outbound_id),
    )
    if dock:
        conn.execute("UPDATE finished_waves SET dock = ? WHERE id = ?", (dock, wave_id))
    unfinished = conn.execute(
        "SELECT COUNT(*) FROM finished_wave_orders WHERE wave_id = ? AND status != '已发货'",
        (wave_id,),
    ).fetchone()[0]
    if unfinished:
        conn.execute("UPDATE finished_waves SET status = '复核中' WHERE id = ?", (wave_id,))
    else:
        conn.execute("UPDATE finished_waves SET status = '已完成', completed_at = ? WHERE id = ?", (now, wave_id))
    log_ledger(conn, "成品装车发货", outbound_id, None, None, dock or None, 1, None, None, f"波次 {wave_id}；TMS {shipment_id}；车牌 {truck_no}；封签 {seal_no}；操作人：{operator}")
    return outbound_id


def finished_waves_payload(conn: sqlite3.Connection) -> list[dict]:
    waves = fetch_all(conn, "SELECT * FROM finished_waves ORDER BY created_at DESC LIMIT 40")
    if not waves:
        return []
    orders = fetch_all(
        conn,
        """
        SELECT
            wo.*,
            o.goods_id,
            o.qty,
            o.allocated_qty,
            o.shortage_qty,
            o.status AS outbound_status,
            o.destination,
            o.bin_no,
            o.created_at AS order_created_at,
            p.name AS goods_name,
            p.unit
        FROM finished_wave_orders wo
        JOIN outbound_orders o ON o.id = wo.outbound_id
        JOIN products p ON p.id = o.goods_id
        ORDER BY wo.id
        """,
    )
    lines = fetch_all(
        conn,
        """
        SELECT wl.*, p.name AS goods_name, p.unit, l.area, l.zone
        FROM finished_wave_lines wl
        JOIN products p ON p.id = wl.goods_id
        JOIN locations l ON l.id = wl.location_id
        ORDER BY l.priority, wl.location_id, wl.goods_id, wl.sscc
        """,
    )
    order_splits = fetch_all(
        conn,
        """
        SELECT
            wo.wave_id,
            ol.outbound_id,
            o.goods_id,
            ol.sscc,
            ol.location_id,
            ol.qty,
            o.destination
        FROM finished_wave_orders wo
        JOIN outbound_lines ol ON ol.outbound_id = wo.outbound_id
        JOIN outbound_orders o ON o.id = ol.outbound_id
        ORDER BY wo.wave_id, ol.sscc, ol.outbound_id
        """,
    )
    for line in lines:
        line["orders"] = [
            split for split in order_splits
            if split["wave_id"] == line["wave_id"]
            and split["goods_id"] == line["goods_id"]
            and split["sscc"] == line["sscc"]
            and split["location_id"] == line["location_id"]
        ]
    for wave in waves:
        wave["orders"] = [order for order in orders if order["wave_id"] == wave["id"]]
        wave["lines"] = [line for line in lines if line["wave_id"] == wave["id"]]
    return waves


def tms_payload(conn: sqlite3.Connection) -> dict:
    shipments = fetch_all(
        conn,
        """
        SELECT
            s.*,
            c.name AS carrier_name,
            l.origin AS lane_origin,
            l.destination AS lane_destination,
            o.channel_code,
            o.min_remaining_days
        FROM tms_shipments s
        JOIN tms_carriers c ON c.code = s.carrier_code
        JOIN tms_lanes l ON l.code = s.lane_code
        LEFT JOIN outbound_orders o ON o.id = s.source_outbound_id
        ORDER BY s.created_at DESC
        LIMIT 120
        """,
    )
    for shipment in shipments:
        ensure_driver_task(conn, shipment["id"])
    lines = fetch_all(
        conn,
        """
        SELECT sl.*, p.name AS goods_name
        FROM tms_shipment_lines sl
        JOIN products p ON p.id = sl.goods_id
        ORDER BY sl.id
        LIMIT 500
        """,
    )
    events = fetch_all(conn, "SELECT * FROM tms_events ORDER BY event_time DESC, id DESC LIMIT 120")
    pods = fetch_all(conn, "SELECT * FROM tms_pods ORDER BY signed_at DESC LIMIT 120")
    freight_bills = fetch_all(conn, "SELECT * FROM tms_freight_bills ORDER BY updated_at DESC, created_at DESC LIMIT 120")
    telemetry = fetch_all(conn, "SELECT * FROM tms_iot_telemetry ORDER BY telemetry_time DESC, id DESC LIMIT 160")
    driver_tasks = fetch_all(conn, "SELECT * FROM tms_driver_tasks ORDER BY updated_at DESC LIMIT 120")
    for shipment in shipments:
        shipment["lines"] = [line for line in lines if line["shipment_id"] == shipment["id"]]
        shipment["events"] = [event for event in events if event["shipment_id"] == shipment["id"]]
        shipment["telemetry"] = [item for item in telemetry if item["shipment_id"] == shipment["id"]]
        shipment["pod"] = next((pod for pod in pods if pod["shipment_id"] == shipment["id"]), None)
        shipment["freight_bill"] = next((bill for bill in freight_bills if bill["shipment_id"] == shipment["id"]), None)
        shipment["driver_task"] = next((task for task in driver_tasks if task["shipment_id"] == shipment["id"]), None)
    return {
        "carriers": fetch_all(conn, "SELECT * FROM tms_carriers ORDER BY code"),
        "lanes": fetch_all(conn, "SELECT * FROM tms_lanes ORDER BY code"),
        "shipments": shipments,
        "events": events,
        "pods": pods,
        "freight_bills": freight_bills,
        "telemetry": telemetry,
        "driver_tasks": driver_tasks,
        "performance": tms_carrier_performance(conn),
        "channel_rules": fetch_all(conn, "SELECT r.*, p.name AS goods_name FROM channel_expiry_rules r JOIN products p ON p.id = r.goods_id ORDER BY r.channel_code, r.goods_id"),
        "control_tower": tms_control_tower(conn),
        "integrations": fetch_all(conn, "SELECT * FROM integration_events ORDER BY created_at DESC LIMIT 160"),
        "audit_packages": fetch_all(conn, "SELECT id, package_type, ref_id, title, status, summary, created_at, operator FROM audit_packages ORDER BY created_at DESC LIMIT 80"),
        "recalls": fetch_all(conn, "SELECT * FROM recall_orders ORDER BY created_at DESC LIMIT 80"),
    }


def tms_carrier_performance(conn: sqlite3.Connection) -> list[dict]:
    carriers = fetch_all(conn, "SELECT * FROM tms_carriers ORDER BY code")
    shipments = fetch_all(conn, "SELECT * FROM tms_shipments")
    bills = fetch_all(conn, "SELECT * FROM tms_freight_bills")
    bill_map = {bill["shipment_id"]: bill for bill in bills}
    rows = []
    for carrier in carriers:
        owned = [shipment for shipment in shipments if shipment["carrier_code"] == carrier["code"]]
        total = len(owned)
        signed = [shipment for shipment in owned if shipment["status"] == "已签收"]
        exception_count = sum(1 for shipment in owned if int(shipment["exception_flag"] or 0))
        on_time_count = 0
        fee_variance_total = 0.0
        fee_variance_samples = 0
        for shipment in signed:
            if shipment.get("eta") and shipment.get("actual_arrival"):
                try:
                    on_time = datetime.strptime(shipment["actual_arrival"][:19], "%Y-%m-%d %H:%M:%S") <= datetime.strptime(shipment["eta"][:19], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    on_time = False
                if on_time and not int(shipment["exception_flag"] or 0):
                    on_time_count += 1
        for shipment in owned:
            bill = bill_map.get(shipment["id"])
            estimated = float((bill or shipment).get("estimated_fee") or 0)
            actual = float((bill or shipment).get("actual_fee") or 0)
            if estimated > 0 and actual > 0:
                fee_variance_total += abs(actual - estimated) / estimated
                fee_variance_samples += 1
        otif_rate = round(on_time_count / total * 100, 1) if total else 100.0
        pod_rate = round(len(signed) / total * 100, 1) if total else 100.0
        exception_rate = round(exception_count / total * 100, 1) if total else 0.0
        fee_variance_rate = round(fee_variance_total / fee_variance_samples * 100, 1) if fee_variance_samples else 0.0
        score = max(0.0, round(100 - exception_rate * 0.8 - max(0, 100 - otif_rate) * 0.5 - fee_variance_rate * 0.2, 1))
        rows.append({
            "carrier_code": carrier["code"],
            "carrier_name": carrier["name"],
            "shipment_count": total,
            "otif_rate": otif_rate,
            "pod_rate": pod_rate,
            "temperature_exception_rate": exception_rate,
            "fee_variance_rate": fee_variance_rate,
            "score": score,
        })
    return rows


def tms_control_tower(conn: sqlite3.Connection) -> dict:
    shipments = fetch_all(conn, "SELECT * FROM tms_shipments")
    telemetry = fetch_all(conn, "SELECT * FROM tms_iot_telemetry ORDER BY telemetry_time DESC")
    tasks = fetch_all(conn, "SELECT * FROM tms_driver_tasks")
    integrations = fetch_all(conn, "SELECT * FROM integration_events ORDER BY created_at DESC LIMIT 80")
    active = [item for item in shipments if item["status"] in {"待发车", "已发车", "在途", "到达", "异常"}]
    high_risk_telemetry = [item for item in telemetry if item["risk_level"] == "高"]
    pending_driver = [item for item in tasks if item["task_status"] in {"待接单", "已接单", "已发车", "到达待签收"}]
    pending_integration = [item for item in integrations if item["status"] in {"待处理", "失败"}]
    risks = []
    for shipment in active:
        if shipment["exception_flag"]:
            risks.append({"severity": "高", "type": "运输异常", "ref_id": shipment["id"], "message": shipment["exception_note"] or "运输异常待处理"})
        elif shipment["status"] == "待发车":
            risks.append({"severity": "中", "type": "待发车", "ref_id": shipment["id"], "message": "运输单已生成，等待司机/承运商发车"})
    for item in high_risk_telemetry[:12]:
        risks.append({"severity": "高", "type": "IoT温控", "ref_id": item["shipment_id"], "message": f"{item['device_id']} {item['temperature']}℃ {item.get('location_text') or ''}".strip()})
    for item in pending_integration[:12]:
        risks.append({"severity": "中" if item["status"] == "待处理" else "高", "type": "接口事件", "ref_id": item["id"], "message": f"{item['system_name']} {item['event_type']}：{item.get('message') or item['status']}"})
    return {
        "active_shipments": len(active),
        "exception_shipments": sum(1 for item in shipments if item["exception_flag"]),
        "high_risk_telemetry": len(high_risk_telemetry),
        "pending_driver_tasks": len(pending_driver),
        "pending_integrations": len(pending_integration),
        "signed_shipments": sum(1 for item in shipments if item["status"] == "已签收"),
        "freight_diff": conn.execute("SELECT COUNT(*) FROM tms_freight_bills WHERE billing_status = '差异'").fetchone()[0],
        "risks": sorted(risks, key=lambda item: {"高": 0, "中": 1, "低": 2}.get(item["severity"], 3))[:30],
    }


def default_tms_lane(conn: sqlite3.Connection, order: dict, product: dict, data: dict) -> dict:
    lane_code = str(data.get("lane_code") or "").strip()
    if not lane_code:
        destination = f"{order.get('destination') or ''} {data.get('destination') or ''}"
        if "杭州" in destination:
            lane_code = "LANE-SZ-HZ-AMB"
        elif product.get("category") == "成品":
            lane_code = "LANE-SZ-SH-COLD"
        else:
            lane_code = "LANE-SZ-NATION-LTL"
    lane = fetch_one(conn, "SELECT * FROM tms_lanes WHERE code = ? AND active = 1", (lane_code,))
    if not lane:
        raise ValueError("TMS线路不存在或未启用")
    return lane


def estimate_tms_fee(lane: dict, qty: float) -> float:
    return round(float(lane.get("base_fee") or 0) + float(lane.get("fee_per_unit") or 0) * qty, 2)


def upsert_tms_freight_bill(
    conn: sqlite3.Connection,
    shipment_id: str,
    carrier_code: str,
    estimated_fee: float,
    actual_fee: float = 0,
    billing_status: str = "待对账",
    exception_reason: str = "",
    confirmed_by: str = "",
) -> str:
    now = now_text()
    existing = fetch_one(conn, "SELECT * FROM tms_freight_bills WHERE shipment_id = ?", (shipment_id,))
    difference = round(float(actual_fee or 0) - float(estimated_fee or 0), 2) if actual_fee else 0.0
    if existing:
        bill_id = existing["id"]
        conn.execute(
            """
            UPDATE tms_freight_bills
            SET carrier_code = ?, estimated_fee = ?, actual_fee = ?, difference = ?,
                billing_status = ?, exception_reason = ?, confirmed_by = COALESCE(NULLIF(?, ''), confirmed_by),
                confirmed_at = CASE WHEN ? IN ('已确认', '差异') THEN COALESCE(confirmed_at, ?) ELSE confirmed_at END,
                updated_at = ?
            WHERE id = ?
            """,
            (carrier_code, estimated_fee, actual_fee, difference, billing_status, exception_reason, confirmed_by, billing_status, now, now, bill_id),
        )
        return bill_id
    bill_id = new_id("FRT")
    conn.execute(
        """
        INSERT INTO tms_freight_bills(
            id, shipment_id, carrier_code, estimated_fee, actual_fee, difference,
            billing_status, exception_reason, confirmed_by, confirmed_at, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            bill_id,
            shipment_id,
            carrier_code,
            estimated_fee,
            actual_fee,
            difference,
            billing_status,
            exception_reason,
            confirmed_by,
            now if billing_status in {"已确认", "差异"} else None,
            now,
            now,
        ),
    )
    return bill_id


def ensure_driver_task(conn: sqlite3.Connection, shipment_id: str) -> str:
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    existing = fetch_one(conn, "SELECT * FROM tms_driver_tasks WHERE shipment_id = ?", (shipment_id,))
    now = now_text()
    if existing:
        conn.execute(
            """
            UPDATE tms_driver_tasks
            SET driver = COALESCE(NULLIF(?, ''), driver),
                driver_phone = COALESCE(NULLIF(?, ''), driver_phone),
                vehicle_no = COALESCE(NULLIF(?, ''), vehicle_no),
                delivery_location = COALESCE(NULLIF(?, ''), delivery_location),
                updated_at = ?
            WHERE shipment_id = ?
            """,
            (shipment.get("driver") or "", shipment.get("driver_phone") or "", shipment.get("vehicle_no") or "", shipment.get("destination") or "", now, shipment_id),
        )
        return existing["id"]
    task_id = new_id("DRV")
    conn.execute(
        """
        INSERT INTO tms_driver_tasks(
            id, shipment_id, driver, driver_phone, vehicle_no, task_status,
            pickup_location, delivery_location, pin_code, assigned_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, '待接单', ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            shipment_id,
            shipment.get("driver") or "",
            shipment.get("driver_phone") or "",
            shipment.get("vehicle_no") or "",
            "苏州工厂月台",
            shipment.get("destination") or "",
            secrets.token_hex(3).upper(),
            now,
            now,
        ),
    )
    return task_id


def update_driver_task(conn: sqlite3.Connection, shipment_id: str, data: dict) -> str:
    task_id = ensure_driver_task(conn, shipment_id)
    task = fetch_one(conn, "SELECT * FROM tms_driver_tasks WHERE id = ?", (task_id,))
    action = str(data.get("action") or data.get("task_status") or "已接单").strip()
    now = now_text()
    status_map = {
        "accept": "已接单",
        "接受": "已接单",
        "已接单": "已接单",
        "depart": "已发车",
        "发车": "已发车",
        "已发车": "已发车",
        "arrive": "到达待签收",
        "到达": "到达待签收",
        "到达待签收": "到达待签收",
        "sign": "已签收",
        "签收": "已签收",
        "已签收": "已签收",
    }
    status = status_map.get(action, action)
    fields = {
        "accepted_at": now if status == "已接单" else task.get("accepted_at"),
        "departed_at": now if status == "已发车" else task.get("departed_at"),
        "arrived_at": now if status == "到达待签收" else task.get("arrived_at"),
        "signed_at": now if status == "已签收" else task.get("signed_at"),
    }
    conn.execute(
        """
        UPDATE tms_driver_tasks
        SET task_status = ?, accepted_at = ?, departed_at = ?, arrived_at = ?, signed_at = ?,
            pod_note = COALESCE(NULLIF(?, ''), pod_note), updated_at = ?
        WHERE id = ?
        """,
        (status, fields["accepted_at"], fields["departed_at"], fields["arrived_at"], fields["signed_at"], str(data.get("pod_note") or data.get("note") or "").strip(), now, task_id),
    )
    if status == "已接单":
        record_integration_event(conn, "司机端", "IN", "司机接单", "shipment", shipment_id, "成功", "司机已接单", data)
    elif status == "已发车":
        dispatch_tms_shipment(conn, shipment_id, {"actual_departure": now, "location_text": data.get("location_text") or "司机端发车", "_operator": data.get("_operator") or "司机端"})
    elif status == "已签收":
        record_tms_pod(conn, shipment_id, {"signed_by": data.get("signed_by") or "司机端POD", "received_qty": data.get("received_qty") or 0, "damaged_qty": data.get("damaged_qty") or 0, "shortage_qty": data.get("shortage_qty") or 0, "note": data.get("pod_note") or data.get("note") or "司机端签收", "_operator": data.get("_operator") or "司机端"})
    return task_id


def record_integration_event(
    conn: sqlite3.Connection,
    system_name: str,
    direction: str,
    event_type: str,
    object_type: str = "",
    object_id: str = "",
    status: str = "成功",
    message: str = "",
    payload: object | None = None,
    operator: str = "",
) -> str:
    event_id = new_id("INT")
    now = now_text()
    conn.execute(
        """
        INSERT INTO integration_events(
            id, system_name, direction, event_type, object_type, object_id,
            status, message, payload, created_at, processed_at, operator
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            system_name,
            direction,
            event_type,
            object_type,
            object_id,
            status,
            message,
            json.dumps(payload or {}, ensure_ascii=False, default=str)[:4000],
            now,
            now if status in {"成功", "失败"} else None,
            operator,
        ),
    )
    return event_id


def create_tms_shipment(conn: sqlite3.Connection, data: dict) -> str:
    outbound_id = require_text(data, "outbound_id")
    order = fetch_one(
        conn,
        """
        SELECT o.*, p.name AS goods_name, p.category, p.unit
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        WHERE o.id = ?
        """,
        (outbound_id,),
    )
    if not order:
        raise ValueError("WMS发货单不存在")
    if float(order["allocated_qty"] or 0) <= 0:
        raise ValueError("发货单没有已分配数量，不能生成运输单")
    product = {"category": order["category"], "unit": order["unit"]}
    lane = default_tms_lane(conn, order, product, data)
    carrier_code = str(data.get("carrier_code") or lane["carrier_code"]).strip()
    if carrier_code != lane["carrier_code"]:
        raise ValueError("承运商与线路不匹配")
    existing = fetch_one(conn, "SELECT * FROM tms_shipments WHERE source_outbound_id = ?", (outbound_id,))
    shipment_id = existing["id"] if existing else new_id("TMS")
    now = now_text()
    planned_departure = str(data.get("planned_departure") or now).strip()
    eta = (datetime.now() + timedelta(days=int(lane["transit_days"] or 1))).strftime("%Y-%m-%d %H:%M:%S")
    customer = str(data.get("customer") or order["destination"]).replace("客户发运：", "").strip()
    destination = str(data.get("destination") or order["destination"]).strip()
    vehicle_no = str(data.get("vehicle_no") or data.get("truck_no") or "").strip()
    driver = str(data.get("driver") or "").strip()
    driver_phone = str(data.get("driver_phone") or "").strip()
    seal_no = str(data.get("seal_no") or "").strip()
    wave_id = str(data.get("wave_id") or "").strip()
    estimated_fee = estimate_tms_fee(lane, float(order["allocated_qty"] or order["qty"] or 0))

    if existing:
        conn.execute(
            """
            UPDATE tms_shipments
            SET wave_id = COALESCE(NULLIF(?, ''), wave_id), carrier_code = ?, lane_code = ?, customer = ?,
                destination = ?, vehicle_no = COALESCE(NULLIF(?, ''), vehicle_no),
                driver = COALESCE(NULLIF(?, ''), driver), driver_phone = COALESCE(NULLIF(?, ''), driver_phone),
                seal_no = COALESCE(NULLIF(?, ''), seal_no), planned_departure = ?,
                eta = ?, temp_min = ?, temp_max = ?, estimated_fee = ?, updated_at = ?
            WHERE id = ?
            """,
            (wave_id, carrier_code, lane["code"], customer, destination, vehicle_no, driver, driver_phone, seal_no, planned_departure, eta, lane["temp_min"], lane["temp_max"], estimated_fee, now, shipment_id),
        )
        upsert_tms_freight_bill(conn, shipment_id, carrier_code, estimated_fee)
        ensure_driver_task(conn, shipment_id)
        return shipment_id

    conn.execute(
        """
        INSERT INTO tms_shipments(
            id, source_outbound_id, wave_id, carrier_code, lane_code, customer, destination,
            vehicle_no, driver, driver_phone, seal_no, planned_departure, eta, temp_min, temp_max,
            status, estimated_fee, created_at, updated_at, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '待发车', ?, ?, ?, ?)
        """,
        (shipment_id, outbound_id, wave_id or None, carrier_code, lane["code"], customer, destination, vehicle_no, driver, driver_phone, seal_no, planned_departure, eta, lane["temp_min"], lane["temp_max"], estimated_fee, now, now, str(data.get("_operator") or "")),
    )
    upsert_tms_freight_bill(conn, shipment_id, carrier_code, estimated_fee)
    ensure_driver_task(conn, shipment_id)
    lines = fetch_all(
        conn,
        """
        SELECT
            ol.*, s.goods_id, s.supplier_batch, s.expiry_date, s.unit
        FROM outbound_lines ol
        JOIN stock_units s ON s.sscc = ol.sscc
        WHERE ol.outbound_id = ?
        ORDER BY ol.id
        """,
        (outbound_id,),
    )
    for line in lines:
        conn.execute(
            """
            INSERT INTO tms_shipment_lines(shipment_id, outbound_id, goods_id, sscc, lot_no, expiry_date, location_id, qty, unit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (shipment_id, outbound_id, line["goods_id"], line["sscc"], line["supplier_batch"], line["expiry_date"], line["location_id"], line["qty"], line["unit"]),
        )
    conn.execute(
        """
        INSERT INTO tms_events(id, shipment_id, event_time, event_type, location_text, note, operator, risk_level)
        VALUES (?, ?, ?, '建单', ?, ?, ?, '低')
        """,
        (new_id("TEV"), shipment_id, now, order["bin_no"] or "", f"由WMS发货单 {outbound_id} 生成", str(data.get("_operator") or "")),
    )
    return shipment_id


def dispatch_tms_shipment(conn: sqlite3.Connection, shipment_id: str, data: dict) -> str:
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    now = str(data.get("actual_departure") or now_text()).strip()
    operator = str(data.get("_operator") or "").strip()
    conn.execute(
        """
        UPDATE tms_shipments
        SET status = '已发车',
            actual_departure = ?,
            vehicle_no = COALESCE(NULLIF(?, ''), vehicle_no),
            driver = COALESCE(NULLIF(?, ''), driver),
            seal_no = COALESCE(NULLIF(?, ''), seal_no),
            updated_at = ?
        WHERE id = ?
        """,
        (now, str(data.get("vehicle_no") or data.get("truck_no") or "").strip(), str(data.get("driver") or "").strip(), str(data.get("seal_no") or "").strip(), now_text(), shipment_id),
    )
    conn.execute(
        """
        INSERT INTO tms_events(id, shipment_id, event_time, event_type, location_text, note, operator, risk_level)
        VALUES (?, ?, ?, '发车', ?, '车辆已发车', ?, '低')
        """,
        (new_id("TEV"), shipment_id, now, str(data.get("location_text") or "工厂月台"), operator),
    )
    ensure_driver_task(conn, shipment_id)
    conn.execute(
        """
        UPDATE tms_driver_tasks
        SET task_status = '已发车',
            driver = COALESCE(NULLIF(?, ''), driver),
            vehicle_no = COALESCE(NULLIF(?, ''), vehicle_no),
            departed_at = COALESCE(departed_at, ?),
            updated_at = ?
        WHERE shipment_id = ?
        """,
        (str(data.get("driver") or "").strip(), str(data.get("vehicle_no") or data.get("truck_no") or "").strip(), now, now_text(), shipment_id),
    )
    return shipment_id


def record_tms_event(conn: sqlite3.Connection, shipment_id: str, data: dict) -> str:
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    event_id = new_id("TEV")
    event_type = str(data.get("event_type") or "GPS/温度").strip()
    event_time = str(data.get("event_time") or now_text()).strip()
    temperature_raw = str(data.get("temperature") or "").strip()
    temperature = float(temperature_raw) if temperature_raw else None
    risk_level = "低"
    note = str(data.get("note") or "").strip()
    if temperature is not None:
        if shipment["temp_min"] is not None and temperature < float(shipment["temp_min"]):
            risk_level = "高"
            note = note or "低于运输温控下限"
        if shipment["temp_max"] is not None and temperature > float(shipment["temp_max"]):
            risk_level = "高"
            note = note or "高于运输温控上限"
    conn.execute(
        """
        INSERT INTO tms_events(id, shipment_id, event_time, event_type, location_text, temperature, humidity, door_open, risk_level, note, operator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (event_id, shipment_id, event_time, event_type, str(data.get("location_text") or "").strip(), temperature, data.get("humidity"), 1 if data.get("door_open") else 0, risk_level, note, str(data.get("_operator") or "")),
    )
    if risk_level == "高":
        conn.execute(
            "UPDATE tms_shipments SET status = '异常', exception_flag = 1, exception_note = ?, updated_at = ? WHERE id = ?",
            (note, now_text(), shipment_id),
        )
    elif shipment["status"] == "已发车":
        conn.execute("UPDATE tms_shipments SET status = '在途', updated_at = ? WHERE id = ?", (now_text(), shipment_id))
    return event_id


def record_iot_telemetry(conn: sqlite3.Connection, data: dict) -> str:
    shipment_id = require_text(data, "shipment_id")
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    device_id = require_text(data, "device_id")
    telemetry_time = str(data.get("telemetry_time") or data.get("event_time") or now_text()).strip()
    temperature_raw = str(data.get("temperature") or "").strip()
    humidity_raw = str(data.get("humidity") or "").strip()
    latitude_raw = str(data.get("latitude") or "").strip()
    longitude_raw = str(data.get("longitude") or "").strip()
    speed_raw = str(data.get("speed") or "").strip()
    temperature = float(temperature_raw) if temperature_raw else None
    humidity = float(humidity_raw) if humidity_raw else None
    latitude = float(latitude_raw) if latitude_raw else None
    longitude = float(longitude_raw) if longitude_raw else None
    speed = float(speed_raw) if speed_raw else None
    door_open = 1 if data.get("door_open") else 0
    risk_level = "低"
    note = str(data.get("note") or "").strip()
    if temperature is not None:
        if shipment["temp_min"] is not None and temperature < float(shipment["temp_min"]):
            risk_level = "高"
            note = note or "IoT低于运输温控下限"
        if shipment["temp_max"] is not None and temperature > float(shipment["temp_max"]):
            risk_level = "高"
            note = note or "IoT高于运输温控上限"
    if door_open and shipment["status"] in {"已发车", "在途"}:
        risk_level = "高"
        note = note or "运输途中开门"
    telemetry_id = new_id("IOT")
    conn.execute(
        """
        INSERT INTO tms_iot_telemetry(
            id, shipment_id, device_id, telemetry_time, latitude, longitude, location_text,
            temperature, humidity, door_open, reefer_status, speed, risk_level, note, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telemetry_id,
            shipment_id,
            device_id,
            telemetry_time,
            latitude,
            longitude,
            str(data.get("location_text") or "").strip(),
            temperature,
            humidity,
            door_open,
            str(data.get("reefer_status") or "").strip(),
            speed,
            risk_level,
            note,
            now_text(),
        ),
    )
    record_tms_event(
        conn,
        shipment_id,
        {
            "event_type": "IoT温控/GPS",
            "event_time": telemetry_time,
            "location_text": data.get("location_text") or f"{latitude or '-'}, {longitude or '-'}",
            "temperature": temperature if temperature is not None else "",
            "humidity": humidity if humidity is not None else "",
            "door_open": door_open,
            "note": note or f"设备 {device_id} 自动上报",
            "_operator": data.get("_operator") or f"IoT:{device_id}",
        },
    )
    record_integration_event(conn, "IoT平台", "IN", "GPS/温控遥测", "shipment", shipment_id, "成功", note or "IoT遥测已入库", data, str(data.get("_operator") or ""))
    return telemetry_id


def record_tms_pod(conn: sqlite3.Connection, shipment_id: str, data: dict) -> str:
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    pod_id = new_id("POD")
    signed_by = require_text(data, "signed_by")
    signed_at = str(data.get("signed_at") or now_text()).strip()
    received_qty = float(data.get("received_qty") or 0)
    damaged_qty = float(data.get("damaged_qty") or 0)
    shortage_qty = float(data.get("shortage_qty") or 0)
    note = str(data.get("note") or "").strip()
    conn.execute(
        """
        INSERT OR REPLACE INTO tms_pods(id, shipment_id, signed_by, signed_at, received_qty, damaged_qty, shortage_qty, note, operator)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (pod_id, shipment_id, signed_by, signed_at, received_qty, damaged_qty, shortage_qty, note, str(data.get("_operator") or "")),
    )
    if damaged_qty or shortage_qty:
        status = "异常"
        exception_flag = 1
        exception_note = note or f"POD异常：破损 {fmt_qty(damaged_qty)}，短少 {fmt_qty(shortage_qty)}"
    else:
        status = "已签收"
        exception_flag = 0
        exception_note = None
    conn.execute(
        "UPDATE tms_shipments SET status = ?, actual_arrival = ?, exception_flag = ?, exception_note = ?, updated_at = ? WHERE id = ?",
        (status, signed_at, exception_flag, exception_note, now_text(), shipment_id),
    )
    ensure_driver_task(conn, shipment_id)
    conn.execute(
        """
        UPDATE tms_driver_tasks
        SET task_status = ?, signed_at = ?, pod_note = COALESCE(NULLIF(?, ''), pod_note), updated_at = ?
        WHERE shipment_id = ?
        """,
        ("已签收" if status == "已签收" else "签收异常", signed_at, note, now_text(), shipment_id),
    )
    return pod_id


def settle_tms_freight(conn: sqlite3.Connection, shipment_id: str, data: dict) -> str:
    actual_fee = float(data.get("actual_fee") or 0)
    if actual_fee <= 0:
        raise ValueError("实际运费必须大于 0")
    shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
    if not shipment:
        raise ValueError("TMS运单不存在")
    estimated = float(shipment["estimated_fee"] or 0)
    billing_status = "已确认" if abs(actual_fee - estimated) <= 0.01 else "差异"
    exception_reason = str(data.get("exception_reason") or data.get("reason") or "").strip()
    if billing_status == "差异" and not exception_reason:
        exception_reason = f"预估 {fmt_qty(estimated)}，实际 {fmt_qty(actual_fee)}"
    operator = str(data.get("_operator") or "").strip()
    conn.execute(
        """
        UPDATE tms_shipments
        SET actual_fee = ?, billing_status = ?, updated_at = ?
        WHERE id = ?
        """,
        (actual_fee, billing_status, now_text(), shipment_id),
    )
    upsert_tms_freight_bill(
        conn,
        shipment_id,
        shipment["carrier_code"],
        estimated,
        actual_fee,
        billing_status,
        exception_reason,
        operator,
    )
    return shipment_id


def create_recall_order(conn: sqlite3.Connection, data: dict) -> str:
    goods_id = require_text(data, "goods_id")
    supplier_batch = require_text(data, "supplier_batch")
    reason = str(data.get("reason") or "批次召回").strip()
    operator = str(data.get("_operator") or "").strip()
    affected_stocks = fetch_all(
        conn,
        "SELECT * FROM stock_units WHERE goods_id = ? AND supplier_batch = ? AND qty > 0 AND quality_status != '已出库' ORDER BY sscc",
        (goods_id, supplier_batch),
    )
    affected_shipment_rows = fetch_all(
        conn,
        "SELECT DISTINCT shipment_id FROM tms_shipment_lines WHERE goods_id = ? AND lot_no = ? ORDER BY shipment_id",
        (goods_id, supplier_batch),
    )
    affected_inventory = len(affected_stocks)
    affected_shipment_ids = [row["shipment_id"] for row in affected_shipment_rows]
    affected_shipments = len(affected_shipment_ids)
    sscc_list = [stock["sscc"] for stock in affected_stocks]
    conn.execute(
        "UPDATE stock_units SET quality_status = '冻结', updated_at = ? WHERE goods_id = ? AND supplier_batch = ? AND qty > 0",
        (now_text(), goods_id, supplier_batch),
    )
    recall_id = new_id("REC")
    for stock in affected_stocks:
        log_ledger(
            conn,
            "召回批次冻结",
            recall_id,
            stock["sscc"],
            goods_id,
            stock["location_id"],
            stock["qty"],
            stock["qty"],
            stock["qty"],
            f"批次 {supplier_batch}；原因：{reason}；操作人：{operator}" if operator else f"批次 {supplier_batch}；原因：{reason}",
        )
    conn.execute(
        """
        INSERT INTO recall_orders(
            id, goods_id, supplier_batch, reason, affected_inventory, affected_shipments,
            affected_sscc, affected_shipment_ids, status, created_at, operator
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '已冻结', ?, ?)
        """,
        (recall_id, goods_id, supplier_batch, reason, affected_inventory, affected_shipments, "、".join(sscc_list), "、".join(affected_shipment_ids), now_text(), operator),
    )
    return recall_id


def process_integration_event(conn: sqlite3.Connection, data: dict) -> str:
    system_name = str(data.get("system_name") or "外部系统").strip()
    event_type = str(data.get("event_type") or "").strip()
    operator = str(data.get("_operator") or "").strip()
    object_type = ""
    object_id = ""
    message = ""
    try:
        if event_type == "OMS订单导入":
            object_id = create_finished_shipment(conn, data)
            object_type = "outbound_order"
            message = f"OMS订单已生成成品发运单 {object_id}"
        elif event_type == "ERP运费回传":
            shipment_id = require_text(data, "shipment_id")
            settle_tms_freight(conn, shipment_id, data)
            object_type = "shipment"
            object_id = shipment_id
            message = f"ERP运费已回写 {shipment_id}"
        elif event_type in {"MES放行", "QMS放行", "MES冻结", "QMS冻结"}:
            sscc = require_text(data, "sscc")
            status = "合格" if "放行" in event_type else "冻结"
            change_status(conn, {"sscc": sscc, "quality_status": status, "reason": data.get("reason") or event_type, "_operator": operator})
            object_type = "stock_unit"
            object_id = sscc
            message = f"{event_type} 已更新 {sscc} 为 {status}"
        elif event_type == "QMS召回":
            object_id = create_recall_order(conn, data)
            object_type = "recall"
            message = f"QMS召回已生成 {object_id}"
        elif event_type == "承运商状态回传":
            shipment_id = require_text(data, "shipment_id")
            record_tms_event(conn, shipment_id, data)
            object_type = "shipment"
            object_id = shipment_id
            message = f"承运商状态已回传 {shipment_id}"
        elif event_type == "IoT遥测":
            object_id = record_iot_telemetry(conn, data)
            object_type = "iot_telemetry"
            message = f"IoT遥测已接收 {object_id}"
        else:
            object_type = str(data.get("object_type") or "").strip()
            object_id = str(data.get("object_id") or "").strip()
            message = "接口事件已记录，等待人工处理"
            return record_integration_event(conn, system_name, "IN", event_type or "接口事件", object_type, object_id, "待处理", message, data, operator)
        return record_integration_event(conn, system_name, "IN", event_type, object_type, object_id, "成功", message, data, operator)
    except Exception as exc:
        event_id = record_integration_event(conn, system_name, "IN", event_type or "接口事件", object_type, object_id, "失败", str(exc), data, operator)
        raise ValueError(f"{event_type or '接口事件'} 处理失败：{exc}；接口日志 {event_id}")


def create_audit_package(conn: sqlite3.Connection, data: dict) -> str:
    package_type = str(data.get("package_type") or "批次追溯审计").strip()
    ref_id = str(data.get("ref_id") or data.get("shipment_id") or data.get("recall_id") or data.get("goods_id") or "").strip()
    operator = str(data.get("_operator") or "").strip()
    if package_type == "运输审计":
        shipment_id = require_text(data, "shipment_id")
        shipment = fetch_one(conn, "SELECT * FROM tms_shipments WHERE id = ?", (shipment_id,))
        if not shipment:
            raise ValueError("TMS运单不存在")
        payload = {
            "shipment": shipment,
            "lines": fetch_all(conn, "SELECT * FROM tms_shipment_lines WHERE shipment_id = ? ORDER BY id", (shipment_id,)),
            "events": fetch_all(conn, "SELECT * FROM tms_events WHERE shipment_id = ? ORDER BY event_time, id", (shipment_id,)),
            "telemetry": fetch_all(conn, "SELECT * FROM tms_iot_telemetry WHERE shipment_id = ? ORDER BY telemetry_time, id", (shipment_id,)),
            "pod": fetch_one(conn, "SELECT * FROM tms_pods WHERE shipment_id = ?", (shipment_id,)),
            "freight": fetch_one(conn, "SELECT * FROM tms_freight_bills WHERE shipment_id = ?", (shipment_id,)),
            "driver_task": fetch_one(conn, "SELECT * FROM tms_driver_tasks WHERE shipment_id = ?", (shipment_id,)),
        }
        title = f"运输审计证据包 {shipment_id}"
        summary = f"运单 {shipment_id}，事件 {len(payload['events'])} 条，遥测 {len(payload['telemetry'])} 条"
        ref_id = shipment_id
    else:
        goods_id = require_text(data, "goods_id")
        supplier_batch = require_text(data, "supplier_batch")
        payload = {
            "goods_id": goods_id,
            "supplier_batch": supplier_batch,
            "inventory": fetch_all(conn, "SELECT * FROM stock_units WHERE goods_id = ? AND supplier_batch = ? ORDER BY sscc", (goods_id, supplier_batch)),
            "shipments": fetch_all(
                conn,
                """
                SELECT s.*
                FROM tms_shipments s
                JOIN tms_shipment_lines sl ON sl.shipment_id = s.id
                WHERE sl.goods_id = ? AND sl.lot_no = ?
                GROUP BY s.id
                ORDER BY s.created_at DESC
                """,
                (goods_id, supplier_batch),
            ),
            "recalls": fetch_all(conn, "SELECT * FROM recall_orders WHERE goods_id = ? AND supplier_batch = ? ORDER BY created_at DESC", (goods_id, supplier_batch)),
            "ledger": fetch_all(conn, "SELECT * FROM ledger WHERE goods_id = ? ORDER BY ts DESC LIMIT 120", (goods_id,)),
        }
        title = f"批次追溯审计证据包 {goods_id}/{supplier_batch}"
        summary = f"在库 {len(payload['inventory'])} 条，发运 {len(payload['shipments'])} 单，召回 {len(payload['recalls'])} 条"
        ref_id = ref_id or f"{goods_id}/{supplier_batch}"
    package_id = new_id("AUD")
    conn.execute(
        """
        INSERT INTO audit_packages(id, package_type, ref_id, title, status, summary, payload, created_at, operator)
        VALUES (?, ?, ?, ?, '已生成', ?, ?, ?, ?)
        """,
        (package_id, package_type, ref_id, title, summary, json.dumps(payload, ensure_ascii=False, default=str)[:20000], now_text(), operator),
    )
    record_integration_event(conn, "审计中心", "OUT", "生成审计包", "audit_package", package_id, "成功", summary, {"package_type": package_type, "ref_id": ref_id}, operator)
    return package_id


ISSUE_ACTIONS = {"出库确认", "成品发运确认", "包材领用确认"}


def severity_rank(severity: str) -> int:
    return {"高": 0, "中": 1, "低": 2}.get(severity, 3)


def build_smart_alerts(
    stock_warnings: list[dict],
    expiry_warnings: list[dict],
    outbounds: list[dict],
    inventory: list[dict],
    counts: list[dict],
    waves: list[dict],
) -> list[dict]:
    alerts: list[dict] = []
    for item in stock_warnings:
        severity = "高" if item.get("stock_status") == "red" else "中"
        alerts.append({
            "severity": severity,
            "type": "安全库存",
            "target": item["id"],
            "title": f"{item['name']} 低于{'最低' if severity == '高' else '安全'}库存",
            "detail": f"可用 {fmt_qty(item.get('available'))} {item.get('unit')}，安全库存 {fmt_qty(item.get('safety_qty'))}，建议补足 {fmt_qty(item.get('reorder_qty'))}。",
            "action": "生成补货/生产计划，或调整发货优先级",
            "priority": 90 if severity == "高" else 70,
        })
    for item in expiry_warnings:
        days_left = item.get("days_left")
        severity = "高" if days_left is not None and days_left < 0 else "中"
        alerts.append({
            "severity": severity,
            "type": "临期",
            "target": item["sscc"],
            "title": f"{item['goods_name']} {item.get('expiry_status_label') or '临期'}",
            "detail": f"SSCC {item['sscc']} 位于 {item['location_id']}，数量 {fmt_qty(item.get('qty'))} {item.get('unit')}，BBD {item.get('expiry_date') or '-'}。",
            "action": "发货/领用时优先分配，必要时冻结复核",
            "priority": 85 if severity == "高" else 65,
        })
    for order in outbounds:
        if order.get("status") == "欠品":
            alerts.append({
                "severity": "高",
                "type": "欠品",
                "target": order["id"],
                "title": f"{order['goods_name']} 出库欠品",
                "detail": f"需求 {fmt_qty(order.get('qty'))} {order.get('unit')}，已分配 {fmt_qty(order.get('allocated_qty'))}，欠品 {fmt_qty(order.get('shortage_qty'))}。",
                "action": "补货、改量或拆单后再确认",
                "priority": 95,
            })
    for stock in inventory:
        if stock.get("quality_status") in {"暂扣", "冻结", "隔离", "待检"}:
            severity = "高" if stock["quality_status"] in {"冻结", "隔离"} else "中"
            alerts.append({
                "severity": severity,
                "type": "品质状态",
                "target": stock["sscc"],
                "title": f"{stock['goods_name']} 处于{stock['quality_status']}",
                "detail": f"SSCC {stock['sscc']}，库位 {stock['location_id']}，数量 {fmt_qty(stock.get('qty'))} {stock.get('unit')}，不会参与正常分配。",
                "action": "质量复核后放行或继续隔离",
                "priority": 80 if severity == "高" else 55,
            })
    for count in counts[:20]:
        diff = float(count.get("diff_qty") or 0)
        if abs(diff) > 0.0001:
            severity = "高" if abs(diff) >= 10 else "中"
            alerts.append({
                "severity": severity,
                "type": "盘点差异",
                "target": count["sscc"],
                "title": f"盘点差异 {fmt_qty(diff)}",
                "detail": f"SSCC {count['sscc']}，系统数 {fmt_qty(count.get('system_qty'))}，实盘数 {fmt_qty(count.get('actual_qty'))}，原因：{count.get('reason') or '-'}。",
                "action": "复盘出入库流水和现场实物",
                "priority": 75 if severity == "高" else 50,
            })
    for wave in waves:
        if wave.get("status") not in {"已完成", "取消"}:
            pending_orders = len([order for order in wave.get("orders", []) if order.get("status") != "已发货"])
            if pending_orders:
                alerts.append({
                    "severity": "低",
                    "type": "波次进度",
                    "target": wave["id"],
                    "title": f"成品波次 {wave['status']}",
                    "detail": f"波次 {wave['id']} 仍有 {pending_orders} 张订单未发货，月台 {wave.get('dock') or '-'}。",
                    "action": "跟进拣货、复核或装车节点",
                    "priority": 35,
                })
    alerts.sort(key=lambda item: (severity_rank(item["severity"]), -int(item.get("priority") or 0), item["type"], item["target"]))
    return alerts[:80]


def fmt_qty(value: object) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return str(value or "")
    text = f"{number:.3f}".rstrip("0").rstrip(".")
    return text or "0"


def dynamic_safety_recommendations(conn: sqlite3.Connection, product_summary: list[dict]) -> list[dict]:
    issue_rows = fetch_all(
        conn,
        """
        SELECT goods_id, ROUND(SUM(qty), 3) AS issue_qty, COUNT(DISTINCT date(ts)) AS active_days
        FROM ledger
        WHERE action IN ('出库确认', '成品发运确认', '包材领用确认')
          AND date(ts) >= date('now', '-30 day')
          AND goods_id IS NOT NULL
        GROUP BY goods_id
        """,
    )
    issue_by_goods = {row["goods_id"]: row for row in issue_rows}
    category_days = {
        "成品": (5, 5),
        "包材": (14, 7),
        "原料": (10, 5),
        "液体原料": (10, 5),
        "返工料": (3, 3),
    }
    recommendations: list[dict] = []
    for item in product_summary:
        issue = issue_by_goods.get(item["id"], {})
        issue_qty = float(issue.get("issue_qty") or 0)
        daily_issue = issue_qty / 30 if issue_qty else 0
        lead_days, buffer_days = category_days.get(item.get("category"), (7, 5))
        min_qty = float(item.get("min_qty") or 0)
        current_safety = float(item.get("safety_qty") or min_qty)
        if daily_issue:
            suggested = max(min_qty, daily_issue * (lead_days + buffer_days))
            confidence = "高" if int(issue.get("active_days") or 0) >= 3 else "中"
            basis = f"近30天出库 {fmt_qty(issue_qty)}，日均 {fmt_qty(daily_issue)}，供应周期 {lead_days} 天，缓冲 {buffer_days} 天"
        else:
            suggested = max(current_safety, min_qty)
            confidence = "低"
            basis = "暂无近30天出库历史，先沿用当前安全库存作为基准"
        suggested = round(suggested, 3)
        diff = round(suggested - current_safety, 3)
        if diff > max(1, current_safety * 0.1):
            action = "建议调高"
        elif diff < -max(1, current_safety * 0.1):
            action = "建议下调"
        else:
            action = "保持"
        recommendations.append({
            "goods_id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "unit": item["unit"],
            "available": item.get("available"),
            "current_safety_qty": round(current_safety, 3),
            "suggested_safety_qty": suggested,
            "diff_qty": diff,
            "daily_issue_qty": round(daily_issue, 3),
            "lead_days": lead_days,
            "buffer_days": buffer_days,
            "confidence": confidence,
            "action": action,
            "basis": basis,
        })
    recommendations.sort(key=lambda item: ({"建议调高": 0, "建议下调": 1, "保持": 2}.get(item["action"], 3), item["category"], item["goods_id"]))
    return recommendations


def smart_wave_suggestions(conn: sqlite3.Connection) -> list[dict]:
    rows = fetch_all(
        conn,
        """
        SELECT
            o.*,
            p.name AS goods_name,
            p.unit,
            COUNT(ol.id) AS pick_lines
        FROM outbound_orders o
        JOIN products p ON p.id = o.goods_id
        LEFT JOIN outbound_lines ol ON ol.outbound_id = o.id
        WHERE p.category = '成品'
          AND o.status = '已分配'
          AND o.shortage_qty = 0
          AND NOT EXISTS (
              SELECT 1
              FROM finished_wave_orders wo
              WHERE wo.outbound_id = o.id
                AND wo.status NOT IN ('已发货', '取消')
          )
        GROUP BY o.id
        ORDER BY o.bin_no, o.destination, o.created_at
        """
    )
    groups: dict[str, dict] = {}
    for row in rows:
        dock = row.get("bin_no") or "未指定月台"
        key = str(dock)
        if key not in groups:
            groups[key] = {
                "dock": dock,
                "route": f"智能波次-{dock}",
                "order_ids": [],
                "order_count": 0,
                "total_qty": 0.0,
                "pick_lines": 0,
                "sku_count": 0,
                "skus": set(),
                "customers": set(),
                "reason": "",
            }
        group = groups[key]
        group["order_ids"].append(row["id"])
        group["order_count"] += 1
        group["total_qty"] += float(row.get("qty") or 0)
        group["pick_lines"] += int(row.get("pick_lines") or 0)
        group["skus"].add(row["goods_id"])
        group["customers"].add(row.get("destination") or "")
    suggestions = []
    for group in groups.values():
        sku_count = len(group.pop("skus"))
        customers = sorted(customer for customer in group.pop("customers") if customer)
        group["sku_count"] = sku_count
        group["customer_count"] = len(customers)
        group["customers"] = "、".join(customers[:4])
        group["total_qty"] = round(group["total_qty"], 3)
        group["reason"] = f"同月台 {group['dock']}，{group['order_count']} 单合并，{sku_count} 个 SKU，减少重复拣货"
        suggestions.append(group)
    suggestions.sort(key=lambda item: (-item["order_count"], item["dock"]))
    return suggestions


def create_smart_finished_wave(conn: sqlite3.Connection, data: dict) -> str:
    suggestions = smart_wave_suggestions(conn)
    if not suggestions:
        raise ValueError("暂无可智能生成波次的成品发货单")
    wanted_dock = str(data.get("dock") or "").strip()
    selected = next((item for item in suggestions if wanted_dock and item["dock"] == wanted_dock), None)
    if not selected:
        selected = suggestions[0]
    payload = {
        "order_ids": selected["order_ids"],
        "dock": selected["dock"],
        "route": str(data.get("route") or selected["route"]).strip(),
        "ship_date": str(data.get("ship_date") or date.today().isoformat()).strip(),
        "remark": str(data.get("remark") or selected["reason"]).strip(),
        "_operator": data.get("_operator"),
    }
    return create_finished_wave(conn, payload)


def apply_dynamic_safety(conn: sqlite3.Connection, data: dict) -> str:
    goods_id = require_text(data, "goods_id")
    safety_qty = positive_number(data.get("safety_qty"), "建议安全库存")
    product = fetch_one(conn, "SELECT * FROM products WHERE id = ?", (goods_id,))
    if not product:
        raise ValueError("货品不存在")
    old_qty = float(product["safety_qty"] or 0)
    conn.execute("UPDATE products SET safety_qty = ? WHERE id = ?", (safety_qty, goods_id))
    log_ledger(
        conn,
        "智能安全库存更新",
        goods_id,
        None,
        goods_id,
        None,
        safety_qty - old_qty,
        old_qty,
        safety_qty,
        str(data.get("reason") or "应用动态安全库存建议"),
    )
    return goods_id


def find_product_from_text(conn: sqlite3.Connection, text: str) -> dict | None:
    text_lower = text.lower()
    products = fetch_all(conn, "SELECT * FROM products ORDER BY LENGTH(id) DESC, id")
    for product in products:
        if product["id"].lower() in text_lower or product["name"] in text:
            return product
    return None


def smart_query_answer(conn: sqlite3.Connection, data: dict, user: dict) -> dict:
    question = require_text(data, "question")
    product = find_product_from_text(conn, question)
    text = question.lower()
    if "日志" in question and "logs" not in role_permissions(user["role"]):
        return {
            "question": question,
            "intent": "权限说明",
            "answer": "系统日志只对系统管理员和仓库主管开放，当前账号不能查询日志明细。",
            "rows": [],
        }
    if any(word in question for word in ("临期", "过期", "效期", "bbd", "BBD")):
        rows = fetch_all(
            conn,
            """
            SELECT s.sscc, s.goods_id, p.name AS goods_name, s.location_id, s.qty, p.unit, s.expiry_date, p.expiry_alert_days
            FROM stock_units s
            JOIN products p ON p.id = s.goods_id
            WHERE s.qty > 0
              AND s.quality_status != '已出库'
              AND s.expiry_date IS NOT NULL
              AND s.expiry_date != ''
              AND date(s.expiry_date) <= date('now', '+' || p.expiry_alert_days || ' day')
            ORDER BY date(s.expiry_date), s.location_id, s.sscc
            LIMIT 20
            """,
        )
        enrich_expiry_status(rows, date.today())
        return {
            "question": question,
            "intent": "临期查询",
            "answer": f"当前共有 {len(rows)} 个临期/过期批次。优先处理剩余天数最少、且品质为合格的批次。",
            "rows": rows,
        }
    if any(word in question for word in ("暂扣", "冻结", "隔离", "待检", "品质")):
        rows = fetch_all(
            conn,
            """
            SELECT s.sscc, s.goods_id, p.name AS goods_name, s.location_id, s.qty, p.unit, s.quality_status, s.supplier_batch, s.po_no
            FROM stock_units s
            JOIN products p ON p.id = s.goods_id
            WHERE s.qty > 0 AND s.quality_status IN ('暂扣', '冻结', '隔离', '待检')
            ORDER BY s.quality_status, s.location_id, s.sscc
            LIMIT 30
            """,
        )
        return {
            "question": question,
            "intent": "品质状态查询",
            "answer": f"当前共有 {len(rows)} 个非合格状态批次；这些批次不会参与正常出库或发料分配。",
            "rows": rows,
        }
    if any(word in question for word in ("欠品", "缺货", "缺料", "短缺")):
        rows = fetch_all(
            conn,
            """
            SELECT o.id, o.goods_id, p.name AS goods_name, p.category, o.qty, o.allocated_qty, o.shortage_qty, p.unit, o.destination, o.bin_no, o.status
            FROM outbound_orders o
            JOIN products p ON p.id = o.goods_id
            WHERE o.status = '欠品' OR o.shortage_qty > 0
            ORDER BY o.created_at DESC
            LIMIT 30
            """,
        )
        return {
            "question": question,
            "intent": "欠品查询",
            "answer": f"当前共有 {len(rows)} 张欠品/短缺出库单，不能直接确认发货或投料。",
            "rows": rows,
        }
    if any(word in question for word in ("波次", "发货", "订单", "装车", "拣货", "复核")):
        rows = finished_waves_payload(conn)[:10]
        pending = sum(1 for wave in rows for order in wave.get("orders", []) if order.get("status") != "已发货")
        return {
            "question": question,
            "intent": "成品发货进度",
            "answer": f"最近 {len(rows)} 个成品波次中，还有 {pending} 张订单未完成发货。可进入 智能 > 智能波次 或 成品 > 发货记录 查看。",
            "rows": rows,
        }
    if any(word in question for word in ("安全库存", "补货", "建议库存")):
        payload = bootstrap_payload(conn, user)
        rows = payload["smart"]["safety_recommendations"][:20]
        adjust_count = sum(1 for row in rows if row["action"] != "保持")
        return {
            "question": question,
            "intent": "动态安全库存",
            "answer": f"系统已计算 {len(rows)} 个 SKU 的动态安全库存建议，其中 {adjust_count} 个建议调整。",
            "rows": rows,
        }
    if any(word in question for word in ("盘点", "差异", "盘亏", "盘盈")):
        rows = fetch_all(
            conn,
            """
            SELECT *
            FROM counts
            WHERE ABS(diff_qty) > 0.0001
            ORDER BY created_at DESC
            LIMIT 20
            """,
        )
        return {
            "question": question,
            "intent": "盘点差异查询",
            "answer": f"最近记录中共有 {len(rows)} 条盘点差异。差异调整仍只允许 admin/supervisor 执行。",
            "rows": rows,
        }
    if product or any(word in question for word in ("库存", "还有多少", "多少", "可用")):
        params: tuple = ()
        where = "s.qty > 0"
        if product:
            where += " AND s.goods_id = ?"
            params = (product["id"],)
        rows = fetch_all(
            conn,
            f"""
            SELECT s.sscc, s.goods_id, p.name AS goods_name, p.category, s.location_id, s.qty, s.reserved_qty,
                   ROUND(s.qty - s.reserved_qty, 3) AS available_qty, p.unit, s.quality_status, s.expiry_date
            FROM stock_units s
            JOIN products p ON p.id = s.goods_id
            WHERE {where}
            ORDER BY p.category, s.location_id, date(NULLIF(s.expiry_date, '')), s.sscc
            LIMIT 30
            """,
            params,
        )
        available = round(sum(float(row.get("available_qty") or 0) for row in rows if row.get("quality_status") == "合格"), 3)
        target = f"{product['id']} {product['name']}" if product else "全部库存"
        return {
            "question": question,
            "intent": "库存查询",
            "answer": f"{target} 当前可用合格库存合计 {fmt_qty(available)}。下方列出前 {len(rows)} 个批次/托盘。",
            "rows": rows,
        }
    return {
        "question": question,
        "intent": "无法识别",
        "answer": "我还没有识别到明确意图。可以问：某个 SKU 还有多少、哪些临期、哪些暂扣、有没有欠品、成品发货到哪一步、动态安全库存建议。",
        "rows": [],
    }


SOP_GUIDES = {
    "成品发货": {
        "title": "成品发货 SOP",
        "steps": ["成品 > 发货通知：录入客户/销售订单/SKU/数量/月台", "成品 > 波次创建 或 智能 > 智能波次：合并同月台订单", "成品 > 合并拣货：扫描 SSCC，按汇总拣货行拣货", "成品 > 订单复核：按客户订单拆分复核", "成品 > 装车发货：录入车牌、司机、封签并确认扣减库存"],
        "checks": ["欠品单不能发货", "暂扣/冻结/隔离批次不会参与分配", "未复核订单不能装车发货"],
        "next_action": "先进入 成品 > 发货通知 创建发货单；多订单场景建议进入 智能 > 智能波次。",
    },
    "入库": {
        "title": "入库上架 SOP",
        "steps": ["入库 > 库位推荐：先按货品/数量/品质获取推荐库位", "入库 > 新建入库：录入供应商批次、PO、生产日期、BBD、库位", "系统生成入库单、SSCC 和库存流水", "RF/扫码 可扫描 SSCC 或库位复核"],
        "checks": ["待检/暂扣优先进入质量区或暂扣库位", "BBD 和供应商批次必须可追溯", "入库后应在库存页确认 SSCC 和库位"],
        "next_action": "先用 入库 > 库位推荐 获取推荐库位，再提交入库单。",
    },
    "出库": {
        "title": "原料/包材出库 SOP",
        "steps": ["出库或包材 > 领用发料：录入 GoodsID、数量和去向", "系统按库位优先级、BBD、SSCC 自动分配", "打印/查看拣货明细", "现场拣货后确认出库，系统扣减库存"],
        "checks": ["欠品单不能确认", "只分配合格库存", "确认后库存和保留量同步变化"],
        "next_action": "先生成出库单，若状态为欠品需补货或改量。",
    },
    "盘点": {
        "title": "盘点与差异调整 SOP",
        "steps": ["盘点 > 日常盘点：扫描或输入 SSCC", "录入实盘数量和原因", "无差异时仓库账号可记录", "有差异且需调整系统库存时仅 admin/supervisor 可执行", "盘点 > 月度/年度盘点 可生成周期盘点清单"],
        "checks": ["差异调整必须写原因", "普通账号不能做系统差异调整", "盘点记录会进入系统日志和库存流水"],
        "next_action": "日常盘点先从 SSCC 录入开始；周期盘点先生成清单。",
    },
    "包材": {
        "title": "包材暂扣/放行 SOP",
        "steps": ["包材 > 入库验收：可直接选择暂扣品质", "暂扣批次保留在库存中但不参与领用分配", "质量复核后在库存或属性变更中放行为合格", "包材 > 领用发料：只会分配合格库存"],
        "checks": ["暂扣原因要写清", "放行前需完成质量/标签/版面复核", "暂扣导致欠品时不能确认领用"],
        "next_action": "先到 包材 > 入库验收 或 库存页进行暂扣/放行操作。",
    },
    "标签": {
        "title": "原料/产品标签 SOP",
        "steps": ["标签 > 原料标签 或 产品标签", "录入批号、生产日期、BBD、数量、库位、SSCC", "系统生成条码/二维码值", "连接打印机打印并记录打印流水"],
        "checks": ["批号和 BBD 必须与实物一致", "SSCC 应能被 RF/扫码识别", "打印记录可导出"],
        "next_action": "进入 标签 模块选择对应模板。",
    },
    "备件": {
        "title": "设备部备品备件 SOP",
        "steps": ["备件 > 基础台账：维护编码、规格、设备、库存阈值", "备件 > 入库验收：记录采购单和验收人", "备件 > 工单领用：必须绑定维修工单", "旧件退库/报废形成流水", "备件盘点可调整库存"],
        "checks": ["食品接触件领用必须清场确认", "关键件/高价值件需要审批人", "领用、退库、报废都要保留工单或原因"],
        "next_action": "先确认备件台账，再按工单领用。",
    },
}


def smart_sop_guide(data: dict) -> dict:
    question = require_text(data, "question")
    mapping = [
        ("成品发货", ("成品", "发货", "波次", "拣货", "复核", "装车")),
        ("入库", ("入库", "收货", "上架", "库位推荐")),
        ("出库", ("出库", "投料", "领用", "发料")),
        ("盘点", ("盘点", "差异", "月度", "年度")),
        ("包材", ("包材", "暂扣", "放行")),
        ("标签", ("标签", "条码", "二维码", "打印")),
        ("备件", ("备件", "工单", "设备", "维修")),
    ]
    topic = next((name for name, words in mapping if any(word in question for word in words)), "成品发货")
    guide = dict(SOP_GUIDES[topic])
    guide["question"] = question
    guide["topic"] = topic
    return guide


def move_stock(conn: sqlite3.Connection, data: dict) -> str:
    sscc = require_text(data, "sscc")
    to_location = require_text(data, "to_location")
    if not fetch_one(conn, "SELECT id FROM locations WHERE id = ?", (to_location,)):
        raise ValueError("目标库位不存在")
    stock = fetch_one(conn, "SELECT * FROM stock_units WHERE sscc = ? AND qty > 0", (sscc,))
    if not stock:
        raise ValueError("SSCC 库存不存在")
    available = float(stock["qty"]) - float(stock["reserved_qty"])
    qty = positive_number(data.get("qty") or available, "移库数量")
    if qty > available + 0.0001:
        raise ValueError("移库数量超过可用库存")
    operator = str(data.get("operator") or data.get("_operator") or "warehouse").strip()
    remark = str(data.get("remark") or "").strip()
    move_id = new_id("MV")
    created_at = now_text()

    if qty >= float(stock["qty"]) - 0.0001 and float(stock["reserved_qty"]) == 0:
        conn.execute(
            "UPDATE stock_units SET location_id = ?, updated_at = ? WHERE sscc = ?",
            (to_location, created_at, sscc),
        )
        moved_sscc = sscc
    else:
        moved_sscc = f"{sscc}-S{datetime.now().strftime('%H%M%S')}"
        remaining = float(stock["qty"]) - qty
        conn.execute(
            "UPDATE stock_units SET qty = ?, updated_at = ? WHERE sscc = ?",
            (remaining, created_at, sscc),
        )
        conn.execute(
            """
            INSERT INTO stock_units(
                sscc, goods_id, owner, location_id, qty, reserved_qty, unit,
                production_date, expiry_date, supplier_batch, po_no, quality_status, updated_at
            ) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                moved_sscc,
                stock["goods_id"],
                stock["owner"],
                to_location,
                qty,
                stock["unit"],
                stock["production_date"],
                stock["expiry_date"],
                stock["supplier_batch"],
                stock["po_no"],
                stock["quality_status"],
                created_at,
            ),
        )

    conn.execute(
        """
        INSERT INTO moves(id, sscc, goods_id, from_location, to_location, qty, status, created_at, operator, remark)
        VALUES (?, ?, ?, ?, ?, ?, '已完成', ?, ?, ?)
        """,
        (move_id, moved_sscc, stock["goods_id"], stock["location_id"], to_location, qty, created_at, operator, remark),
    )
    log_ledger(
        conn,
        "移库",
        move_id,
        moved_sscc,
        stock["goods_id"],
        to_location,
        qty,
        float(stock["qty"]),
        float(stock["qty"]),
        f"{stock['location_id']} -> {to_location}；操作人：{operator}",
    )
    return move_id


def create_count(conn: sqlite3.Connection, data: dict) -> str:
    sscc = require_text(data, "sscc")
    stock = fetch_one(conn, "SELECT * FROM stock_units WHERE sscc = ? AND qty >= 0", (sscc,))
    if not stock:
        raise ValueError("SSCC 库存不存在")
    actual_qty = float(data.get("actual_qty", ""))
    if actual_qty < 0:
        raise ValueError("实盘数量不能小于 0")
    system_qty = float(stock["qty"])
    diff_qty = actual_qty - system_qty
    can_adjust = bool(data.get("_can_adjust"))
    if abs(diff_qty) > 0.0001 and not can_adjust:
        raise PermissionError("系统差异调整需要主管或管理员权限")
    reason = str(data.get("reason") or "盘点差异").strip()
    operator = str(data.get("_operator") or "").strip()
    count_type = str(data.get("count_type") or "日常盘点").strip()
    scope = str(data.get("scope") or stock["goods_id"]).strip()
    if operator:
        reason = f"{reason}；操作人：{operator}"
    count_id = new_id("CK")
    created_at = now_text()
    reserved = min(float(stock["reserved_qty"]), actual_qty)
    new_status = "盘亏清零" if actual_qty == 0 else stock["quality_status"]
    if abs(diff_qty) > 0.0001:
        conn.execute(
            """
            UPDATE stock_units
            SET qty = ?, reserved_qty = ?, quality_status = ?, updated_at = ?
            WHERE sscc = ?
            """,
            (actual_qty, reserved, new_status, created_at, sscc),
        )
    conn.execute(
        """
        INSERT INTO counts(id, sscc, goods_id, location_id, system_qty, actual_qty, diff_qty, status, count_type, scope, operator, adjusted, created_at, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            count_id, sscc, stock["goods_id"], stock["location_id"], system_qty, actual_qty, diff_qty,
            "已调整" if abs(diff_qty) > 0.0001 else "已记录", count_type, scope, operator, 1 if abs(diff_qty) > 0.0001 else 0, created_at, reason,
        ),
    )
    log_ledger(conn, f"{count_type}差异调整" if abs(diff_qty) > 0.0001 else f"{count_type}记录", count_id, sscc, stock["goods_id"], stock["location_id"], diff_qty, system_qty, actual_qty, reason)
    return count_id


def create_cycle_count(conn: sqlite3.Connection, data: dict) -> str:
    count_type = str(data.get("count_type") or "月度盘点").strip()
    if count_type not in {"月度盘点", "年度盘点"}:
        raise ValueError("盘点类型必须是月度盘点或年度盘点")
    scope = str(data.get("scope") or "全仓").strip()
    operator = str(data.get("_operator") or "").strip()
    reason = str(data.get("reason") or count_type).strip()
    filters = ["s.qty > 0"]
    params: list[object] = []
    if scope and scope != "全仓":
        filters.append("(p.category = ? OR l.area = ? OR s.goods_id = ?)")
        params.extend([scope, scope, scope])
    rows = fetch_all(
        conn,
        f"""
        SELECT s.*, p.category, l.area
        FROM stock_units s
        JOIN products p ON p.id = s.goods_id
        JOIN locations l ON l.id = s.location_id
        WHERE {' AND '.join(filters)}
        ORDER BY p.category, l.priority, s.goods_id, s.sscc
        """,
        tuple(params),
    )
    if not rows:
        raise ValueError("没有可生成盘点清单的库存")
    created_at = now_text()
    batch_id = new_id("CC")
    note = f"{reason}；范围：{scope}；批次：{batch_id}"
    if operator:
        note = f"{note}；操作人：{operator}"
    for index, row in enumerate(rows, start=1):
        qty = float(row["qty"])
        conn.execute(
            """
            INSERT INTO counts(id, sscc, goods_id, location_id, system_qty, actual_qty, diff_qty, status, count_type, scope, operator, adjusted, created_at, reason)
            VALUES (?, ?, ?, ?, ?, ?, 0, '已生成', ?, ?, ?, 0, ?, ?)
            """,
            (f"{batch_id}-{index:03d}"[:48], row["sscc"], row["goods_id"], row["location_id"], qty, qty, count_type, scope, operator, created_at, note),
        )
    log_ledger(conn, f"{count_type}清单", batch_id, None, None, None, len(rows), None, None, note)
    return f"{batch_id}（{len(rows)} 条）"


def change_status(conn: sqlite3.Connection, data: dict) -> None:
    sscc = require_text(data, "sscc")
    quality_status = require_text(data, "quality_status")
    reason = str(data.get("reason") or "").strip()
    operator = str(data.get("_operator") or "").strip()
    stock = fetch_one(conn, "SELECT * FROM stock_units WHERE sscc = ?", (sscc,))
    if not stock:
        raise ValueError("SSCC 库存不存在")
    conn.execute(
        "UPDATE stock_units SET quality_status = ?, updated_at = ? WHERE sscc = ?",
        (quality_status, now_text(), sscc),
    )
    status_note = reason or f"{stock['quality_status']} -> {quality_status}"
    if operator:
        status_note = f"{status_note}；操作人：{operator}"
    log_ledger(
        conn,
        "属性变更",
        None,
        sscc,
        stock["goods_id"],
        stock["location_id"],
        stock["qty"],
        stock["qty"],
        stock["qty"],
        status_note,
    )


def add_product(conn: sqlite3.Connection, data: dict) -> None:
    goods_id = require_text(data, "id").upper()
    name = require_text(data, "name")
    category = str(data.get("category") or "原料").strip()
    unit = str(data.get("unit") or "kg").strip()
    raw_min_qty = data.get("min_qty")
    raw_safety_qty = data.get("safety_qty")
    safety_qty = float(raw_safety_qty if raw_safety_qty not in (None, "") else raw_min_qty or 0)
    min_qty = float(raw_min_qty if raw_min_qty not in (None, "") else safety_qty)
    if safety_qty < min_qty:
        safety_qty = min_qty
    expiry_alert_days = int(float(data.get("expiry_alert_days") or 60))
    courbon = 1 if data.get("courbon") else 0
    shelf_days = int(float(data.get("shelf_days") or 0))
    conn.execute(
        """
        INSERT INTO products(id, name, category, unit, min_qty, safety_qty, expiry_alert_days, courbon, shelf_days)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            category = excluded.category,
            unit = excluded.unit,
            min_qty = excluded.min_qty,
            safety_qty = excluded.safety_qty,
            expiry_alert_days = excluded.expiry_alert_days,
            courbon = excluded.courbon,
            shelf_days = excluded.shelf_days
        """,
        (goods_id, name, category, unit, min_qty, safety_qty, expiry_alert_days, courbon, shelf_days),
    )


def add_location(conn: sqlite3.Connection, data: dict) -> None:
    location_id = require_text(data, "id").upper()
    area = require_text(data, "area")
    zone = str(data.get("zone") or area).strip()
    location_type = str(data.get("type") or "正常货位").strip()
    priority = int(float(data.get("priority") or 5))
    capacity = float(data.get("capacity") or 0)
    conn.execute(
        """
        INSERT INTO locations(id, area, zone, type, priority, capacity)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            area = excluded.area,
            zone = excluded.zone,
            type = excluded.type,
            priority = excluded.priority,
            capacity = excluded.capacity
        """,
        (location_id, area, zone, location_type, priority, capacity),
    )


def save_spare_part(conn: sqlite3.Connection, data: dict, seed: bool = False) -> None:
    part_id = require_text(data, "id" if data.get("id") else "part_id").upper()
    existing = fetch_one(conn, "SELECT * FROM spare_parts WHERE id = ?", (part_id,))
    current_qty = float(data.get("current_qty", existing["current_qty"] if existing else 0) or 0)
    payload = {
        "id": part_id,
        "name": require_text(data, "name"),
        "spec": str(data.get("spec") or "").strip(),
        "brand": str(data.get("brand") or "").strip(),
        "category": str(data.get("category") or "机械类").strip(),
        "abc_class": str(data.get("abc_class") or "B").strip().upper()[:1] or "B",
        "unit": str(data.get("unit") or "个").strip(),
        "current_qty": current_qty,
        "min_qty": float(data.get("min_qty") or 0),
        "safety_qty": float(data.get("safety_qty") or 0),
        "max_qty": float(data.get("max_qty") or 0),
        "lead_days": int(float(data.get("lead_days") or 0)),
        "unit_price": float(data.get("unit_price") or 0),
        "supplier": str(data.get("supplier") or "").strip(),
        "location": str(data.get("location") or "").strip().upper(),
        "equipment_name": str(data.get("equipment_name") or "").strip(),
        "equipment_code": str(data.get("equipment_code") or "").strip().upper(),
        "food_contact": 1 if truthy_excel(data.get("food_contact")) else 0,
        "imported": 1 if truthy_excel(data.get("imported")) else 0,
        "critical": 1 if truthy_excel(data.get("critical")) else 0,
        "expiry_date": str(data.get("expiry_date") or "").strip(),
        "remark": str(data.get("remark") or "").strip(),
    }
    now = now_text()
    created_at = now if not existing else existing["created_at"]
    conn.execute(
        """
        INSERT INTO spare_parts(
            id, name, spec, brand, category, abc_class, unit, current_qty,
            min_qty, safety_qty, max_qty, lead_days, unit_price, supplier,
            location, equipment_name, equipment_code, food_contact, imported,
            critical, expiry_date, remark, created_at, updated_at
        ) VALUES (
            :id, :name, :spec, :brand, :category, :abc_class, :unit, :current_qty,
            :min_qty, :safety_qty, :max_qty, :lead_days, :unit_price, :supplier,
            :location, :equipment_name, :equipment_code, :food_contact, :imported,
            :critical, :expiry_date, :remark, :created_at, :updated_at
        )
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            spec = excluded.spec,
            brand = excluded.brand,
            category = excluded.category,
            abc_class = excluded.abc_class,
            unit = excluded.unit,
            current_qty = excluded.current_qty,
            min_qty = excluded.min_qty,
            safety_qty = excluded.safety_qty,
            max_qty = excluded.max_qty,
            lead_days = excluded.lead_days,
            unit_price = excluded.unit_price,
            supplier = excluded.supplier,
            location = excluded.location,
            equipment_name = excluded.equipment_name,
            equipment_code = excluded.equipment_code,
            food_contact = excluded.food_contact,
            imported = excluded.imported,
            critical = excluded.critical,
            expiry_date = excluded.expiry_date,
            remark = excluded.remark,
            updated_at = excluded.updated_at
        """,
        {**payload, "created_at": created_at, "updated_at": now},
    )
    if not seed and existing and abs(float(existing["current_qty"]) - current_qty) > 0.0001:
        log_spare_transaction(
            conn,
            action="主数据校正库存",
            part_id=part_id,
            qty=current_qty - float(existing["current_qty"]),
            before_qty=float(existing["current_qty"]),
            after_qty=current_qty,
            unit_price=payload["unit_price"],
            location=payload["location"],
            note="通过备件主数据维护更新库存",
        )


def spare_status(part: dict) -> tuple[str, str]:
    current = float(part["current_qty"])
    min_qty = float(part["min_qty"])
    safety_qty = float(part["safety_qty"])
    if current <= 0 and (part["critical"] or part["abc_class"] == "A"):
        return "red", "红色：关键备件缺货"
    if current <= min_qty:
        return "orange", "橙色：低于最低库存"
    if current <= safety_qty:
        return "yellow", "黄色：低于安全库存"
    return "ok", "正常"


def spare_parts_with_status(conn: sqlite3.Connection) -> list[dict]:
    rows = fetch_all(conn, "SELECT * FROM spare_parts ORDER BY critical DESC, abc_class, category, id")
    for row in rows:
        status, label = spare_status(row)
        row["stock_status"] = status
        row["stock_status_label"] = label
        row["stock_value"] = round(float(row["current_qty"]) * float(row["unit_price"]), 2)
    return rows


def log_spare_transaction(
    conn: sqlite3.Connection,
    action: str,
    part_id: str,
    qty: float,
    before_qty: float,
    after_qty: float,
    unit_price: float,
    location: str = "",
    ref_no: str = "",
    work_order: str = "",
    equipment_name: str = "",
    equipment_code: str = "",
    reason: str = "",
    requester: str = "",
    approver: str = "",
    keeper: str = "",
    old_part_status: str = "",
    food_clearance: bool = False,
    note: str = "",
) -> str:
    trx_id = new_id("SPT")
    amount = round(abs(qty) * unit_price, 2)
    conn.execute(
        """
        INSERT INTO spare_transactions(
            id, ts, action, part_id, qty, before_qty, after_qty, unit_price,
            amount, location, ref_no, work_order, equipment_name, equipment_code,
            reason, requester, approver, keeper, old_part_status, food_clearance, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            trx_id,
            now_text(),
            action,
            part_id,
            qty,
            before_qty,
            after_qty,
            unit_price,
            amount,
            location,
            ref_no,
            work_order,
            equipment_name,
            equipment_code,
            reason,
            requester,
            approver,
            keeper,
            old_part_status,
            1 if food_clearance else 0,
            note,
        ),
    )
    return trx_id


def spare_part_for_update(conn: sqlite3.Connection, part_id: str) -> dict:
    part = fetch_one(conn, "SELECT * FROM spare_parts WHERE id = ?", (part_id.upper(),))
    if not part:
        raise ValueError("备件不存在")
    return part


def create_spare_receipt(conn: sqlite3.Connection, data: dict) -> str:
    part = spare_part_for_update(conn, require_text(data, "part_id"))
    qty = positive_number(data.get("qty"), "入库数量")
    before_qty = float(part["current_qty"])
    after_qty = before_qty + qty
    location = str(data.get("location") or part["location"] or "").strip().upper()
    supplier = str(data.get("supplier") or part["supplier"] or "").strip()
    unit_price = float(data.get("unit_price") or part["unit_price"] or 0)
    conn.execute(
        "UPDATE spare_parts SET current_qty = ?, location = ?, supplier = ?, unit_price = ?, updated_at = ? WHERE id = ?",
        (after_qty, location, supplier, unit_price, now_text(), part["id"]),
    )
    return log_spare_transaction(
        conn,
        action="备件入库",
        part_id=part["id"],
        qty=qty,
        before_qty=before_qty,
        after_qty=after_qty,
        unit_price=unit_price,
        location=location,
        ref_no=str(data.get("ref_no") or "").strip(),
        reason=str(data.get("reason") or "采购/退回/项目转库存").strip(),
        approver=str(data.get("approver") or "").strip(),
        keeper=str(data.get("keeper") or data.get("_operator") or "").strip(),
        note=str(data.get("note") or data.get("remark") or "外观、型号、数量已验收").strip(),
    )


def create_spare_issue(conn: sqlite3.Connection, data: dict) -> str:
    part = spare_part_for_update(conn, require_text(data, "part_id"))
    qty = positive_number(data.get("qty"), "领用数量")
    work_order = require_text(data, "work_order")
    equipment_name = require_text(data, "equipment_name")
    requester = require_text(data, "requester")
    before_qty = float(part["current_qty"])
    if qty > before_qty + 0.0001:
        raise ValueError("备件库存不足")
    unit_price = float(part["unit_price"] or 0)
    amount = qty * unit_price
    approver = str(data.get("approver") or "").strip()
    if (amount > 500 or part["critical"] or part["abc_class"] == "A") and not approver:
        raise ValueError("高价值或关键备件领用必须填写审批人")
    food_clearance = truthy_excel(data.get("food_clearance"))
    if part["food_contact"] and not food_clearance:
        raise ValueError("食品接触备件领用必须完成维修后清场确认")
    after_qty = before_qty - qty
    conn.execute("UPDATE spare_parts SET current_qty = ?, updated_at = ? WHERE id = ?", (after_qty, now_text(), part["id"]))
    return log_spare_transaction(
        conn,
        action="备件领用",
        part_id=part["id"],
        qty=-qty,
        before_qty=before_qty,
        after_qty=after_qty,
        unit_price=unit_price,
        location=str(part["location"] or ""),
        ref_no=str(data.get("ref_no") or "").strip(),
        work_order=work_order,
        equipment_name=equipment_name,
        equipment_code=str(data.get("equipment_code") or part["equipment_code"] or "").strip().upper(),
        reason=str(data.get("reason") or "故障维修").strip(),
        requester=requester,
        approver=approver,
        keeper=str(data.get("keeper") or data.get("_operator") or "").strip(),
        old_part_status=str(data.get("old_part_status") or "退库/报废/待分析").strip(),
        food_clearance=food_clearance,
        note=str(data.get("note") or data.get("remark") or "").strip(),
    )


def create_spare_return(conn: sqlite3.Connection, data: dict) -> str:
    data = dict(data)
    data.setdefault("reason", "旧件退库/可维修件退回")
    data.setdefault("note", data.get("note") or "旧件已退回待修区或可用库存")
    trx_id = create_spare_receipt(conn, data)
    conn.execute("UPDATE spare_transactions SET action = '备件退库', old_part_status = ? WHERE id = ?", (str(data.get("old_part_status") or "可维修件").strip(), trx_id))
    return trx_id


def create_spare_count(conn: sqlite3.Connection, data: dict) -> str:
    part = spare_part_for_update(conn, require_text(data, "part_id"))
    try:
        actual_qty = float(data.get("actual_qty"))
    except (TypeError, ValueError):
        raise ValueError("实盘数量必须是数字")
    if actual_qty < 0:
        raise ValueError("实盘数量不能小于 0")
    before_qty = float(part["current_qty"])
    diff_qty = actual_qty - before_qty
    conn.execute("UPDATE spare_parts SET current_qty = ?, updated_at = ? WHERE id = ?", (actual_qty, now_text(), part["id"]))
    return log_spare_transaction(
        conn,
        action="备件盘点调整",
        part_id=part["id"],
        qty=diff_qty,
        before_qty=before_qty,
        after_qty=actual_qty,
        unit_price=float(part["unit_price"] or 0),
        location=str(part["location"] or ""),
        reason=str(data.get("reason") or "盘点差异").strip(),
        keeper=str(data.get("keeper") or data.get("_operator") or "").strip(),
        note=str(data.get("note") or "").strip(),
    )


def create_spare_scrap(conn: sqlite3.Connection, data: dict) -> str:
    part = spare_part_for_update(conn, require_text(data, "part_id"))
    qty = positive_number(data.get("qty"), "报废数量")
    before_qty = float(part["current_qty"])
    if qty > before_qty + 0.0001:
        raise ValueError("报废数量超过库存")
    approver = require_text(data, "approver")
    reason = require_text(data, "reason")
    after_qty = before_qty - qty
    conn.execute("UPDATE spare_parts SET current_qty = ?, updated_at = ? WHERE id = ?", (after_qty, now_text(), part["id"]))
    return log_spare_transaction(
        conn,
        action="备件报废",
        part_id=part["id"],
        qty=-qty,
        before_qty=before_qty,
        after_qty=after_qty,
        unit_price=float(part["unit_price"] or 0),
        location=str(part["location"] or ""),
        ref_no=str(data.get("ref_no") or "").strip(),
        reason=reason,
        requester=str(data.get("requester") or "").strip(),
        approver=approver,
        keeper=str(data.get("keeper") or data.get("_operator") or "").strip(),
        old_part_status="报废",
        note=str(data.get("note") or "设备工程师技术确认，财务/负责人按金额审批").strip(),
    )


class WMSHandler(BaseHTTPRequestHandler):
    server_version = "YuWMS/1.0"

    def log_api_event(
        self,
        method: str,
        path: str,
        status_code: int,
        user: dict | None = None,
        action: str = "",
        message: str = "",
        payload: dict | None = None,
    ) -> None:
        try:
            with connect() as conn:
                if user is None:
                    user = user_from_session(conn, self.session_token())
                log_operation(
                    conn,
                    method,
                    path,
                    status_code,
                    user=user,
                    action=action,
                    message=message,
                    payload=payload,
                    ip=self.client_address[0] if self.client_address else "",
                )
        except Exception:
            return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/"):
                self.handle_api_get(parsed.path)
                return
            self.serve_static(parsed.path)
        except ValueError as exc:
            self.log_api_event("GET", parsed.path, 400, action="参数错误", message=str(exc), payload={"query": parsed.query})
            self.send_json({"error": str(exc)}, status=400)
        except PermissionError as exc:
            self.log_api_event("GET", parsed.path, 403, action="权限拒绝", message=str(exc), payload={"query": parsed.query})
            self.send_json({"error": str(exc)}, status=403)
        except Exception as exc:  # noqa: BLE001 - local app should surface failures clearly.
            self.log_api_event("GET", parsed.path, 500, action="服务器错误", message=str(exc), payload={"query": parsed.query})
            self.send_json({"error": f"服务器错误：{exc}"}, status=500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        payload: dict = {}
        user: dict | None = None
        if not parsed.path.startswith("/api/"):
            self.send_error(404)
            return
        try:
            if parsed.path == "/api/import":
                self.handle_import()
                return
            payload = self.read_json()
            with connect() as conn:
                if parsed.path == "/api/login":
                    self.handle_login(conn, payload)
                    return
                if parsed.path == "/api/logout":
                    user = user_from_session(conn, self.session_token())
                    delete_session(conn, self.session_token())
                    log_operation(conn, "POST", parsed.path, 200, user=user, action="退出登录", message="已退出登录", payload=payload, ip=self.client_address[0] if self.client_address else "")
                    self.send_json(
                        {"notice": "已退出登录"},
                        headers={"Set-Cookie": f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"},
                    )
                    return
                user = user_from_session(conn, self.session_token())
                if not user:
                    log_operation(conn, "POST", parsed.path, 401, action="未登录拦截", message="请先登录", payload=payload, ip=self.client_address[0] if self.client_address else "")
                    self.send_json({"error": "请先登录", "auth": {"user": None}}, status=401)
                    return
                result = self.route_post(conn, parsed.path, payload, user)
                if isinstance(result, dict):
                    message = str(result.get("notice") or "操作完成")
                else:
                    message = str(result)
                log_operation(conn, "POST", parsed.path, 200, user=user, action="业务操作", message=message, payload=payload, ip=self.client_address[0] if self.client_address else "")
                data = bootstrap_payload(conn, user)
                if isinstance(result, dict):
                    data.update(result)
                data["notice"] = message
                self.send_json(data)
        except ValueError as exc:
            self.log_api_event("POST", parsed.path, 400, user=user, action="参数错误", message=str(exc), payload=payload)
            self.send_json({"error": str(exc)}, status=400)
        except PermissionError as exc:
            self.log_api_event("POST", parsed.path, 403, user=user, action="权限拒绝", message=str(exc), payload=payload)
            self.send_json({"error": str(exc)}, status=403)
        except Exception as exc:  # noqa: BLE001 - local app should surface failures clearly.
            self.log_api_event("POST", parsed.path, 500, user=user, action="服务器错误", message=str(exc), payload=payload)
            self.send_json({"error": f"服务器错误：{exc}"}, status=500)

    def handle_api_get(self, path: str) -> None:
        if path == "/api/export":
            self.handle_export()
            return
        if path != "/api/bootstrap":
            self.send_json({"error": "接口不存在"}, status=404)
            return
        with connect() as conn:
            user = user_from_session(conn, self.session_token())
            if not user:
                self.send_json({"error": "请先登录", "auth": {"user": None}}, status=401)
                return
            self.send_json(bootstrap_payload(conn, user))

    def handle_export(self) -> None:
        parsed = urlparse(self.path)
        dataset = parse_qs(parsed.query).get("dataset", [""])[0]
        with connect() as conn:
            user = user_from_session(conn, self.session_token())
            if not user:
                log_operation(conn, "GET", "/api/export", 401, action="未登录拦截", message="请先登录", payload={"dataset": dataset}, ip=self.client_address[0] if self.client_address else "")
                self.send_json({"error": "请先登录", "auth": {"user": None}}, status=401)
                return
            require_permission(user, "view")
            if dataset == "operation_logs":
                require_permission(user, "logs")
            title, columns, rows = export_rows(conn, dataset)
            body = make_xlsx(title, columns, rows)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ascii_filename = f"YuWMS_{dataset or 'export'}_{timestamp}.xlsx"
            display_filename = f"YuWMS_{title}_{timestamp}.xlsx"
            self.send_bytes(
                body,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f'attachment; filename="{ascii_filename}"; filename*=UTF-8\'\'{quote(display_filename)}'},
            )
            log_operation(conn, "GET", "/api/export", 200, user=user, action="导出", message=title, payload={"dataset": dataset}, ip=self.client_address[0] if self.client_address else "")

    def handle_import(self) -> None:
        with connect() as conn:
            user = user_from_session(conn, self.session_token())
            if not user:
                log_operation(conn, "POST", "/api/import", 401, action="未登录拦截", message="请先登录", ip=self.client_address[0] if self.client_address else "")
                self.send_json({"error": "请先登录", "auth": {"user": None}}, status=401)
                return
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            import_type = form.getfirst("import_type", "")
            file_item = form["file"] if "file" in form else None
            if file_item is None or not getattr(file_item, "filename", ""):
                raise ValueError("请选择 Excel 或 CSV 文件")
            content = file_item.file.read()
            rows = parse_spreadsheet(file_item.filename, content)
            for row in rows:
                row["_operator"] = f"{user['display_name']}({user['username']})"
            count = import_rows(conn, import_type, rows, user)
            data = bootstrap_payload(conn, user)
            data["notice"] = f"导入完成：{IMPORT_SCHEMAS[import_type]['label']} {count} 行"
            log_operation(conn, "POST", "/api/import", 200, user=user, action="导入", message=data["notice"], payload={"import_type": import_type, "filename": file_item.filename, "rows": count}, ip=self.client_address[0] if self.client_address else "")
            self.send_json(data)

    def handle_login(self, conn: sqlite3.Connection, payload: dict) -> None:
        username = require_text(payload, "username")
        password = require_text(payload, "password")
        user = authenticate_user(conn, username, password)
        if not user:
            log_operation(conn, "POST", "/api/login", 401, action="登录失败", message=f"账号或密码错误：{username}", payload=payload, ip=self.client_address[0] if self.client_address else "")
            self.send_json({"error": "账号或密码错误"}, status=401)
            return
        token = create_session(conn, username)
        data = bootstrap_payload(conn, user)
        data["notice"] = f"登录成功：{user['display_name']}"
        log_operation(conn, "POST", "/api/login", 200, user=user, action="登录", message=data["notice"], payload=payload, ip=self.client_address[0] if self.client_address else "")
        self.send_json(
            data,
            headers={"Set-Cookie": f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_DAYS * 86400}"},
        )

    def route_post(self, conn: sqlite3.Connection, path: str, payload: dict, user: dict) -> str:
        payload = dict(payload)
        payload["_operator"] = f"{user['display_name']}({user['username']})"
        payload["_can_adjust"] = "adjust" in role_permissions(user["role"])
        if path == "/api/inbounds":
            require_permission(user, "inbound")
            return f"入库完成：{create_inbound(conn, payload)}"
        if path == "/api/location-recommendations":
            require_permission(user, "view")
            return {"notice": "库位推荐已生成", "location_recommendations": recommend_locations(conn, payload)}
        if path == "/api/scans":
            require_permission(user, "view")
            return {"notice": "扫描已识别", "scan_result": parse_scan_code(conn, payload)}
        if path == "/api/labels/generate":
            require_permission(user, "view")
            label = generate_label(conn, payload)
            return {"notice": f"标签已生成：{label['id']}", "current_label": label}
        if path == "/api/camera-scans":
            require_permission(user, "view")
            return f"库位建模采集完成：{record_camera_scan(conn, payload)}"
        if path == "/api/outbounds":
            require_permission(user, "outbound")
            outbound_id = create_outbound(conn, payload)
            return f"出库单已生成：{outbound_id}"
        if path == "/api/finished/receive":
            require_permission(user, "finished")
            return f"成品入库完成：{create_finished_receipt(conn, payload)}"
        if path == "/api/finished/ship":
            require_permission(user, "finished")
            outbound_id = create_finished_shipment(conn, payload)
            return f"成品发运单已生成：{outbound_id}"
        if path == "/api/finished/waves":
            require_permission(user, "finished")
            return f"成品拣货波次已创建：{create_finished_wave(conn, payload)}"
        if path == "/api/smart/waves/generate":
            require_permission(user, "finished")
            return f"智能成品波次已创建：{create_smart_finished_wave(conn, payload)}"
        if path == "/api/smart/safety/apply":
            require_permission(user, "masters")
            return f"动态安全库存已应用：{apply_dynamic_safety(conn, payload)}"
        if path == "/api/smart/query":
            require_permission(user, "view")
            return {"notice": "查询助手已回答", "smart_answer": smart_query_answer(conn, payload, user)}
        if path == "/api/smart/sop":
            require_permission(user, "view")
            return {"notice": "SOP助手已生成步骤", "smart_sop": smart_sop_guide(payload)}
        if path.startswith("/api/finished/waves/") and path.endswith("/pick"):
            require_permission(user, "finished")
            wave_id = path.split("/")[4]
            return f"波次拣货已记录：{pick_finished_wave(conn, wave_id, payload)}"
        if path.startswith("/api/finished/waves/") and path.endswith("/review"):
            require_permission(user, "finished")
            wave_id = path.split("/")[4]
            return f"订单复核完成：{review_finished_wave_order(conn, wave_id, payload)}"
        if path.startswith("/api/finished/waves/") and path.endswith("/ship"):
            require_permission(user, "finished")
            wave_id = path.split("/")[4]
            return f"装车发货完成：{ship_finished_wave_order(conn, wave_id, payload)}"
        if path == "/api/tms/shipments":
            require_permission(user, "tms")
            return f"TMS运单已生成：{create_tms_shipment(conn, payload)}"
        if path.startswith("/api/tms/shipments/") and path.endswith("/dispatch"):
            require_permission(user, "tms")
            shipment_id = path.split("/")[4]
            return f"TMS发车完成：{dispatch_tms_shipment(conn, shipment_id, payload)}"
        if path.startswith("/api/tms/shipments/") and path.endswith("/event"):
            require_permission(user, "tms")
            shipment_id = path.split("/")[4]
            return f"TMS事件已记录：{record_tms_event(conn, shipment_id, payload)}"
        if path.startswith("/api/tms/shipments/") and path.endswith("/pod"):
            require_permission(user, "tms")
            shipment_id = path.split("/")[4]
            return f"POD签收已记录：{record_tms_pod(conn, shipment_id, payload)}"
        if path.startswith("/api/tms/shipments/") and path.endswith("/freight"):
            require_permission(user, "tms_settle")
            shipment_id = path.split("/")[4]
            return f"运费对账已处理：{settle_tms_freight(conn, shipment_id, payload)}"
        if path == "/api/tms/iot":
            require_permission(user, "tms")
            return f"IoT遥测已接收：{record_iot_telemetry(conn, payload)}"
        if path.startswith("/api/tms/shipments/") and path.endswith("/driver"):
            require_permission(user, "tms")
            shipment_id = path.split("/")[4]
            return f"司机任务已更新：{update_driver_task(conn, shipment_id, payload)}"
        if path == "/api/integrations/events":
            require_permission(user, "tms_admin")
            return f"接口事件已处理：{process_integration_event(conn, payload)}"
        if path == "/api/audit/packages":
            require_permission(user, "recall")
            return f"审计证据包已生成：{create_audit_package(conn, payload)}"
        if path == "/api/recalls":
            require_permission(user, "recall")
            return f"批次召回已创建：{create_recall_order(conn, payload)}"
        if path == "/api/packaging/receive":
            require_permission(user, "packaging")
            return f"包材入库完成：{create_packaging_receipt(conn, payload)}"
        if path == "/api/packaging/issue":
            require_permission(user, "packaging")
            outbound_id = create_packaging_issue(conn, payload)
            return f"包材领用单已生成：{outbound_id}"
        if path.startswith("/api/outbounds/") and path.endswith("/confirm"):
            outbound_id = path.split("/")[3]
            order = fetch_one(
                conn,
                """
                SELECT p.category
                FROM outbound_orders o
                JOIN products p ON p.id = o.goods_id
                WHERE o.id = ?
                """,
                (outbound_id,),
            )
            confirm_permission = "outbound"
            if order and order["category"] == "成品":
                confirm_permission = "finished"
            elif order and order["category"] == "包材":
                confirm_permission = "packaging"
            require_permission(user, confirm_permission)
            confirm_outbound(conn, outbound_id, payload["_operator"])
            if order and order["category"] == "成品":
                create_tms_shipment(conn, {"outbound_id": outbound_id, "_operator": payload["_operator"]})
            return f"出库确认完成：{outbound_id}"
        if path == "/api/moves":
            require_permission(user, "move")
            return f"移库完成：{move_stock(conn, payload)}"
        if path == "/api/counts":
            require_permission(user, "count")
            return f"盘点调整完成：{create_count(conn, payload)}"
        if path == "/api/cycle-counts":
            require_permission(user, "count")
            return f"周期盘点清单已生成：{create_cycle_count(conn, payload)}"
        if path == "/api/status":
            require_permission(user, "status")
            change_status(conn, payload)
            return "属性已更新"
        if path == "/api/masters/products":
            require_permission(user, "masters")
            add_product(conn, payload)
            return "货品主数据已保存"
        if path == "/api/masters/locations":
            require_permission(user, "masters")
            add_location(conn, payload)
            return "库位主数据已保存"
        if path == "/api/spares/parts":
            require_permission(user, "spares_master")
            save_spare_part(conn, payload)
            return "备件主数据已保存"
        if path == "/api/spares/receive":
            require_permission(user, "spares")
            return f"备件入库完成：{create_spare_receipt(conn, payload)}"
        if path == "/api/spares/issue":
            require_permission(user, "spares")
            return f"备件领用完成：{create_spare_issue(conn, payload)}"
        if path == "/api/spares/return":
            require_permission(user, "spares")
            return f"备件退库完成：{create_spare_return(conn, payload)}"
        if path == "/api/spares/count":
            require_permission(user, "spares")
            return f"备件盘点完成：{create_spare_count(conn, payload)}"
        if path == "/api/spares/scrap":
            require_permission(user, "spares")
            return f"备件报废完成：{create_spare_scrap(conn, payload)}"
        if path == "/api/reset":
            require_permission(user, "reset")
            for table in ("audit_packages", "integration_events", "tms_driver_tasks", "tms_iot_telemetry", "tms_pods", "tms_events", "tms_freight_bills", "tms_shipment_lines", "tms_shipments", "recall_orders", "channel_expiry_rules", "finished_wave_lines", "finished_wave_orders", "finished_waves", "label_prints", "camera_scans", "scan_events", "spare_transactions", "spare_parts", "ledger", "counts", "moves", "outbound_lines", "outbound_orders", "inbound_orders", "stock_units", "locations", "products"):
                conn.execute(f"DELETE FROM {table}")
            seed_demo_data(conn)
            return "演示数据已重置"
        raise ValueError("接口不存在")

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def session_token(self) -> str | None:
        cookie = self.headers.get("Cookie", "")
        for part in cookie.split(";"):
            key, _, value = part.strip().partition("=")
            if key == SESSION_COOKIE:
                return value
        return None

    def send_json(self, payload: dict, status: int = 200, headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body: bytes, content_type: str, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def serve_static(self, raw_path: str) -> None:
        path = unquote(raw_path)
        if path in ("", "/"):
            file_path = STATIC_DIR / "index.html"
        else:
            clean_path = path.lstrip("/")
            file_path = STATIC_DIR / clean_path
        if not file_path.exists() or not file_path.is_file() or not file_path.resolve().is_relative_to(STATIC_DIR):
            file_path = STATIC_DIR / "index.html"
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        try:
            print(f"[{now_text()}] {self.address_string()} {fmt % args}")
        except OSError:
            pass


def main() -> None:
    init_db()
    host = os.environ.get("HOST", "127.0.0.1")
    preferred_port = int(os.environ.get("PORT", "8765"))
    server = None
    for port in range(preferred_port, preferred_port + 20):
        try:
            server = ThreadingHTTPServer((host, port), WMSHandler)
            break
        except OSError as exc:
            if exc.errno not in (48, 98):
                raise
            if port == preferred_port:
                print(f"Port {preferred_port} is already in use; trying the next port...")
    if server is None:
        raise OSError(f"No free port found from {preferred_port} to {preferred_port + 19}")
    actual_host, actual_port = server.server_address
    print(f"YuWMS running at http://{actual_host}:{actual_port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
