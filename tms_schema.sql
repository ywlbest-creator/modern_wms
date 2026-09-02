-- YuWMS / YuTMS complete pet food WMS-TMS extension schema
-- Updated: 2026-06-05
-- Run after the YuWMS core tables when foreign key checks are enabled.

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

CREATE INDEX IF NOT EXISTS idx_tms_shipments_status ON tms_shipments(status);
CREATE INDEX IF NOT EXISTS idx_tms_shipments_carrier ON tms_shipments(carrier_code);
CREATE INDEX IF NOT EXISTS idx_tms_shipments_outbound ON tms_shipments(source_outbound_id);
CREATE INDEX IF NOT EXISTS idx_tms_lines_shipment ON tms_shipment_lines(shipment_id);
CREATE INDEX IF NOT EXISTS idx_tms_lines_goods_lot ON tms_shipment_lines(goods_id, lot_no);
CREATE INDEX IF NOT EXISTS idx_tms_events_shipment ON tms_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_tms_events_type_time ON tms_events(event_type, event_time);
CREATE INDEX IF NOT EXISTS idx_tms_iot_shipment_time ON tms_iot_telemetry(shipment_id, telemetry_time);
CREATE INDEX IF NOT EXISTS idx_tms_iot_risk ON tms_iot_telemetry(risk_level);
CREATE INDEX IF NOT EXISTS idx_tms_driver_status ON tms_driver_tasks(task_status);
CREATE INDEX IF NOT EXISTS idx_integrations_status ON integration_events(status, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_packages_type_ref ON audit_packages(package_type, ref_id);

INSERT OR IGNORE INTO tms_carriers (
    code, name, contact, phone, service_type, cold_chain, active, score, updated_at
) VALUES
    ('TMS-SF', '顺丰冷运/快运', '承运商客服', '95338', '冷链/快运', 1, 1, 96, datetime('now')),
    ('TMS-JD', '京东物流', '承运商客服', '950616', '仓配/快运', 1, 1, 94, datetime('now')),
    ('TMS-LTL', '区域零担承运商', '调度员', '13800000000', '零担', 0, 1, 88, datetime('now'));

INSERT OR IGNORE INTO tms_lanes (
    code, origin, destination, carrier_code, transit_days,
    temp_min, temp_max, base_fee, fee_per_unit, active, updated_at
) VALUES
    ('LANE-SZ-SH-COLD', '苏州工厂', '上海区域', 'TMS-SF', 1, 2, 8, 180, 0.45, 1, datetime('now')),
    ('LANE-SZ-HZ-AMB', '苏州工厂', '杭州区域', 'TMS-JD', 1, NULL, NULL, 150, 0.35, 1, datetime('now')),
    ('LANE-SZ-NATION-LTL', '苏州工厂', '全国零担', 'TMS-LTL', 3, NULL, NULL, 260, 0.28, 1, datetime('now'));
