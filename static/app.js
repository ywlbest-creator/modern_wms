const navItems = [
  { id: "overview", label: "总览", icon: "■" },
  { id: "smart", label: "智能", icon: "※", children: [
    { id: "alerts", label: "预警中心" },
    { id: "query", label: "查询助手" },
    { id: "sop", label: "SOP助手" },
    { id: "waves", label: "智能波次" },
    { id: "safety", label: "安全库存" },
  ] },
  { id: "inbound", label: "入库", icon: "+", children: [
    { id: "receive", label: "收货上架" },
    { id: "recommend", label: "库位推荐" },
    { id: "records", label: "入库记录" },
  ] },
  { id: "outbound", label: "出库", icon: ">", children: [
    { id: "notice", label: "出库通知" },
    { id: "picking", label: "分配拣货" },
    { id: "records", label: "出库记录" },
  ] },
  { id: "packaging", label: "包材", icon: "▣", children: [
    { id: "receive", label: "入库验收" },
    { id: "issue", label: "领用发料" },
    { id: "inventory", label: "库存查询" },
    { id: "warnings", label: "预警提醒" },
    { id: "documents", label: "出入库单" },
  ] },
  { id: "finished", label: "成品", icon: "◆", children: [
    { id: "receive", label: "完工入库" },
    { id: "inventory", label: "成品库存" },
    { id: "ship", label: "发货通知" },
    { id: "wave", label: "波次创建" },
    { id: "picking", label: "合并拣货" },
    { id: "review", label: "订单复核" },
    { id: "loading", label: "装车发货" },
    { id: "records", label: "发货记录" },
    { id: "warnings", label: "预警提醒" },
  ] },
  { id: "tms", label: "TMS运输", icon: "↦", children: [
    { id: "tower", label: "控制塔" },
    { id: "plan", label: "运输计划" },
    { id: "monitor", label: "在途温控" },
    { id: "iot", label: "IoT/GPS" },
    { id: "pod", label: "POD/运费" },
    { id: "driver", label: "司机协同" },
    { id: "interfaces", label: "外部接口" },
    { id: "recall", label: "召回追溯" },
    { id: "performance", label: "承运商绩效" },
    { id: "audit", label: "审计包" },
    { id: "master", label: "承运商线路" },
  ] },
  { id: "spares", label: "备件", icon: "◇", children: [
    { id: "warnings", label: "库存预警" },
    { id: "receive", label: "入库验收" },
    { id: "issue", label: "工单领用" },
    { id: "returns", label: "退库报废" },
    { id: "count", label: "盘点调整" },
    { id: "master", label: "基础台账" },
    { id: "transactions", label: "出入库流水" },
  ] },
  { id: "rf", label: "RF/扫码", icon: "⌁", children: [
    { id: "scan", label: "RF枪扫描" },
    { id: "camera", label: "摄像头扫码" },
    { id: "records", label: "扫描记录" },
  ] },
  { id: "labels", label: "标签", icon: "▥", children: [
    { id: "raw", label: "原料标签" },
    { id: "product", label: "产品标签" },
    { id: "records", label: "打印记录" },
  ] },
  { id: "inventory", label: "库存", icon: "#" },
  { id: "model", label: "三维库位", icon: "▤", children: [
    { id: "overview", label: "三维总览" },
    { id: "locations", label: "库位明细" },
    { id: "capture", label: "摄像头采集" },
    { id: "records", label: "采集记录" },
  ] },
  { id: "move", label: "移库", icon: "⇄" },
  { id: "count", label: "盘点", icon: "✓", children: [
    { id: "daily", label: "日常盘点" },
    { id: "cycle", label: "月度/年度盘点" },
    { id: "records", label: "盘点记录" },
  ] },
  { id: "masters", label: "主数据", icon: "◎" },
  { id: "excel", label: "Excel", icon: "⇩" },
  { id: "ledger", label: "流水", icon: "≡" },
  { id: "logs", label: "日志", icon: "☰" },
];

const pageTitles = {
  overview: "总览",
  smart: "智能中心",
  inbound: "入库上架",
  outbound: "出库分配",
  packaging: "包材 WMS",
  finished: "成品 WMS",
  tms: "TMS 运输执行",
  spares: "设备部备品备件",
  rf: "RF 枪 / 二维码扫描",
  labels: "原料 / 产品标签打印",
  inventory: "库存查询",
  model: "仓库三维库位模型",
  move: "手持移库",
  count: "盘点调整",
  masters: "主数据",
  excel: "Excel 导入导出",
  ledger: "库存流水",
  logs: "系统操作日志",
};

const app = {
  page: "overview",
  sections: {
    smart: "alerts",
    inbound: "receive",
    outbound: "notice",
    packaging: "receive",
    finished: "inventory",
    tms: "tower",
    spares: "warnings",
    count: "daily",
    rf: "scan",
    labels: "raw",
    model: "overview",
  },
  expandedNav: {},
  data: null,
  search: "",
  qrStream: null,
  qrTimer: null,
  modelStream: null,
};

const pagePermissions = {
  overview: "view",
  smart: "view",
  inbound: "inbound",
  outbound: "outbound",
  packaging: "packaging",
  finished: "finished",
  tms: "tms",
  spares: "spares",
  rf: "view",
  labels: "view",
  inventory: "view",
  model: "view",
  move: "move",
  count: "count",
  masters: "masters",
  excel: "view",
  ledger: "view",
  logs: "logs",
};

const excelExportItems = [
  { dataset: "inventory", label: "库存明细" },
  { dataset: "finished_inventory", label: "成品库存" },
  { dataset: "packaging_inventory", label: "包材库存" },
  { dataset: "packaging_warnings", label: "包材库存预警" },
  { dataset: "products", label: "货品主数据" },
  { dataset: "locations", label: "库位主数据" },
  { dataset: "inbounds", label: "入库单" },
  { dataset: "outbounds", label: "出库单" },
  { dataset: "ledger", label: "库存流水" },
  { dataset: "operation_logs", label: "系统操作日志", permission: "logs" },
  { dataset: "label_prints", label: "标签打印记录" },
  { dataset: "stock_warnings", label: "安全库存预警" },
  { dataset: "expiry_warnings", label: "临期提醒" },
  { dataset: "spare_parts", label: "备件基础台账" },
  { dataset: "spare_transactions", label: "备件出入库流水" },
  { dataset: "spare_warnings", label: "备件库存预警" },
  { dataset: "tms_shipments", label: "TMS运输单", permission: "tms" },
  { dataset: "tms_events", label: "TMS在途/温控事件", permission: "tms" },
  { dataset: "tms_pods", label: "TMS签收POD", permission: "tms" },
  { dataset: "tms_freight_bills", label: "TMS运费账单", permission: "tms_settle" },
  { dataset: "tms_performance", label: "TMS承运商绩效", permission: "tms" },
  { dataset: "tms_iot_telemetry", label: "TMS IoT/GPS温控遥测", permission: "tms" },
  { dataset: "tms_driver_tasks", label: "TMS司机任务", permission: "tms" },
  { dataset: "integration_events", label: "外部系统接口日志", permission: "tms_admin" },
  { dataset: "audit_packages", label: "审计证据包", permission: "recall" },
  { dataset: "channel_expiry_rules", label: "渠道效期规则", permission: "tms" },
  { dataset: "recalls", label: "批次召回记录", permission: "recall" },
];

const excelImportItems = [
  { type: "products", dataset: "template_products", label: "货品主数据", permission: "masters" },
  { type: "locations", dataset: "template_locations", label: "库位主数据", permission: "masters" },
  { type: "inbounds", dataset: "template_inbounds", label: "入库批量导入", permission: "inbound" },
  { type: "outbounds", dataset: "template_outbounds", label: "出库批量导入", permission: "outbound" },
  { type: "finished_receipts", dataset: "template_finished_receipts", label: "成品完工入库", permission: "finished" },
  { type: "finished_shipments", dataset: "template_finished_shipments", label: "成品客户发运", permission: "finished" },
  { type: "packaging_receipts", dataset: "template_packaging_receipts", label: "包材入库", permission: "packaging" },
  { type: "packaging_issues", dataset: "template_packaging_issues", label: "包材领用", permission: "packaging" },
  { type: "spare_parts", dataset: "template_spare_parts", label: "备件基础台账", permission: "spares_master" },
  { type: "spare_receipts", dataset: "template_spare_receipts", label: "备件入库", permission: "spares" },
  { type: "spare_issues", dataset: "template_spare_issues", label: "备件领用", permission: "spares" },
];

const appShell = document.querySelector("#appShell");
const loginScreen = document.querySelector("#loginScreen");
const loginForm = document.querySelector("#loginForm");
const loginError = document.querySelector("#loginError");
const navEl = document.querySelector("#nav");
const kpisEl = document.querySelector("#kpis");
const contentEl = document.querySelector("#content");
const noticeEl = document.querySelector("#notice");
const pageTitleEl = document.querySelector("#pageTitle");
const searchEl = document.querySelector("#globalSearch");
const userBadge = document.querySelector("#userBadge");
const logoutBtn = document.querySelector("#logoutBtn");

searchEl.addEventListener("input", (event) => {
  app.search = event.target.value.trim().toLowerCase();
  render();
});

document.querySelector("#resetDemo").addEventListener("click", async () => {
  if (!hasPerm("reset")) {
    showNotice("当前账号没有重置演示数据权限", true);
    return;
  }
  if (!confirm("重置后会清空当前演示账套，确定继续？")) return;
  await postJSON("/api/reset", {});
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.hidden = true;
  const payload = Object.fromEntries(new FormData(loginForm).entries());
  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    showLogin(data.error || "登录失败");
    return;
  }
  app.data = data;
  loginForm.reset();
  showApp();
  render();
  showNotice(data.notice || "登录成功");
});

logoutBtn.addEventListener("click", async () => {
  await fetch("/api/logout", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  app.data = null;
  showLogin("已退出登录");
});

async function loadData() {
  const response = await fetch("/api/bootstrap");
  const data = await response.json();
  if (!response.ok) {
    showLogin(data.error || "请先登录");
    return;
  }
  app.data = data;
  showApp();
  render();
}

async function postJSON(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (response.status === 401) {
    app.data = null;
    showLogin(data.error || "请先登录");
    return null;
  }
  if (!response.ok) {
    showNotice(data.error || "操作失败", true);
    return null;
  }
  app.data = data;
  render();
  showNotice(data.notice || "操作完成");
  return data;
}

function showLogin(errorText = "") {
  appShell.hidden = true;
  loginScreen.hidden = false;
  if (errorText) {
    loginError.hidden = false;
    loginError.textContent = errorText;
  } else {
    loginError.hidden = true;
  }
}

function showApp() {
  loginScreen.hidden = true;
  appShell.hidden = false;
}

function currentUser() {
  return app.data?.auth?.user || null;
}

function hasPerm(permission) {
  const user = currentUser();
  return !!user && user.permissions.includes(permission);
}

function canOpenPage(page) {
  return hasPerm(pagePermissions[page] || "view");
}

function navItem(page) {
  return navItems.find((item) => item.id === page);
}

function activeSection(page = app.page) {
  const item = navItem(page);
  if (!item?.children?.length) return "";
  const saved = app.sections[page] || item.children[0].id;
  return item.children.some((child) => child.id === saved) ? saved : item.children[0].id;
}

function sectionLabel(page = app.page, section = activeSection(page)) {
  const item = navItem(page);
  return item?.children?.find((child) => child.id === section)?.label || "";
}

function currentPageTitle() {
  const child = sectionLabel();
  return child ? `${pageTitles[app.page]} / ${child}` : pageTitles[app.page];
}

function showNotice(text, danger = false) {
  noticeEl.hidden = false;
  noticeEl.textContent = text;
  noticeEl.style.borderColor = danger ? "#f7b6ad" : "#b7e0ce";
  noticeEl.style.background = danger ? "#fff0ee" : "#f0faf5";
  noticeEl.style.color = danger ? "var(--red)" : "var(--green)";
  clearTimeout(showNotice.timer);
  showNotice.timer = setTimeout(() => {
    noticeEl.hidden = true;
  }, 3800);
}

function render() {
  if (!app.data) return;
  if (!canOpenPage(app.page)) {
    app.page = "overview";
  }
  const currentNavItem = navItem(app.page);
  if (currentNavItem?.children?.length && !(app.page in app.expandedNav)) {
    app.expandedNav[app.page] = true;
  }
  const user = currentUser();
  userBadge.hidden = !user;
  logoutBtn.hidden = !user;
  if (user) {
    userBadge.textContent = `${user.display_name} / ${user.role_label}`;
  }
  document.querySelector("#resetDemo").hidden = !hasPerm("reset");
  renderNav();
  renderKpis();
  pageTitleEl.textContent = currentPageTitle();
  const renderer = {
    overview: renderOverview,
    smart: renderSmart,
    inbound: renderInbound,
    outbound: renderOutbound,
    packaging: renderPackaging,
    finished: renderFinished,
    tms: renderTMS,
    spares: renderSpares,
    rf: renderRFScanner,
    labels: renderLabels,
    inventory: renderInventory,
    model: renderWarehouseModel,
    move: renderMove,
    count: renderCount,
    masters: renderMasters,
    excel: renderExcel,
    ledger: renderLedger,
    logs: renderOperationLogs,
  }[app.page];
  contentEl.innerHTML = renderer();
  bindPageEvents();
}

function renderNav() {
  const badges = {
    inbound: app.data.inbounds.length,
    outbound: app.data.stats.open_outbound_count,
    packaging: (app.data.stats.packaging_issue_count || 0) + (app.data.stats.packaging_hold_count || 0) + (app.data.stats.packaging_stock_warning_count || 0),
    finished: app.data.stats.finished_shipping_count,
    tms: (app.data.stats.tms_active_count || 0) + (app.data.stats.tms_exception_count || 0),
    spares: app.data.stats.spare_warning_count,
    inventory: (app.data.stats.stock_warning_count || 0) + (app.data.stats.expiring_count || 0),
    count: app.data.stats.expiring_count,
    smart: app.data.stats.smart_risk_count || 0,
  };
  navEl.innerHTML = navItems
    .filter((item) => canOpenPage(item.id))
    .map((item) => {
      const isActive = item.id === app.page;
      const hasChildren = !!item.children?.length;
      const isExpanded = hasChildren && !!app.expandedNav[item.id];
      const badge = badges[item.id] !== undefined ? `<span class="badge">${badges[item.id]}</span>` : "";
      const childRows = isExpanded ? `
        <div class="nav-children">
          ${item.children.map((child) => `
            <button class="nav-child ${activeSection(item.id) === child.id ? "active" : ""}" data-page="${item.id}" data-section="${child.id}" type="button">
              <span aria-hidden="true">·</span>
              <span class="nav-label">${escapeHTML(child.label)}</span>
            </button>
          `).join("")}
        </div>
      ` : "";
      return `
      <button class="${isActive ? "active" : ""}" data-page="${item.id}" ${hasChildren ? `data-parent="true" aria-expanded="${isExpanded}"` : ""} type="button">
        <span aria-hidden="true">${item.icon}</span>
        <span class="nav-label">${item.label}</span>
        ${badge || hasChildren ? `<span class="nav-meta">${badge}${hasChildren ? `<span class="nav-caret" aria-hidden="true">${isExpanded ? "▾" : "▸"}</span>` : ""}</span>` : ""}
      </button>
      ${childRows}
    `;
    })
    .join("");
  navEl.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      const page = button.dataset.page;
      const item = navItem(page);
      if (button.dataset.section) {
        app.page = page;
        app.sections[page] = button.dataset.section;
        app.expandedNav[page] = true;
      } else if (item?.children?.length) {
        const willExpand = !app.expandedNav[page];
        Object.keys(app.expandedNav).forEach((key) => {
          app.expandedNav[key] = false;
        });
        app.expandedNav[page] = willExpand;
        app.page = page;
        if (!app.sections[page]) {
          app.sections[page] = activeSection(page);
        }
      } else {
        app.page = page;
      }
      render();
    });
  });
}

function renderKpis() {
  const stats = app.data.stats;
  const items = app.page === "smart" ? [
    ["智能风险", stats.smart_risk_count || 0, "库存/临期/欠品/质量"],
    ["高风险", stats.smart_high_risk_count || 0, "需要优先处理"],
    ["波次建议", stats.smart_wave_suggestion_count || 0, "可自动组波"],
    ["安全库存建议", stats.smart_safety_adjust_count || 0, "建议调整项"],
    ["欠品单", stats.shortage_count || 0, "需补货或改量"],
    ["临期提醒", stats.expiring_count || 0, "按批次和 BBD"],
  ] : app.page === "spares" ? [
    ["备件 SKU", stats.spare_sku_count, "设备部台账"],
    ["库存金额", fmt(stats.spare_stock_value), "按最近单价估算"],
    ["预警项", stats.spare_warning_count, "低于安全/最低库存"],
    ["关键缺货", stats.spare_critical_shortage_count, "A类/关键件红色预警"],
    ["食品接触", stats.spare_food_contact_count, "需合格证明和清场"],
    ["领用金额", fmt(stats.spare_issue_amount), "最近流水累计"],
  ] : app.page === "packaging" ? [
    ["包材 SKU", stats.packaging_sku_count || 0, "包材主数据"],
    ["包材批次", stats.packaging_pallet_count || 0, "当前在库"],
    ["包材在库", fmt(stats.packaging_on_hand_qty || 0), "标准单位合计"],
    ["安全预警", stats.packaging_stock_warning_count || 0, "低于安全/最低库存"],
    ["暂扣批次", stats.packaging_hold_count || 0, "不参与领用分配"],
    ["待领用", stats.packaging_issue_count || 0, "已分配/欠品"],
  ] : app.page === "finished" ? [
    ["成品 SKU", stats.finished_sku_count, "成品主数据"],
    ["成品托盘", stats.finished_pallet_count, "当前在库"],
    ["成品在库", fmt(stats.finished_on_hand_qty), "包装/袋合计"],
    ["安全预警", stats.finished_stock_warning_count || 0, "低于安全/最低库存"],
    ["临期提醒", stats.finished_expiring_count, "按 SKU 设置天数"],
    ["待发运", stats.finished_shipping_count, "已分配/欠品"],
  ] : app.page === "tms" ? [
    ["运输单", stats.tms_shipment_count || 0, "WMS发货联动"],
    ["在途/待发", stats.tms_active_count || 0, "待发车/在途"],
    ["运输异常", stats.tms_exception_count || 0, "温控/POD异常"],
    ["待POD", stats.tms_pending_pod_count || 0, "需签收回单"],
    ["IoT高风险", stats.tms_iot_high_risk_count || 0, "温控/开门"],
    ["接口待办", stats.integration_pending_count || 0, "失败/待处理"],
  ] : app.page === "rf" ? [
    ["扫码记录", stats.rf_scan_count || 0, "RF/二维码"],
    ["库存批次", stats.pallet_count, "可识别 SSCC"],
    ["库位数", app.data.locations.length, "可识别库位码"],
    ["安全预警", stats.stock_warning_count || 0, "扫描后联动查询"],
    ["临期提醒", stats.expiring_count, "按 SSCC 追溯"],
    ["欠品单", stats.shortage_count, "可扫码复核"],
  ] : app.page === "labels" ? [
    ["标签记录", stats.label_print_count || 0, "生成流水"],
    ["原料 SKU", app.data.products.filter((item) => item.category !== "成品").length, "原料/包材/返工料"],
    ["产品 SKU", app.data.products.filter((item) => item.category === "成品").length, "成品标签"],
    ["库存批次", stats.pallet_count, "可带 SSCC"],
    ["库位数", app.data.locations.length, "可打印库位"],
    ["临期提醒", stats.expiring_count, "标签带 BBD"],
  ] : app.page === "model" ? [
    ["库位数", app.data.locations.length, "主数据"],
    ["已采集", stats.modeled_location_count || 0, "摄像头记录"],
    ["采集记录", stats.camera_scan_count || 0, "建模样本"],
    ["高占用", (app.data.location_model || []).filter((item) => item.model_status === "高占用").length, ">=90%"],
    ["空闲库位", (app.data.location_model || []).filter((item) => item.model_status === "空闲").length, "<=20%"],
    ["需复核", (app.data.location_model || []).filter((item) => item.model_status === "需复核").length, "冻结/隔离/待检"],
  ] : [
    ["SKU", stats.sku_count, "货品主数据"],
    ["托盘/批次", stats.pallet_count, "当前在库"],
    ["在库数量", fmt(stats.on_hand_qty), "标准单位合计"],
    ["安全预警", stats.stock_warning_count || 0, "低于安全/最低库存"],
    ["临期提醒", stats.expiring_count, "按货品设置天数"],
    ["欠品单", stats.shortage_count, "需补货或改量"],
  ];
  kpisEl.innerHTML = items
    .map(([label, value, hint]) => `
      <div class="kpi">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
        <div class="hint">${hint}</div>
      </div>
    `)
    .join("");
}

function renderOverview() {
  const lowRows = app.data.stock_warnings.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td class="num">${fmt(item.available)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.safety_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.reorder_qty)} ${escapeHTML(item.unit)}</td>
      <td>${stockStatusPill(item)}</td>
    </tr>
  `).join("");

  const expiryRows = app.data.expiry_warnings.slice(0, 8).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${expiryDatePill(item)}</td>
      <td class="num">${fmt(item.days_left)}</td>
      <td>${expiryStatusPill(item)}</td>
    </tr>
  `).join("");

  const summaryRows = app.data.product_summary.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td class="num">${fmt(item.on_hand)}</td>
      <td class="num">${fmt(item.reserved)}</td>
      <td class="num">${fmt(item.available)}</td>
      <td>${item.courbon ? pill("MES", "info") : pill("本地", "")}</td>
    </tr>
  `).join("");

  const analysis = app.data.source_analysis.map((item) => `
    <div class="analysis-item">
      <strong>${escapeHTML(item.module)}</strong>
      <div>
        <p>${escapeHTML(item.kept)}</p>
        <small>${escapeHTML(item.old_clues)}</small>
      </div>
    </div>
  `).join("");

  return `
    <div class="grid-2">
      <section class="panel">
        <div class="panel-head"><h2>旧资料拆解</h2></div>
        <div class="analysis-list">${analysis}</div>
      </section>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>货品库存汇总</h2></div>
        ${table(["货品", "名称", "类别", "在库", "保留", "可用", "接口"], summaryRows)}
      </section>
    </div>
    <div class="grid-2">
      <section class="table-wrap">
        <div class="panel-head panel">
          <h2>安全库存预警</h2>
          ${hasPerm("masters") ? `<button class="secondary" data-jump="masters" type="button"><span aria-hidden="true">◎</span>设置阈值</button>` : ""}
        </div>
        ${table(["货品", "名称", "可用", "最低库存", "安全库存", "建议补足", "状态"], lowRows || emptyRow(7))}
      </section>
      <section class="table-wrap">
        <div class="panel-head panel">
          <h2>临期提醒</h2>
          <div class="actions"><button class="secondary" data-jump="inventory" type="button"><span aria-hidden="true">#</span>查看库存</button></div>
        </div>
        ${table(["SSCC", "货品", "名称", "库位", "BBD", "剩余天数", "状态"], expiryRows || emptyRow(7))}
      </section>
    </div>
  `;
}

function renderSmart() {
  const smart = app.data.smart || { alerts: [], wave_suggestions: [], safety_recommendations: [] };
  const alerts = smart.alerts || [];
  const waveSuggestions = smart.wave_suggestions || [];
  const safetyRecommendations = smart.safety_recommendations || [];
  const smartAnswer = app.data.smart_answer || null;
  const smartSop = app.data.smart_sop || null;
  const alertRows = filterRows(alerts).map((item) => `
    <tr>
      <td>${smartSeverityPill(item.severity)}</td>
      <td>${pill(item.type, item.severity === "高" ? "bad" : item.severity === "中" ? "warn" : "info")}</td>
      <td class="mono">${escapeHTML(item.target)}</td>
      <td>
        <strong>${escapeHTML(item.title)}</strong>
        <small>${escapeHTML(item.detail)}</small>
      </td>
      <td>${escapeHTML(item.action)}</td>
    </tr>
  `).join("");
  const waveRows = filterRows(waveSuggestions).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.dock)}</td>
      <td>${escapeHTML(item.route)}</td>
      <td class="num">${fmt(item.order_count)}</td>
      <td class="num">${fmt(item.sku_count)}</td>
      <td class="num">${fmt(item.total_qty)}</td>
      <td>${escapeHTML(item.customers || "-")}</td>
      <td>${escapeHTML(item.reason)}</td>
      <td>
        ${hasPerm("finished") ? `<button class="primary" data-generate-smart-wave="${escapeAttr(item.dock)}" data-route="${escapeAttr(item.route)}" type="button"><span aria-hidden="true">+</span>生成</button>` : ""}
      </td>
    </tr>
  `).join("");
  const safetyRows = filterRows(safetyRecommendations).map((item) => `
    <tr>
      <td>${safetyActionPill(item.action)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td class="num">${fmt(item.available)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.current_safety_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.suggested_safety_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.diff_qty)} ${escapeHTML(item.unit)}</td>
      <td>${pill(item.confidence, item.confidence === "高" ? "ok" : item.confidence === "中" ? "info" : "warn")}</td>
      <td>${escapeHTML(item.basis)}</td>
      <td>
        ${hasPerm("masters") && item.action !== "保持" ? `<button class="secondary" data-apply-safety="${escapeAttr(item.goods_id)}" data-safety="${escapeAttr(item.suggested_safety_qty)}" type="button"><span aria-hidden="true">◎</span>应用</button>` : ""}
      </td>
    </tr>
  `).join("");

  const section = activeSection("smart");
  if (section === "query") return `
    <div class="grid-2">
      <form class="form-panel" id="smartQueryForm">
        <div class="panel-head"><h2>自然语言查询助手</h2></div>
        <div class="form-grid one">
          ${textAreaField("question", "你想查询什么", "例如：FG-DOG-ADULT-10KG 还有多少？哪些批次临期？有没有暂扣？成品发货到哪一步？")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">※</span>查询</button>
        </div>
      </form>
      ${renderSmartAnswer(smartAnswer)}
    </div>
  `;
  if (section === "sop") return `
    <div class="grid-2">
      <form class="form-panel" id="smartSopForm">
        <div class="panel-head"><h2>智能 SOP 助手</h2></div>
        <div class="form-grid one">
          ${textAreaField("question", "你要做哪个操作", "例如：成品发货怎么做？包材暂扣怎么放行？盘点差异怎么处理？备件领用需要什么？")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">✓</span>生成步骤</button>
        </div>
      </form>
      ${renderSmartSop(smartSop)}
    </div>
  `;
  if (section === "waves") return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>智能波次建议</h2>
        <small>按同月台、同线路、同 SKU 聚合，减少重复拣货</small>
      </div>
      ${table(["月台", "线路", "订单数", "SKU数", "总数量", "客户", "推荐理由", "操作"], waveRows || emptyRow(8))}
    </section>
  `;
  if (section === "safety") return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>动态安全库存建议</h2>
        <small>按近 30 天出库、供应周期和安全缓冲计算；无历史时沿用当前设置</small>
      </div>
      ${table(["建议", "GoodsID", "名称", "类别", "可用", "当前安全", "建议安全", "差异", "置信度", "计算依据", "操作"], safetyRows || emptyRow(11))}
    </section>
  `;
  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>智能预警中心</h2>
        <div class="actions">
          <button class="secondary" data-jump="inventory" type="button"><span aria-hidden="true">#</span>库存</button>
          <button class="secondary" data-page-jump="smart" data-section-jump="waves" type="button"><span aria-hidden="true">※</span>看波次建议</button>
        </div>
      </div>
      ${table(["风险", "类型", "对象", "问题", "建议动作"], alertRows || emptyRow(5))}
    </section>
  `;
}

function renderSmartAnswer(answer) {
  if (!answer) {
    return `
      <section class="panel">
        <div class="panel-head"><h2>查询结果</h2></div>
        <p class="muted-text">提交问题后，这里会显示基于当前 WMS 数据的受控回答。</p>
      </section>
    `;
  }
  const rows = (answer.rows || []).map((row) => {
    const object = row.sscc || row.id || row.outbound_id || row.goods_id || row.part_id || row.target || "";
    const name = row.goods_name || row.name || row.status || row.stock_status_label || row.expiry_status_label || "";
    const place = row.location_id || row.bin_no || row.destination || row.dock || row.staging_location || "";
    const qty = row.available_qty ?? row.available ?? row.qty ?? row.shortage_qty ?? row.diff_qty ?? "";
    const note = row.quality_status || row.expiry_status_label || row.basis || row.reason || row.remark || "";
    return `
      <tr>
        <td class="mono">${escapeHTML(object)}</td>
        <td>${escapeHTML(name)}</td>
        <td>${escapeHTML(place)}</td>
        <td class="num">${fmt(qty)} ${escapeHTML(row.unit || "")}</td>
        <td>${escapeHTML(note)}</td>
      </tr>
    `;
  }).join("");
  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>${escapeHTML(answer.intent || "查询结果")}</h2>
        <small>${escapeHTML(answer.question || "")}</small>
      </div>
      <div class="panel" style="box-shadow:none;border-left:0;border-right:0;border-radius:0">
        <p>${escapeHTML(answer.answer || "")}</p>
      </div>
      ${table(["对象", "名称/状态", "库位/去向", "数量", "备注"], rows || emptyRow(5))}
    </section>
  `;
}

function renderSmartSop(guide) {
  if (!guide) {
    return `
      <section class="panel">
        <div class="panel-head"><h2>SOP 步骤</h2></div>
        <p class="muted-text">输入操作场景后，这里会给出对应步骤、检查点和下一步入口。</p>
      </section>
    `;
  }
  const stepRows = (guide.steps || []).map((step, index) => `
    <tr>
      <td class="num">${index + 1}</td>
      <td>${escapeHTML(step)}</td>
    </tr>
  `).join("");
  const checkRows = (guide.checks || []).map((check) => `
    <tr>
      <td>${pill("检查", "info")}</td>
      <td>${escapeHTML(check)}</td>
    </tr>
  `).join("");
  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>${escapeHTML(guide.title || "SOP 步骤")}</h2>
        <small>${escapeHTML(guide.question || "")}</small>
      </div>
      ${table(["步骤", "操作"], stepRows || emptyRow(2))}
      <div class="panel" style="margin-top:12px">
        <h3>关键检查</h3>
        ${table(["类型", "检查项"], checkRows || emptyRow(2))}
        <p><strong>下一步：</strong>${escapeHTML(guide.next_action || "")}</p>
      </div>
    </section>
  `;
}

function renderInbound() {
  const rows = filterRows(app.data.inbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${pill(item.status, "ok")}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.received_qty)} ${escapeHTML(item.unit)}</td>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${escapeHTML(item.expiry_date || "")}</td>
      <td>${escapeHTML(item.created_at)}</td>
    </tr>
  `).join("");
  const recommendations = (app.data.location_recommendations || []).map((item) => `
    <div class="mini-row recommendation-row">
      <div>
        <strong class="mono">${escapeHTML(item.id)}</strong>
        <small>${escapeHTML(item.area)} / ${escapeHTML(item.zone)} / ${escapeHTML(item.reason || "")}</small>
      </div>
      <div class="num">
        ${fmt(item.score)}
        <button class="ghost compact-btn" data-apply-location="${escapeAttr(item.id)}" type="button">应用</button>
      </div>
    </div>
  `).join("");

  const inventoryRows = app.data.inventory.slice(0, 10).map(stockMiniRow).join("");
  const section = activeSection("inbound");
  if (section === "recommend") return `
    <div class="grid-2">
      <section class="rf-panel">
        <div class="panel-head"><h2>库位推荐</h2></div>
        <form id="locationRecommendForm" class="form-grid one">
          ${selectField("goods_id", "货品", productOptions())}
          ${numberField("qty", "数量", "1000")}
          ${selectField("quality_status", "品质", qualityOptions("合格"))}
          <div class="actions">
            <button class="secondary" type="submit"><span aria-hidden="true">◎</span>推荐库位</button>
          </div>
        </form>
        <div class="mini-list recommend-list">
          ${recommendations || `<div class="empty compact">暂无推荐</div>`}
        </div>
      </section>
      <section class="rf-panel">
        <div class="panel-head"><h2>SSCC 当前在库</h2></div>
        <div class="mini-list">${inventoryRows}</div>
      </section>
    </div>
  `;
  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>入库记录</h2></div>
      ${table(["入库单", "状态", "货品", "名称", "数量", "SSCC", "库位", "BBD", "时间"], rows || emptyRow(9))}
    </section>
  `;
  return `
    <div class="grid-2">
      <form class="form-panel" id="inboundForm">
        <div class="panel-head"><h2>入库通知 / 收货 / 上架</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "货品", productOptions())}
          ${numberField("qty", "数量", "1000")}
          ${textField("supplier", "供应商/来源", "现场收货")}
          ${textField("supplier_batch", "供应商批次", "BATCH-001")}
          ${dateField("production_date", "生产日期")}
          ${dateField("expiry_date", "BBD/过期日期")}
          ${textField("po_no", "PO/单号", "PO260603")}
          ${selectField("location_id", "上架库位", locationOptions())}
          ${selectField("quality_status", "品质", qualityOptions("合格"))}
          ${textField("owner", "货主", "MARS-RMR")}
          ${textAreaField("remark", "备注", "外观、标签、质检报告已核对")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>入库上架</button>
        </div>
      </form>
      <section class="rf-panel">
        <div class="panel-head"><h2>SSCC 当前在库</h2></div>
        <div class="mini-list">${inventoryRows}</div>
      </section>
    </div>
  `;
}

function renderOutbound() {
  const rows = filterRows(app.data.outbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${statusPill(item.status)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.allocated_qty)}</td>
      <td class="num">${fmt(item.shortage_qty)}</td>
      <td>${escapeHTML(item.destination)}</td>
      <td>${item.courbon_connected ? pill("连接", "ok") : pill("断开", "warn")}</td>
      <td class="actions">
        <button class="ghost" data-print="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">□</span>分拣单</button>
        ${item.status === "已分配" && hasPerm("outbound") ? `<button class="primary" data-confirm="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">✓</span>确认</button>` : ""}
      </td>
    </tr>
    ${item.lines.length ? `<tr><td colspan="10">${allocationLines(item.lines)}</td></tr>` : ""}
  `).join("");

  const availableRows = app.data.inventory.filter((item) => item.quality_status === "合格").slice(0, 10).map(stockMiniRow).join("");
  const section = activeSection("outbound");
  if (section === "picking") return `
    <div class="grid-2">
      <section class="panel">
        <div class="panel-head"><h2>可用库存</h2></div>
        <div class="mini-list">${availableRows}</div>
      </section>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>分配拣货</h2></div>
        ${table(["出库单", "状态", "货品", "名称", "需求", "分配", "欠品", "去向", "MES", "操作"], rows || emptyRow(10))}
      </section>
    </div>
  `;
  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>出库记录</h2></div>
      ${table(["出库单", "状态", "货品", "名称", "需求", "分配", "欠品", "去向", "MES", "操作"], rows || emptyRow(10))}
    </section>
  `;
  return `
    <div class="grid-2">
      <form class="form-panel" id="outboundForm">
        <div class="panel-head"><h2>出库通知 / FIFO 分配</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "货品", productOptions())}
          ${numberField("qty", "需求数量", "500")}
          ${selectField("destination", "领用去向", `
            <option>粉碎投料</option>
            <option>膨化投料</option>
            <option>包装返工</option>
            <option>出口出库</option>
            <option>退货出库</option>
          `)}
          ${textField("bin_no", "料仓号", "BIN-01")}
          <label class="field full toggle">
            <input name="courbon_connected" type="checkbox" checked>
            MES连接
          </label>
          ${textAreaField("remark", "备注", "按 BBD 先后和 SSCC 顺序分配")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">></span>生成并分配</button>
        </div>
      </form>
      <section class="panel">
        <div class="panel-head"><h2>可用库存</h2></div>
        <div class="mini-list">${availableRows}</div>
      </section>
    </div>
  `;
}

function renderPackaging() {
  const packaging = app.data.packaging || { inventory: [], inbounds: [], outbounds: [], low_stock: [], expiry_warnings: [] };
  const inventoryRows = filterRows(packaging.inventory).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.reserved_qty)}</td>
      <td class="num">${fmt(item.available_qty)}</td>
      <td>${qualityPill(item.quality_status)}</td>
      <td>${escapeHTML(item.supplier_batch || "")}</td>
      <td class="actions">
        ${hasPerm("status") ? `<button class="ghost" data-hold="${escapeHTML(item.sscc)}" type="button">暂扣</button>` : ""}
        ${hasPerm("status") ? `<button class="secondary" data-release="${escapeHTML(item.sscc)}" type="button">放行</button>` : ""}
      </td>
    </tr>
  `).join("");
  const lowRows = packaging.low_stock.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td class="num">${fmt(item.available)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)}</td>
      <td class="num">${fmt(item.safety_qty)}</td>
      <td class="num">${fmt(item.reorder_qty)}</td>
      <td>${stockStatusPill(item)}</td>
    </tr>
  `).join("");
  const expiryRows = packaging.expiry_warnings.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${expiryDatePill(item)}</td>
      <td class="num">${fmt(item.days_left)}</td>
      <td>${expiryStatusPill(item)}</td>
    </tr>
  `).join("");
  const inboundRows = filterRows(packaging.inbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.received_qty)} ${escapeHTML(item.unit)}</td>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${escapeHTML(item.supplier || "")}</td>
      <td>${escapeHTML(item.created_at)}</td>
    </tr>
  `).join("");
  const outboundRows = filterRows(packaging.outbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${statusPill(item.status)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.allocated_qty)}</td>
      <td class="num">${fmt(item.shortage_qty)}</td>
      <td>${escapeHTML(item.destination)}</td>
      <td class="mono">${escapeHTML(item.bin_no || "")}</td>
      <td class="actions">
        <button class="ghost" data-print="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">□</span>领用单</button>
        ${item.status === "已分配" && hasPerm("packaging") ? `<button class="primary" data-confirm="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">✓</span>确认领用</button>` : ""}
      </td>
    </tr>
    ${item.lines.length ? `<tr><td colspan="10">${allocationLines(item.lines)}</td></tr>` : ""}
  `).join("");

  const section = activeSection("packaging");
  if (section === "receive") return `
      <form class="form-panel" id="packagingReceiveForm">
        <div class="panel-head"><h2>包材入库 / 验收</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "包材", productOptions("包材"))}
          ${numberField("qty", "入库数量", "1000")}
          ${textField("supplier", "供应商/来源", "包材供应商")}
          ${textField("supplier_batch", "供应商批次", "PKG-BATCH-001")}
          ${dateField("production_date", "生产日期")}
          ${dateField("expiry_date", "BBD/过期日期")}
          ${textField("po_no", "采购单号", "PO-PKG-001")}
          ${selectField("location_id", "包材库位", locationOptions("包材仓"))}
          ${selectField("quality_status", "品质", qualityOptions("合格"))}
          ${textAreaField("remark", "备注", "外观、印刷、条码、尺寸、数量已核对")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>包材入库</button>
        </div>
      </form>
    `;
  if (section === "issue") return `
      <form class="form-panel" id="packagingIssueForm">
        <div class="panel-head"><h2>包材领用 / 发料</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "包材", productOptions("包材"))}
          ${numberField("qty", "领用数量", "2000")}
          ${selectField("destination", "领用去向", `
            <option>包装一线领用</option>
            <option>包装二线领用</option>
            <option>返工换包</option>
            <option>试产打样</option>
            <option>报废处理</option>
          `)}
          ${textField("bin_no", "包装线/月台", "PK-LINE-01")}
          ${textAreaField("remark", "备注", "按生产工单发料，暂扣/待检库存不参与分配")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">></span>生成领用单</button>
        </div>
      </form>
    `;
  if (section === "warnings") return `
    <div class="grid-2">
      <section class="table-wrap">
        <div class="panel-head panel">
          <h2>包材安全库存</h2>
          <div class="actions"><button class="secondary" data-export="packaging_warnings" type="button"><span aria-hidden="true">⇩</span>导出预警</button></div>
        </div>
        ${table(["包材", "名称", "可用", "最低", "安全", "建议补足", "状态"], lowRows || emptyRow(7))}
      </section>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>包材临期提醒</h2></div>
        ${table(["SSCC", "包材", "名称", "库位", "BBD", "剩余天数", "状态"], expiryRows || emptyRow(7))}
      </section>
    </div>
  `;
  if (section === "inventory") return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>包材库存</h2>
        <div class="actions"><button class="secondary" data-export="packaging_inventory" type="button"><span aria-hidden="true">⇩</span>导出库存</button></div>
      </div>
      ${table(["SSCC", "包材", "名称", "库位", "在库", "保留", "可用", "品质", "批次", "操作"], inventoryRows || emptyRow(10))}
    </section>
  `;
  return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>包材领用单</h2></div>
      ${table(["领用单", "状态", "包材", "名称", "需求", "分配", "欠品", "去向", "包装线", "操作"], outboundRows || emptyRow(10))}
    </section>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>最近包材入库</h2></div>
      ${table(["入库单", "包材", "名称", "数量", "SSCC", "库位", "供应商", "时间"], inboundRows || emptyRow(8))}
    </section>
  `;
}

function renderFinished() {
  const finished = app.data.finished || { inventory: [], inbounds: [], outbounds: [], low_stock: [], summary: [] };
  const inventoryRows = filterRows(finished.inventory).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.reserved_qty)}</td>
      <td class="num">${fmt(item.available_qty)}</td>
      <td>${qualityPill(item.quality_status)}</td>
      <td>${expiryDatePill(item)}</td>
    </tr>
  `).join("");
  const outboundRows = filterRows(finished.outbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${statusPill(item.status)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.allocated_qty)}</td>
      <td class="num">${fmt(item.shortage_qty)}</td>
      <td>${escapeHTML(item.destination)}</td>
      <td class="mono">${escapeHTML(item.bin_no || "")}</td>
      <td class="actions">
        <button class="ghost" data-print="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">□</span>拣货单</button>
        ${item.status === "已分配" && hasPerm("finished") ? `<button class="primary" data-confirm="${escapeHTML(item.id)}" type="button"><span aria-hidden="true">✓</span>装车确认</button>` : ""}
      </td>
    </tr>
    ${item.lines.length ? `<tr><td colspan="10">${allocationLines(item.lines)}</td></tr>` : ""}
  `).join("");
  const inboundRows = filterRows(finished.inbounds).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.received_qty)} ${escapeHTML(item.unit)}</td>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${escapeHTML(item.supplier || "")}</td>
      <td>${escapeHTML(item.created_at)}</td>
    </tr>
  `).join("");
  const lowRows = finished.low_stock.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td class="num">${fmt(item.available)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.safety_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.reorder_qty)} ${escapeHTML(item.unit)}</td>
      <td>${stockStatusPill(item)}</td>
    </tr>
  `).join("");
  const expiryRows = (finished.expiry_warnings || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td>${expiryDatePill(item)}</td>
      <td class="num">${fmt(item.days_left)}</td>
      <td>${expiryStatusPill(item)}</td>
    </tr>
  `).join("");
  const waves = finished.waves || [];
  const pendingWaveOrders = finished.outbounds.filter((item) => item.status === "已分配").map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td>${escapeHTML(item.destination)}</td>
      <td class="mono">${escapeHTML(item.bin_no || "")}</td>
      <td>${statusPill(item.status)}</td>
    </tr>
  `).join("");
  const waveRows = waves.map((wave) => `
    <tr>
      <td class="mono">${escapeHTML(wave.id)}</td>
      <td>${statusPill(wave.status)}</td>
      <td>${escapeHTML(wave.ship_date || "")}</td>
      <td class="mono">${escapeHTML(wave.dock || "")}</td>
      <td>${escapeHTML(wave.route || "")}</td>
      <td class="num">${fmt(wave.orders?.length || 0)}</td>
      <td class="num">${fmt(wave.lines?.length || 0)}</td>
      <td>${escapeHTML(wave.created_by || "")}</td>
    </tr>
  `).join("");
  const pickRows = waves.flatMap((wave) => (wave.lines || []).map((line) => `
    <tr>
      <td class="mono">${escapeHTML(wave.id)}</td>
      <td>${statusPill(line.status)}</td>
      <td class="mono">${escapeHTML(line.location_id)}</td>
      <td class="mono">${escapeHTML(line.sscc)}</td>
      <td class="mono">${escapeHTML(line.goods_id)}</td>
      <td>${escapeHTML(line.goods_name)}</td>
      <td class="num">${fmt(line.total_qty)} ${escapeHTML(line.unit || "")}</td>
      <td class="num">${fmt(line.picked_qty)}</td>
      <td>${(line.orders || []).map((order) => `<span class="mono">${escapeHTML(order.outbound_id)}:${fmt(order.qty)}</span>`).join("<br>")}</td>
    </tr>
  `)).join("");
  const waveOrderRows = waves.flatMap((wave) => (wave.orders || []).map((order) => `
    <tr>
      <td class="mono">${escapeHTML(wave.id)}</td>
      <td>${statusPill(order.status)}</td>
      <td class="mono">${escapeHTML(order.outbound_id)}</td>
      <td>${escapeHTML(order.destination || "")}</td>
      <td class="mono">${escapeHTML(order.goods_id)}</td>
      <td class="num">${fmt(order.qty)} ${escapeHTML(order.unit || "")}</td>
      <td class="mono">${escapeHTML(order.staging_location || "")}</td>
      <td>${escapeHTML(order.reviewer || order.picker || "")}</td>
      <td class="mono">${escapeHTML(order.truck_no || "")}</td>
      <td class="mono">${escapeHTML(order.seal_no || "")}</td>
    </tr>
  `)).join("");

  const section = activeSection("finished");
  if (section === "receive") return `
      <form class="form-panel" id="finishedReceiveForm">
        <div class="panel-head"><h2>成品完工入库</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "成品 SKU", productOptions("成品"))}
          ${numberField("qty", "完工数量", "240")}
          ${textField("production_line", "产线/班组", "包装一线")}
          ${textField("supplier_batch", "生产批次", "FG-BATCH-001")}
          ${dateField("production_date", "生产日期")}
          ${dateField("expiry_date", "BBD/过期日期")}
          ${textField("po_no", "生产工单", "MO260603-01")}
          ${selectField("location_id", "成品库位", locationOptions("成品仓"))}
          ${selectField("quality_status", "品质", qualityOptions("合格"))}
          ${textAreaField("remark", "备注", "外箱、码垛、SSCC 标签已核对")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>完工入库</button>
        </div>
      </form>
  `;
  if (section === "ship") return `
      <form class="form-panel" id="finishedShipForm">
        <div class="panel-head"><h2>发货通知</h2></div>
        <div class="form-grid">
          ${selectField("goods_id", "成品 SKU", productOptions("成品"))}
          ${numberField("qty", "发运数量", "120")}
          ${textField("customer", "客户/渠道", "华东经销商")}
          ${selectField("channel_code", "渠道编码", channelOptions())}
          ${textField("order_no", "销售订单", "SO260603-01")}
          ${textField("ship_dock", "月台/装车口", "DOCK-FG-01")}
          ${textAreaField("remark", "备注", "按 BBD 先后分配，装车前复核客户订单")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">></span>生成发运单</button>
        </div>
      </form>
  `;
  if (section === "wave") return `
    <div class="grid-2">
      <form class="form-panel" id="finishedWaveForm">
        <div class="panel-head"><h2>波次创建</h2></div>
        <div class="form-grid one">
          ${dateField("ship_date", "计划发货日期")}
          ${textField("dock", "月台", "DOCK-FG-01")}
          ${textField("route", "线路/区域", "华东线")}
          ${textAreaField("order_ids", "合并订单", "留空自动选择全部已分配成品发货单；或粘贴多个发货单号，用逗号/换行分隔")}
          ${textAreaField("remark", "备注", "同线路/同月台订单合并拣货")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>创建波次</button>
        </div>
      </form>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>可加入波次订单</h2></div>
        ${table(["发货单", "SKU", "名称", "需求", "客户", "月台", "状态"], pendingWaveOrders || emptyRow(7))}
      </section>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>波次列表</h2></div>
      ${table(["波次", "状态", "发货日期", "月台", "线路", "订单数", "拣货行", "创建人"], waveRows || emptyRow(8))}
    </section>
  `;
  if (section === "picking") return `
    <div class="grid-2">
      <form class="rf-panel" id="finishedWavePickForm">
        <div class="panel-head"><h2>合并拣货</h2></div>
        <div class="form-grid one">
          ${selectField("wave_id", "波次", finishedWaveOptions(waves, ["已创建", "拣货中", "已拣货", "复核中"]))}
          <label class="field">扫描 SSCC
            <input class="scan-input" name="sscc" placeholder="FGSSCC202606020001" autofocus>
          </label>
          ${numberField("qty", "拣货数量", "留空则拣完当前 SSCC")}
          ${textField("picker", "拣货人", "FG-RF-01")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">✓</span>确认拣货</button>
        </div>
      </form>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>合并拣货行</h2></div>
        ${table(["波次", "状态", "库位", "SSCC", "SKU", "名称", "总拣", "已拣", "订单拆分"], pickRows || emptyRow(9))}
      </section>
    </div>
  `;
  if (section === "review") return `
    <div class="grid-2">
      <form class="form-panel" id="finishedWaveReviewForm">
        <div class="panel-head"><h2>订单复核</h2></div>
        <div class="form-grid one">
          ${selectField("wave_id", "波次", finishedWaveOptions(waves, ["已拣货", "复核中"]))}
          ${selectField("outbound_id", "发货单", finishedWaveOrderOptions(waves, ["已拣货"]))}
          ${textField("staging_location", "复核暂存位", "STAGE-01")}
          ${textField("reviewer", "复核人", "复核员")}
          ${textAreaField("remark", "复核备注", "订单、SKU、数量、SSCC一致")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">✓</span>复核完成</button>
        </div>
      </form>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>订单复核状态</h2></div>
        ${table(["波次", "状态", "发货单", "客户", "SKU", "数量", "暂存位", "人员", "车牌", "封签"], waveOrderRows || emptyRow(10))}
      </section>
    </div>
  `;
  if (section === "loading") return `
    <div class="grid-2">
      <form class="form-panel" id="finishedWaveShipForm">
        <div class="panel-head"><h2>装车发货</h2></div>
        <div class="form-grid one">
          ${selectField("wave_id", "波次", finishedWaveOptions(waves, ["复核中", "已拣货"]))}
          ${selectField("outbound_id", "发货单", finishedWaveOrderOptions(waves, ["已复核"]))}
          ${textField("dock", "月台", "DOCK-FG-01")}
          ${textField("truck_no", "车牌", "苏E12345")}
          ${textField("driver", "司机", "司机")}
          ${textField("seal_no", "封签号", "SEAL-001")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">></span>确认发货</button>
        </div>
      </form>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>装车队列</h2></div>
        ${table(["波次", "状态", "发货单", "客户", "SKU", "数量", "暂存位", "人员", "车牌", "封签"], waveOrderRows || emptyRow(10))}
      </section>
    </div>
  `;
  if (section === "inventory") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>成品库存</h2></div>
      ${table(["SSCC", "SKU", "名称", "库位", "在库", "保留", "可用", "品质", "BBD"], inventoryRows || emptyRow(9))}
    </section>
  `;
  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>成品发货波次</h2></div>
      ${table(["波次", "状态", "发货日期", "月台", "线路", "订单数", "拣货行", "创建人"], waveRows || emptyRow(8))}
    </section>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>成品发货单</h2></div>
      ${table(["发运单", "状态", "SKU", "名称", "需求", "分配", "欠品", "客户", "月台", "操作"], outboundRows || emptyRow(10))}
    </section>
  `;
  if (section === "warnings") return `
    <div class="grid-2">
      <section class="table-wrap">
        <div class="panel-head panel"><h2>成品安全库存</h2></div>
        ${table(["SKU", "名称", "可用", "最低库存", "安全库存", "建议补足", "状态"], lowRows || emptyRow(7))}
      </section>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>成品临期提醒</h2>
        <div class="actions"><button class="secondary" data-export="expiry_warnings" type="button"><span aria-hidden="true">⇩</span>导出临期</button></div>
      </div>
      ${table(["SSCC", "SKU", "名称", "库位", "BBD", "剩余天数", "状态"], expiryRows || emptyRow(7))}
    </section>
  `;
  return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>成品发运单</h2></div>
      ${table(["发运单", "状态", "SKU", "名称", "需求", "分配", "欠品", "客户", "月台", "操作"], outboundRows || emptyRow(10))}
    </section>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>最近成品入库</h2></div>
      ${table(["入库单", "SKU", "名称", "数量", "SSCC", "库位", "来源", "时间"], inboundRows || emptyRow(8))}
    </section>
  `;
}

function renderTMS() {
  const tms = app.data.tms || {
    shipments: [],
    carriers: [],
    lanes: [],
    events: [],
    pods: [],
    freight_bills: [],
    telemetry: [],
    driver_tasks: [],
    integrations: [],
    audit_packages: [],
    performance: [],
    channel_rules: [],
    control_tower: { risks: [] },
    recalls: [],
  };
  const shipments = filterRows(tms.shipments || []);
  const shipmentRows = shipments.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${statusPill(item.status)}</td>
      <td class="mono">${escapeHTML(item.source_outbound_id || "-")}</td>
      <td>${escapeHTML(item.carrier_name || item.carrier_code)}</td>
      <td>${escapeHTML(item.customer || "-")}</td>
      <td>${escapeHTML(item.channel_code || "-")}</td>
      <td class="num">${item.min_remaining_days ? `${fmt(item.min_remaining_days)}天` : "-"}</td>
      <td>${escapeHTML(item.destination || "-")}</td>
      <td>${escapeHTML(item.vehicle_no || "-")}</td>
      <td>${item.temp_min !== null && item.temp_min !== undefined ? `${fmt(item.temp_min)}-${fmt(item.temp_max)}℃` : "常温"}</td>
      <td>${item.exception_flag ? pill(item.exception_note || "异常", "bad") : "-"}</td>
    </tr>
  `).join("");
  const eventRows = (tms.events || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.shipment_id)}</td>
      <td>${escapeHTML(item.event_time)}</td>
      <td>${escapeHTML(item.event_type)}</td>
      <td>${escapeHTML(item.location_text || "-")}</td>
      <td class="num">${item.temperature === null || item.temperature === undefined ? "-" : fmt(item.temperature)}</td>
      <td>${smartSeverityPill(item.risk_level || "低")}</td>
      <td>${escapeHTML(item.note || "-")}</td>
    </tr>
  `).join("");
  const podRows = (tms.pods || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.shipment_id)}</td>
      <td>${escapeHTML(item.signed_by)}</td>
      <td>${escapeHTML(item.signed_at)}</td>
      <td class="num">${fmt(item.received_qty)}</td>
      <td class="num">${fmt(item.damaged_qty)}</td>
      <td class="num">${fmt(item.shortage_qty)}</td>
      <td>${escapeHTML(item.note || "-")}</td>
    </tr>
  `).join("");
  const freightRows = (tms.freight_bills || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.shipment_id)}</td>
      <td class="mono">${escapeHTML(item.carrier_code || "-")}</td>
      <td class="num">${fmt(item.estimated_fee)}</td>
      <td class="num">${fmt(item.actual_fee)}</td>
      <td class="num">${fmt(item.difference)}</td>
      <td>${statusPill(item.billing_status)}</td>
      <td>${escapeHTML(item.exception_reason || "-")}</td>
    </tr>
  `).join("");
  const carrierRows = (tms.carriers || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.code)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.service_type)}</td>
      <td>${item.cold_chain ? pill("冷链", "info") : pill("常温", "")}</td>
      <td class="num">${fmt(item.score)}</td>
    </tr>
  `).join("");
  const laneRows = (tms.lanes || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.code)}</td>
      <td>${escapeHTML(item.origin)}</td>
      <td>${escapeHTML(item.destination)}</td>
      <td class="mono">${escapeHTML(item.carrier_code)}</td>
      <td>${item.temp_min !== null && item.temp_min !== undefined ? `${fmt(item.temp_min)}-${fmt(item.temp_max)}℃` : "常温"}</td>
      <td class="num">${fmt(item.base_fee)}</td>
      <td class="num">${fmt(item.fee_per_unit)}</td>
    </tr>
  `).join("");
  const performanceRows = (tms.performance || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.carrier_code)}</td>
      <td>${escapeHTML(item.carrier_name)}</td>
      <td class="num">${fmt(item.shipment_count)}</td>
      <td class="num">${fmt(item.otif_rate)}%</td>
      <td class="num">${fmt(item.pod_rate)}%</td>
      <td class="num">${fmt(item.temperature_exception_rate)}%</td>
      <td class="num">${fmt(item.fee_variance_rate)}%</td>
      <td>${pill(fmt(item.score), item.score < 80 ? "warn" : "ok")}</td>
    </tr>
  `).join("");
  const channelRuleRows = (tms.channel_rules || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.channel_code)}</td>
      <td>${escapeHTML(item.channel_name)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name || "-")}</td>
      <td class="num">${fmt(item.min_remaining_days)} 天</td>
      <td>${item.allow_near_expiry ? pill("允许", "warn") : pill("拦截", "info")}</td>
    </tr>
  `).join("");
  const recallRows = (tms.recalls || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.supplier_batch)}</td>
      <td>${escapeHTML(item.reason || "-")}</td>
      <td class="num">${fmt(item.affected_inventory)}</td>
      <td class="num">${fmt(item.affected_shipments)}</td>
      <td>${statusPill(item.status)}</td>
    </tr>
  `).join("");
  const tower = tms.control_tower || { risks: [] };
  const towerRiskRows = (tower.risks || []).map((item) => `
    <tr>
      <td>${smartSeverityPill(item.severity)}</td>
      <td>${escapeHTML(item.type || "-")}</td>
      <td class="mono">${escapeHTML(item.ref_id || "-")}</td>
      <td>${escapeHTML(item.message || "-")}</td>
    </tr>
  `).join("");
  const telemetryRows = (tms.telemetry || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.shipment_id)}</td>
      <td>${escapeHTML(item.telemetry_time || "")}</td>
      <td class="mono">${escapeHTML(item.device_id || "")}</td>
      <td>${escapeHTML(item.location_text || "-")}</td>
      <td class="num">${item.temperature === null || item.temperature === undefined ? "-" : fmt(item.temperature)}</td>
      <td class="num">${item.humidity === null || item.humidity === undefined ? "-" : fmt(item.humidity)}</td>
      <td>${item.door_open ? pill("开门", "bad") : pill("关闭", "ok")}</td>
      <td>${escapeHTML(item.reefer_status || "-")}</td>
      <td>${smartSeverityPill(item.risk_level || "低")}</td>
    </tr>
  `).join("");
  const driverRows = (tms.driver_tasks || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.shipment_id)}</td>
      <td>${escapeHTML(item.driver || "-")}</td>
      <td>${escapeHTML(item.driver_phone || "-")}</td>
      <td>${escapeHTML(item.vehicle_no || "-")}</td>
      <td>${statusPill(item.task_status)}</td>
      <td>${escapeHTML(item.pickup_location || "-")}</td>
      <td>${escapeHTML(item.delivery_location || "-")}</td>
      <td class="mono">${escapeHTML(item.pin_code || "-")}</td>
    </tr>
  `).join("");
  const integrationRows = (tms.integrations || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.created_at || "")}</td>
      <td>${escapeHTML(item.system_name || "-")}</td>
      <td>${pill(item.direction || "-", "info")}</td>
      <td>${escapeHTML(item.event_type || "-")}</td>
      <td class="mono">${escapeHTML(item.object_id || "-")}</td>
      <td>${statusPill(item.status)}</td>
      <td>${escapeHTML(item.message || "-")}</td>
    </tr>
  `).join("");
  const auditRows = (tms.audit_packages || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.package_type || "-")}</td>
      <td class="mono">${escapeHTML(item.ref_id || "-")}</td>
      <td>${escapeHTML(item.title || "-")}</td>
      <td>${statusPill(item.status)}</td>
      <td>${escapeHTML(item.summary || "-")}</td>
      <td>${escapeHTML(item.created_at || "")}</td>
    </tr>
  `).join("");

  const section = activeSection("tms");
  if (section === "tower") return `
    <div class="kpis compact">
      <div class="kpi"><span class="label">活跃运输</span><strong class="value">${fmt(tower.active_shipments || 0)}</strong><span class="hint">待发/在途/异常</span></div>
      <div class="kpi"><span class="label">运输异常</span><strong class="value">${fmt(tower.exception_shipments || 0)}</strong><span class="hint">温控/POD/延误</span></div>
      <div class="kpi"><span class="label">IoT高风险</span><strong class="value">${fmt(tower.high_risk_telemetry || 0)}</strong><span class="hint">温度/开门</span></div>
      <div class="kpi"><span class="label">司机待办</span><strong class="value">${fmt(tower.pending_driver_tasks || 0)}</strong><span class="hint">接单/发车/签收</span></div>
      <div class="kpi"><span class="label">接口待办</span><strong class="value">${fmt(tower.pending_integrations || 0)}</strong><span class="hint">失败/待处理</span></div>
      <div class="kpi"><span class="label">运费差异</span><strong class="value">${fmt(tower.freight_diff || 0)}</strong><span class="hint">需财务复核</span></div>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>风险队列</h2></div>
      ${table(["级别", "类型", "对象", "说明"], towerRiskRows || emptyRow(4))}
    </section>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>运输单总览</h2></div>
      ${table(["运单", "状态", "WMS发货单", "承运商", "客户", "渠道", "最小效期", "目的地", "车牌", "温区", "异常"], shipmentRows || emptyRow(11))}
    </section>
  `;
  if (section === "iot") return `
    <form class="form-panel" id="tmsIotForm">
      <div class="panel-head"><h2>IoT/GPS温控上报</h2></div>
      <div class="form-grid">
        ${selectField("shipment_id", "运单", tmsShipmentOptions(tms.shipments))}
        ${textField("device_id", "设备号", "IOT-TEMP-001")}
        ${textField("location_text", "位置", "高速服务区 / 客户园区")}
        ${numberField("latitude", "纬度", "31.2304")}
        ${numberField("longitude", "经度", "121.4737")}
        ${numberField("temperature", "温度", "6")}
        ${numberField("humidity", "湿度", "60")}
        ${numberField("speed", "速度", "72")}
        ${textField("reefer_status", "冷机状态", "运行")}
        <label class="field toggle"><input name="door_open" type="checkbox">车厢开门</label>
        ${textAreaField("note", "备注", "设备自动上报")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="primary" type="submit"><span aria-hidden="true">+</span>接收遥测</button>
        <button class="secondary" data-export="tms_iot_telemetry" type="button"><span aria-hidden="true">⇩</span>导出遥测</button>
      </div>
    </form>
    <section class="table-wrap">
      ${table(["运单", "时间", "设备", "位置", "温度", "湿度", "开门", "冷机", "风险"], telemetryRows || emptyRow(9))}
    </section>
  `;
  if (section === "driver") return `
    <div class="grid-2">
      <form class="form-panel" id="driverTaskForm">
        <div class="panel-head"><h2>司机/承运商任务</h2></div>
        <div class="form-grid one">
          ${selectField("shipment_id", "运单", tmsShipmentOptions(tms.shipments))}
          ${selectField("action", "动作", `
            <option>已接单</option>
            <option>已发车</option>
            <option>到达待签收</option>
            <option>已签收</option>
          `)}
          ${textField("signed_by", "签收人", "客户仓管")}
          ${numberField("received_qty", "实收数量", "0")}
          ${numberField("damaged_qty", "破损", "0")}
          ${numberField("shortage_qty", "短少", "0")}
          ${textAreaField("pod_note", "回单备注", "司机端回传")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">✓</span>更新任务</button>
        </div>
      </form>
      <section class="panel">
        <div class="panel-head"><h2>任务状态</h2></div>
        <div class="mini-list">
          ${(tms.driver_tasks || []).slice(0, 6).map((item) => `
            <div class="mini-row">
              <div><strong class="mono">${escapeHTML(item.shipment_id)}</strong><small>${escapeHTML(item.driver || "-")} / ${escapeHTML(item.vehicle_no || "-")}</small></div>
              <div>${statusPill(item.task_status)}</div>
            </div>
          `).join("") || `<div class="empty compact">暂无司机任务</div>`}
        </div>
      </section>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>司机任务明细</h2>
        <button class="secondary" data-export="tms_driver_tasks" type="button"><span aria-hidden="true">⇩</span>导出司机任务</button>
      </div>
      ${table(["任务", "运单", "司机", "电话", "车牌", "状态", "提货点", "送达点", "签收码"], driverRows || emptyRow(9))}
    </section>
  `;
  if (section === "interfaces") return `
    <form class="form-panel" id="integrationEventForm">
      <div class="panel-head"><h2>外部系统接口事件</h2></div>
      <div class="form-grid">
        ${selectField("system_name", "系统", `<option>OMS</option><option>ERP</option><option>MES</option><option>QMS</option><option>承运商平台</option><option>IoT平台</option>`)}
        ${selectField("event_type", "事件", `
          <option>OMS订单导入</option>
          <option>ERP运费回传</option>
          <option>MES放行</option>
          <option>QMS冻结</option>
          <option>QMS召回</option>
          <option>承运商状态回传</option>
          <option>IoT遥测</option>
        `)}
        ${selectField("shipment_id", "TMS运单", tmsShipmentOptions(tms.shipments))}
        ${textField("sscc", "SSCC", "SSCC...")}
        ${textField("goods_id", "GoodsID", "FG-DOG-ADULT-10KG")}
        ${numberField("qty", "数量", "1")}
        ${textField("customer", "客户", "接口客户")}
        ${textField("channel_code", "渠道", "ECOM")}
        ${textField("supplier_batch", "批次", "FGDA-0528-A")}
        ${numberField("actual_fee", "实际运费", "260")}
        ${textField("device_id", "设备号", "IOT-TEMP-001")}
        ${numberField("temperature", "温度", "6")}
        ${textField("location_text", "位置", "接口回传位置")}
        ${textAreaField("reason", "原因/备注", "外部系统事件说明")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="primary" type="submit"><span aria-hidden="true">+</span>处理接口事件</button>
        <button class="secondary" data-export="integration_events" type="button"><span aria-hidden="true">⇩</span>导出接口日志</button>
      </div>
    </form>
    <section class="table-wrap">
      ${table(["时间", "系统", "方向", "事件", "对象", "状态", "消息"], integrationRows || emptyRow(7))}
    </section>
  `;
  if (section === "audit") return `
    <form class="form-panel" id="auditPackageForm">
      <div class="panel-head"><h2>审计证据包</h2></div>
      <div class="form-grid">
        ${selectField("package_type", "类型", `<option>运输审计</option><option>批次追溯审计</option>`)}
        ${selectField("shipment_id", "TMS运单", tmsShipmentOptions(tms.shipments))}
        ${textField("goods_id", "GoodsID", "FG-DOG-ADULT-10KG")}
        ${textField("supplier_batch", "批次", "FGDA-0528-A")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="primary" type="submit"><span aria-hidden="true">+</span>生成审计包</button>
        <button class="secondary" data-export="audit_packages" type="button"><span aria-hidden="true">⇩</span>导出审计包</button>
      </div>
    </form>
    <section class="table-wrap">
      ${table(["审计包", "类型", "对象", "标题", "状态", "摘要", "时间"], auditRows || emptyRow(7))}
    </section>
  `;
  if (section === "monitor") return `
    <form class="form-panel" id="tmsEventForm">
      ${selectField("shipment_id", "运单", tmsShipmentOptions(tms.shipments))}
      ${selectField("event_type", "事件", ["GPS定位", "温度上报", "到达", "开门", "延误"].map((item) => `<option>${item}</option>`).join(""))}
      ${textField("location_text", "位置", "高速服务区 / 客户园区")}
      ${numberField("temperature", "温度", "6")}
      ${numberField("humidity", "湿度", "60")}
      ${textAreaField("note", "备注", "温控、延误或异常说明")}
      <button class="primary" type="submit"><span aria-hidden="true">+</span>上传事件</button>
    </form>
    <section class="table-wrap">
      ${table(["运单", "时间", "事件", "位置", "温度", "风险", "备注"], eventRows || emptyRow(7))}
    </section>
  `;
  if (section === "pod") return `
    <form class="form-panel" id="tmsPodForm">
      ${selectField("shipment_id", "运单", tmsShipmentOptions(tms.shipments))}
      ${textField("signed_by", "签收人", "客户仓管")}
      ${numberField("received_qty", "实收数量", "100")}
      ${numberField("damaged_qty", "破损", "0")}
      ${numberField("shortage_qty", "短少", "0")}
      ${textAreaField("note", "POD备注", "签收正常 / 破损短少说明")}
      <button class="primary" type="submit"><span aria-hidden="true">✓</span>记录POD</button>
    </form>
    <form class="form-panel compact" id="tmsFreightForm">
      ${selectField("shipment_id", "运单", tmsShipmentOptions(tms.shipments))}
      ${numberField("actual_fee", "实际运费", "230")}
      <button class="primary" type="submit"><span aria-hidden="true">✓</span>运费对账</button>
    </form>
    <section class="table-wrap">
      ${table(["运单", "签收人", "时间", "实收", "破损", "短少", "备注"], podRows || emptyRow(7))}
    </section>
    <section class="table-wrap">
      <h3>运费账单</h3>
      ${table(["账单", "运单", "承运商", "预估", "实际", "差异", "状态", "原因"], freightRows || emptyRow(8))}
    </section>
  `;
  if (section === "performance") return `
    <section class="table-wrap">
      <h3>承运商绩效</h3>
      ${table(["承运商编码", "承运商", "运单数", "OTIF", "POD率", "温控异常率", "费用偏差率", "评分"], performanceRows || emptyRow(8))}
    </section>
  `;
  if (section === "recall") return `
    <form class="form-panel" id="recallForm">
      ${selectField("goods_id", "GoodsID", productOptions())}
      ${textField("supplier_batch", "批次", "FGDA-0528-A")}
      ${textAreaField("reason", "召回原因", "质量复核 / 客诉 / 温控异常")}
      <button class="primary" type="submit"><span aria-hidden="true">!</span>冻结并定位</button>
    </form>
    <section class="table-wrap">
      ${table(["召回单", "GoodsID", "批次", "原因", "在库影响", "运单影响", "状态"], recallRows || emptyRow(7))}
    </section>
  `;
  if (section === "master") return `
    <section class="table-wrap">
      <h3>承运商</h3>
      ${table(["编码", "名称", "服务", "能力", "评分"], carrierRows || emptyRow(5))}
    </section>
    <section class="table-wrap">
      <h3>线路费率</h3>
      ${table(["线路", "始发", "目的地", "承运商", "温区", "基础费", "单位费率"], laneRows || emptyRow(7))}
    </section>
    <section class="table-wrap">
      <h3>渠道效期规则</h3>
      ${table(["渠道编码", "渠道", "GoodsID", "名称", "最小剩余效期", "临期策略"], channelRuleRows || emptyRow(6))}
    </section>
  `;
  return `
    <form class="form-panel" id="tmsShipmentForm">
      ${selectField("outbound_id", "WMS发货单", tmsOutboundOptions())}
      ${selectField("carrier_code", "承运商", tmsCarrierOptions(tms.carriers))}
      ${selectField("lane_code", "线路", tmsLaneOptions(tms.lanes))}
      ${textField("customer", "客户", "客户名称")}
      ${textField("vehicle_no", "车牌", "苏E-TMS01")}
      ${textField("driver", "司机", "张师傅")}
      ${textField("driver_phone", "司机电话", "13800000000")}
      ${textField("seal_no", "封签", "SEAL-001")}
      <button class="primary" type="submit"><span aria-hidden="true">+</span>生成运输单</button>
    </form>
    <section class="table-wrap">
      ${table(["运单", "状态", "WMS发货单", "承运商", "客户", "渠道", "最小效期", "目的地", "车牌", "温区", "异常"], shipmentRows || emptyRow(11))}
    </section>
    <div class="actions">
      ${shipments.slice(0, 8).map((item) => `<button class="secondary" data-tms-dispatch="${escapeAttr(item.id)}" type="button">发车 ${escapeHTML(item.id)}</button>`).join("")}
    </div>
  `;
}

function renderSpares() {
  const spares = app.data.spares || { parts: [], warnings: [], transactions: [] };
  const warningRows = filterRows(spares.warnings).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.spec || "")}</td>
      <td>${pill(item.abc_class, item.abc_class === "A" ? "bad" : "info")}</td>
      <td class="num">${fmt(item.current_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)} / ${fmt(item.safety_qty)}</td>
      <td>${spareStatusPill(item.stock_status, item.stock_status_label)}</td>
      <td class="mono">${escapeHTML(item.location || "")}</td>
      <td>${escapeHTML(item.equipment_name || "")}</td>
    </tr>
  `).join("");
  const partRows = filterRows(spares.parts).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td>${escapeHTML(item.spec || "")}</td>
      <td class="num">${fmt(item.current_qty)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.stock_value)}</td>
      <td>${spareStatusPill(item.stock_status, item.stock_status_label)}</td>
      <td>${item.food_contact ? pill("食品接触", "warn") : ""} ${item.critical ? pill("关键", "bad") : ""}</td>
      <td class="mono">${escapeHTML(item.location || "")}</td>
    </tr>
  `).join("");
  const trxRows = filterRows(spares.transactions).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts)}</td>
      <td>${spareActionPill(item.action)}</td>
      <td class="mono">${escapeHTML(item.part_id)}</td>
      <td>${escapeHTML(item.part_name)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit || "")}</td>
      <td class="num">${fmt(item.before_qty)} → ${fmt(item.after_qty)}</td>
      <td class="num">${fmt(item.amount)}</td>
      <td class="mono">${escapeHTML(item.work_order || item.ref_no || "")}</td>
      <td>${escapeHTML(item.equipment_name || "")}</td>
      <td>${escapeHTML(item.requester || item.approver || item.keeper || "")}</td>
    </tr>
  `).join("");

  const section = activeSection("spares");
  if (section === "receive") return `
      <form class="form-panel" id="spareReceiveForm">
        <div class="panel-head"><h2>备件入库 / 到货验收</h2></div>
        <div class="form-grid">
          ${selectField("part_id", "备件", sparePartOptions())}
          ${numberField("qty", "入库数量", "1")}
          ${textField("ref_no", "采购订单号", "PO-SP-001")}
          ${textField("supplier", "供应商", "原厂供应商")}
          ${textField("location", "货位", "SP-A-01-01")}
          ${numberField("unit_price", "单价", "0")}
          ${textField("approver", "验收人", "设备工程师")}
          ${textField("keeper", "库管员", "备件库管")}
          ${textAreaField("note", "验收备注", "包装、数量、型号、食品级证明/质保资料已核对")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>入库</button>
        </div>
      </form>
  `;
  if (section === "issue") return `
      <form class="form-panel" id="spareIssueForm">
        <div class="panel-head"><h2>工单领用 / 发料</h2></div>
        <div class="form-grid">
          ${selectField("part_id", "备件", sparePartOptions())}
          ${numberField("qty", "领用数量", "1")}
          ${textField("work_order", "维修工单号", "WO-SP-001")}
          ${textField("equipment_name", "设备名称", "1号包装机")}
          ${textField("equipment_code", "设备编号", "PK01")}
          ${selectField("reason", "领用原因", `
            <option>故障维修</option>
            <option>计划保养</option>
            <option>年度大修</option>
            <option>技改项目</option>
            <option>安全环保整改</option>
            <option>工具耗材领用</option>
          `)}
          ${textField("requester", "领用人", "维修人员")}
          ${textField("approver", "审批人", "维修主管")}
          ${textField("keeper", "发料人", "备件库管")}
          ${selectField("old_part_status", "旧件处理", `
            <option>退库</option>
            <option>报废</option>
            <option>待分析</option>
            <option>无旧件</option>
          `)}
          <label class="field full toggle">
            <input name="food_clearance" type="checkbox" checked>
            食品接触区域维修后清场确认
          </label>
          ${textAreaField("note", "安装反馈", "安装完成，设备恢复正常，旧件已按要求处理")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">-</span>领用出库</button>
        </div>
      </form>
  `;
  if (section === "returns") return `
    <div class="grid-2">
      <form class="form-panel" id="spareReturnForm">
        <div class="panel-head"><h2>旧件退库</h2></div>
        <div class="form-grid one">
          ${selectField("part_id", "备件", sparePartOptions())}
          ${numberField("qty", "退库数量", "1")}
          ${textField("work_order", "工单号", "WO-SP-001")}
          ${textField("keeper", "库管员", "备件库管")}
          ${selectField("old_part_status", "旧件状态", `<option>可维修件</option><option>可用件</option><option>待分析件</option>`)}
          ${textAreaField("note", "备注", "旧件退回待修区/可用库存")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="secondary" type="submit"><span aria-hidden="true">+</span>退库</button>
        </div>
      </form>
      <form class="form-panel" id="spareScrapForm">
        <div class="panel-head"><h2>旧件报废</h2></div>
        <div class="form-grid one">
          ${selectField("part_id", "备件", sparePartOptions())}
          ${numberField("qty", "报废数量", "1")}
          ${textField("reason", "报废原因", "损坏无法修复")}
          ${textField("approver", "审批人", "设备经理")}
          ${textField("requester", "申请人", "维修人员")}
          ${textAreaField("note", "备注", "已拍照留存，按报废流程处理")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="danger" type="submit"><span aria-hidden="true">!</span>报废</button>
        </div>
      </form>
    </div>
  `;
  if (section === "count") return `
    <form class="form-panel" id="spareCountForm">
      <div class="panel-head"><h2>备件盘点</h2></div>
      <div class="form-grid one">
        ${selectField("part_id", "备件", sparePartOptions())}
        ${numberField("actual_qty", "实盘数量", "1")}
        ${textField("keeper", "盘点人", "备件库管")}
        ${textAreaField("reason", "差异原因", "月度盘点差异，已复核")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="secondary" type="submit"><span aria-hidden="true">✓</span>盘点调整</button>
      </div>
    </form>
  `;
  if (section === "master") return `
    <form class="form-panel" id="sparePartForm">
      <div class="panel-head"><h2>备件基础台账</h2></div>
      <div class="form-grid">
        ${textField("id", "备件编码", "SP-ME-EX01-0009")}
        ${textField("name", "备件名称", "膨化机切刀")}
        ${textField("spec", "规格型号", "EX01-刀片套件")}
        ${textField("brand", "品牌", "原厂")}
        ${selectField("category", "类别", `
          <option>机械类</option><option>电气类</option><option>气动类</option><option>液压类</option>
          <option>仪表类</option><option>包装类</option><option>公用工程类</option><option>食品接触类</option><option>工具耗材类</option>
        `)}
        ${selectField("abc_class", "ABC等级", `<option>A</option><option>B</option><option>C</option><option>D</option>`)}
        ${textField("unit", "单位", "个")}
        ${numberField("current_qty", "当前库存", "0")}
        ${numberField("min_qty", "最低库存", "1")}
        ${numberField("safety_qty", "安全库存", "2")}
        ${numberField("max_qty", "最高库存", "5")}
        ${numberField("lead_days", "采购周期/天", "15")}
        ${numberField("unit_price", "单价", "0")}
        ${textField("supplier", "供应商", "合格供应商")}
        ${textField("location", "货位", "SP-A-01-01")}
        ${textField("equipment_name", "适用设备", "1号膨化线")}
        ${textField("equipment_code", "设备编号", "EX01")}
        ${dateField("expiry_date", "有效期")}
        <label class="field toggle"><input name="food_contact" type="checkbox">食品接触件</label>
        <label class="field toggle"><input name="critical" type="checkbox">关键备件</label>
        <label class="field toggle"><input name="imported" type="checkbox">进口件</label>
        ${textAreaField("remark", "备注", "特殊材质、食品级证明、储存要求")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="primary" type="submit"><span aria-hidden="true">+</span>保存备件</button>
      </div>
    </form>
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>备件库存台账</h2>
        <div class="actions"><button class="secondary" data-export="spare_parts" type="button"><span aria-hidden="true">⇩</span>导出台账</button></div>
      </div>
      ${table(["编码", "名称", "类别", "规格", "库存", "金额", "状态", "标签", "货位"], partRows || emptyRow(9))}
    </section>
  `;
  if (section === "transactions") return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>备件出入库流水</h2>
        <div class="actions"><button class="secondary" data-export="spare_transactions" type="button"><span aria-hidden="true">⇩</span>导出流水</button></div>
      </div>
      ${table(["时间", "动作", "编码", "名称", "数量", "库存变化", "金额", "单号", "设备", "人员"], trxRows || emptyRow(10))}
    </section>
  `;
  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>库存预警</h2>
        <div class="actions"><button class="secondary" data-export="spare_warnings" type="button"><span aria-hidden="true">⇩</span>导出预警</button></div>
      </div>
      ${table(["编码", "名称", "规格", "等级", "库存", "最低/安全", "状态", "货位", "设备"], warningRows || emptyRow(9))}
    </section>
  `;
}

function renderRFScanner() {
  const scan = app.data.scan_result;
  const scanRows = filterRows(app.data.recent_scans || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts || "")}</td>
      <td>${escapeHTML(item.scan_type || "")}</td>
      <td class="mono">${escapeHTML(item.code || "")}</td>
      <td>${scanTypePill(item.parsed_type)}</td>
      <td class="mono">${escapeHTML(item.ref_id || "")}</td>
      <td class="mono">${escapeHTML(item.location_id || "")}</td>
      <td class="mono">${escapeHTML(item.goods_id || "")}</td>
      <td>${escapeHTML(item.action || "")}</td>
      <td>${escapeHTML(item.result || "")}</td>
      <td>${escapeHTML(item.operator || "")}</td>
    </tr>
  `).join("");
  const detail = scan?.detail || {};
  const resultPanel = scan ? `
    <section class="scan-result">
      <div class="panel-head"><h2>扫描结果</h2>${scanTypePill(scan.parsed_type)}</div>
      <div class="scan-result-grid">
        <div><small>编码</small><strong class="mono">${escapeHTML(scan.code || "")}</strong></div>
        <div><small>引用</small><strong class="mono">${escapeHTML(scan.ref_id || "")}</strong></div>
        <div><small>库位</small><strong class="mono">${escapeHTML(scan.location_id || detail.location_id || "")}</strong></div>
        <div><small>货品</small><strong class="mono">${escapeHTML(scan.goods_id || detail.goods_id || "")}</strong></div>
        <div><small>名称/区域</small><strong>${escapeHTML(detail.goods_name || detail.name || detail.area || "")}</strong></div>
        <div><small>数量/容量</small><strong>${fmt(detail.qty ?? detail.capacity ?? "")}</strong></div>
      </div>
    </section>
  ` : `
    <section class="scan-result">
      <div class="panel-head"><h2>扫描结果</h2></div>
      <div class="empty compact">等待扫描</div>
    </section>
  `;
  const section = activeSection("rf");
  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>扫描记录</h2></div>
      ${table(["时间", "来源", "编码", "类型", "引用", "库位", "货品", "动作", "结果", "操作人"], scanRows || emptyRow(10))}
    </section>
  `;
  const isCamera = section === "camera";

  return `
    <div class="grid-2 scan-grid">
      <form class="rf-panel" id="rfScanForm">
        <div class="panel-head"><h2>${isCamera ? "摄像头扫码" : "RF枪扫描"}</h2></div>
        <div class="form-grid one">
          ${isCamera ? `<input name="scan_type" type="hidden" value="摄像头">` : `<input name="scan_type" type="hidden" value="RF枪">`}
          ${selectField("action", "动作", `
            <option>查询</option>
            <option>移库起点</option>
            <option>目标库位</option>
            <option>盘点复核</option>
            <option>出库复核</option>
          `)}
          <label class="field">扫描码
            <input class="scan-input" name="code" id="rfScanInput" placeholder="SSCC / 库位 / GoodsID" autofocus>
          </label>
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">⌁</span>识别</button>
          ${isCamera ? `<button class="secondary" id="startQrBtn" type="button"><span aria-hidden="true">▣</span>开启摄像头</button><button class="ghost" id="stopQrBtn" type="button">停止</button>` : ""}
        </div>
        ${isCamera ? `<video class="scanner-video" id="qrVideo" muted playsinline></video>` : ""}
      </form>
      ${resultPanel}
    </div>
  `;
}

function renderLabels() {
  const label = app.data.current_label;
  const printRows = filterRows(app.data.label_prints || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts || "")}</td>
      <td>${escapeHTML(item.label_type || "")}</td>
      <td class="mono">${escapeHTML(item.goods_id || "")}</td>
      <td>${escapeHTML(item.goods_name || "")}</td>
      <td class="mono">${escapeHTML(item.batch_no || "")}</td>
      <td class="mono">${escapeHTML(item.sscc || "")}</td>
      <td>${escapeHTML(item.code_type || "")}</td>
      <td class="num">${fmt(item.copies || 1)}</td>
      <td>${escapeHTML(item.operator || "")}</td>
    </tr>
  `).join("");
  const section = activeSection("labels");
  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>标签打印记录</h2>
        <button class="secondary" data-export="label_prints" type="button"><span aria-hidden="true">⇩</span>导出记录</button>
      </div>
      ${table(["时间", "类型", "GoodsID", "名称", "批号", "SSCC", "码制", "份数", "操作人"], printRows || emptyRow(9))}
    </section>
  `;
  const labelType = section === "product" ? "产品标签" : "原料标签";
  const visibleLabel = label?.label_type === labelType ? label : null;
  const preview = visibleLabel ? labelCardHTML(visibleLabel, false) : `<div class="empty compact">生成后显示标签预览</div>`;
  const goodsOptions = section === "product" ? productOptions("成品") : rawProductOptions();

  return `
    <div class="grid-2 label-grid">
      <form class="form-panel" id="labelForm">
        <div class="panel-head"><h2>${labelType}</h2></div>
        <div class="form-grid">
          <input name="label_type" type="hidden" value="${escapeAttr(labelType)}">
          ${selectField("goods_id", "货品", goodsOptions)}
          ${textField("batch_no", "人工录入批号", "BATCH-20260602-001")}
          ${textField("supplier_batch", "供应商/生产批次", "SUP-BATCH-001")}
          ${numberField("qty", "数量", "1000")}
          ${selectField("location_id", "库位", `<option value="">不指定</option>${locationOptions()}`)}
          ${textField("sscc", "SSCC/托盘号", "SSCC202606020001")}
          ${dateField("production_date", "生产日期")}
          ${dateField("expiry_date", "BBD/有效期")}
          ${selectField("quality_status", "品质", qualityOptions("合格"))}
          ${selectField("code_type", "码制", `<option>条码+二维码</option><option>条码</option><option>二维码</option>`)}
          ${numberField("copies", "打印份数", "1")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">▥</span>生成标签</button>
          <button class="secondary" id="printCurrentLabelBtn" type="button" ${visibleLabel ? "" : "disabled"}><span aria-hidden="true">□</span>连接打印机打印</button>
        </div>
      </form>
      <section class="panel label-preview-panel">
        <div class="panel-head"><h2>打印预览</h2></div>
        <div class="label-preview">${preview}</div>
      </section>
    </div>
  `;
}

function renderWarehouseModel() {
  const modelRows = filterRows(app.data.location_model || []).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.area)}</td>
      <td>${escapeHTML(item.zone)}</td>
      <td>${escapeHTML(item.type)}</td>
      <td class="num">${fmt(item.occupied_qty)}</td>
      <td class="num">${fmt(item.capacity)}</td>
      <td class="num">${fmt(item.occupancy_pct)}%</td>
      <td>${modelStatusPill(item.model_status)}</td>
      <td>${escapeHTML(item.last_camera_scan || "")}</td>
    </tr>
  `).join("");
  const cameraRows = filterRows(app.data.camera_scans || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts || "")}</td>
      <td class="mono">${escapeHTML(item.location_id || "")}</td>
      <td>${escapeHTML(item.camera_name || "")}</td>
      <td>${modelStatusPill(item.model_status)}</td>
      <td class="num">${fmt(item.confidence)}</td>
      <td>${escapeHTML(item.operator || "")}</td>
      <td>${escapeHTML(item.image_note || "")}</td>
    </tr>
  `).join("");
  const tiles = (app.data.location_model || []).map((item) => {
    const height = Math.max(22, Math.min(120, Number(item.occupancy_pct || 0) + 22));
    return `
      <div class="model-location ${modelStatusClass(item.model_status)}" style="--height:${height}px">
        <div class="model-cube"></div>
        <strong class="mono">${escapeHTML(item.id)}</strong>
        <small>${escapeHTML(item.area)} · ${fmt(item.occupancy_pct)}%</small>
      </div>
    `;
  }).join("");
  const section = activeSection("model");

  if (section === "locations") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>库位模型明细</h2></div>
      ${table(["库位", "仓库", "库区", "类型", "占用", "容量", "占用率", "状态", "最近采集"], modelRows || emptyRow(9))}
    </section>
  `;

  if (section === "capture") return `
    <form class="rf-panel" id="cameraModelForm">
      <div class="panel-head"><h2>摄像头采集</h2></div>
      <div class="form-grid one">
        ${selectField("location_id", "库位", locationOptions())}
        ${textField("camera_name", "摄像头", "WH-CAM-01")}
        ${textAreaField("image_note", "采集备注", "货架识别/占用复核")}
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="secondary" id="startModelCameraBtn" type="button"><span aria-hidden="true">▣</span>开启</button>
        <button class="primary" id="captureModelBtn" type="button"><span aria-hidden="true">+</span>采集建模</button>
        <button class="ghost" id="stopModelCameraBtn" type="button">停止</button>
      </div>
      <video class="scanner-video" id="modelVideo" muted playsinline></video>
    </form>
  `;

  if (section === "records") return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>摄像头采集记录</h2></div>
      ${table(["时间", "库位", "摄像头", "状态", "置信度", "操作人", "备注"], cameraRows || emptyRow(7))}
    </section>
  `;

  return `
    <section class="panel model-panel">
      <div class="panel-head"><h2>在线三维库位</h2></div>
      <div class="warehouse-scene">${tiles}</div>
    </section>
  `;
}

function renderInventory() {
  const stockRows = app.data.stock_warnings.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td class="num">${fmt(item.on_hand)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.available)} ${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)}</td>
      <td class="num">${fmt(item.safety_qty)}</td>
      <td class="num">${fmt(item.reorder_qty)}</td>
      <td>${stockStatusPill(item)}</td>
    </tr>
  `).join("");
  const expiryRows = app.data.expiry_warnings.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td>${escapeHTML(item.goods_name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
      <td>${expiryDatePill(item)}</td>
      <td class="num">${fmt(item.days_left)}</td>
      <td>${expiryStatusPill(item)}</td>
    </tr>
  `).join("");
  const rows = filterRows(app.data.inventory).map((item) => {
    return `
      <tr>
        <td class="mono">${escapeHTML(item.sscc)}</td>
        <td class="mono">${escapeHTML(item.goods_id)}</td>
        <td>${escapeHTML(item.goods_name)}</td>
        <td class="mono">${escapeHTML(item.location_id)}</td>
        <td>${escapeHTML(item.area)} / ${escapeHTML(item.zone)}</td>
        <td class="num">${fmt(item.qty)} ${escapeHTML(item.unit)}</td>
        <td class="num">${fmt(item.reserved_qty)}</td>
        <td class="num">${fmt(item.available_qty)}</td>
        <td>${qualityPill(item.quality_status)}</td>
        <td>${expiryDatePill(item)}</td>
        <td class="actions">
          ${hasPerm("status") ? `<button class="ghost" data-freeze="${escapeHTML(item.sscc)}" type="button">冻结</button>` : ""}
          ${hasPerm("status") ? `<button class="ghost" data-hold="${escapeHTML(item.sscc)}" type="button">暂扣</button>` : ""}
          ${hasPerm("status") ? `<button class="secondary" data-release="${escapeHTML(item.sscc)}" type="button">合格</button>` : ""}
        </td>
      </tr>
    `;
  }).join("");

  return `
    <div class="grid-2">
      <section class="table-wrap">
        <div class="panel-head panel">
          <h2>安全库存预警</h2>
          <div class="actions"><button class="secondary" data-export="stock_warnings" type="button"><span aria-hidden="true">⇩</span>导出预警</button></div>
        </div>
        ${table(["货品", "名称", "类别", "在库", "可用", "最低", "安全", "建议补足", "状态"], stockRows || emptyRow(9))}
      </section>
      <section class="table-wrap">
        <div class="panel-head panel">
          <h2>临期提醒</h2>
          <div class="actions"><button class="secondary" data-export="expiry_warnings" type="button"><span aria-hidden="true">⇩</span>导出临期</button></div>
        </div>
        ${table(["SSCC", "货品", "名称", "类别", "库位", "在库", "BBD", "剩余天数", "状态"], expiryRows || emptyRow(9))}
      </section>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>在库明细</h2>
        <div class="actions">
          ${hasPerm("move") ? `<button class="secondary" data-jump="move" type="button"><span aria-hidden="true">⇄</span>移库</button>` : ""}
          ${hasPerm("count") ? `<button class="secondary" data-jump="count" type="button"><span aria-hidden="true">✓</span>盘点</button>` : ""}
        </div>
      </div>
      ${table(["SSCC", "货品", "名称", "库位", "库区", "在库", "保留", "可用", "品质", "BBD", "操作"], rows || emptyRow(11))}
    </section>
  `;
}

function renderMove() {
  const moveRows = filterRows(app.data.moves).map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td class="mono">${escapeHTML(item.from_location)}</td>
      <td class="mono">${escapeHTML(item.to_location)}</td>
      <td class="num">${fmt(item.qty)}</td>
      <td>${escapeHTML(item.operator || "")}</td>
      <td>${escapeHTML(item.created_at)}</td>
    </tr>
  `).join("");

  return `
    <div class="grid-2">
      <form class="rf-panel" id="moveForm">
        <div class="panel-head"><h2>RF 移库</h2></div>
        <div class="form-grid one">
          <label class="field">扫描 SSCC
            <input class="scan-input" name="sscc" placeholder="SSCC202606020001" autofocus>
          </label>
          ${selectField("to_location", "移入库位", locationOptions())}
          ${numberField("qty", "数量", "留空则整托")}
          ${textField("operator", "操作人", "forklift-01")}
          ${textAreaField("remark", "备注", "实物与标签一致")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">⇄</span>确认移库</button>
        </div>
      </form>
      <section class="panel">
        <div class="panel-head"><h2>待移动库存</h2></div>
        <div class="mini-list">
          ${app.data.inventory.slice(0, 9).map(stockMiniRow).join("")}
        </div>
      </section>
    </div>
    <section class="table-wrap">
      <div class="panel-head panel"><h2>移库记录</h2></div>
      ${table(["移库单", "SSCC", "货品", "移出", "移入", "数量", "操作人", "时间"], moveRows || emptyRow(8))}
    </section>
  `;
}

function renderCount() {
  const countRows = filterRows(app.data.counts || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.count_type || "日常盘点")}</td>
      <td>${escapeHTML(item.scope || "")}</td>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td class="mono">${escapeHTML(item.sscc)}</td>
      <td class="mono">${escapeHTML(item.goods_id)}</td>
      <td class="mono">${escapeHTML(item.location_id)}</td>
      <td class="num">${fmt(item.system_qty)}</td>
      <td class="num">${fmt(item.actual_qty)}</td>
      <td class="num">${fmt(item.diff_qty)}</td>
      <td>${pill(item.status, "ok")}</td>
      <td>${item.adjusted ? pill("已调整", "warn") : pill("未调整", "info")}</td>
      <td>${escapeHTML(item.operator || "")}</td>
      <td>${escapeHTML(item.reason || "")}</td>
      <td>${escapeHTML(item.created_at || "")}</td>
    </tr>
  `).join("");
  const section = activeSection("count");

  if (section === "daily") return `
    <div class="grid-2">
      <form class="rf-panel" id="countForm">
        <div class="panel-head"><h2>日常盘点</h2></div>
        <div class="form-grid one">
          ${selectField("count_type", "盘点类型", `
            <option>日常盘点</option>
            <option>月度盘点</option>
            <option>年度盘点</option>
          `)}
          ${textField("scope", "范围", "原料仓 / 包材仓 / 成品仓")}
          <label class="field">扫描 SSCC
            <input class="scan-input" name="sscc" placeholder="SSCC202606020001">
          </label>
          ${numberField("actual_qty", "实盘数量", "1000")}
          ${textAreaField("reason", "原因", "P 段盘点差异，已复核")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">✓</span>保存盘点</button>
        </div>
      </form>
      <form class="form-panel" id="statusForm">
        <div class="panel-head"><h2>在库属性变更</h2></div>
        <div class="form-grid one">
          ${textField("sscc", "SSCC", "SSCC202606020001")}
          ${selectField("quality_status", "品质状态", qualityOptions("冻结"))}
          ${textAreaField("reason", "原因", "质检复核/隔离/放行")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="secondary" type="submit"><span aria-hidden="true">◎</span>更新属性</button>
        </div>
      </form>
    </div>
  `;

  if (section === "cycle") return `
    <div class="grid-2">
      <form class="form-panel" id="cycleCountForm">
        <div class="panel-head"><h2>月度/年度盘点</h2></div>
        <div class="form-grid one">
          ${selectField("count_type", "盘点类型", `
            <option>月度盘点</option>
            <option>年度盘点</option>
          `)}
          ${textField("scope", "盘点范围", "全仓 / 原料 / 包材 / 成品 / GoodsID")}
          ${textAreaField("reason", "盘点说明", "月末全仓盘点")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>生成清单</button>
        </div>
      </form>
      <section class="panel">
        <div class="panel-head"><h2>当前库存</h2></div>
        <div class="mini-list">
          ${app.data.inventory.slice(0, 8).map(stockMiniRow).join("")}
        </div>
      </section>
    </div>
  `;

  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>盘点记录</h2>
        <button class="secondary" data-export="inventory" type="button"><span aria-hidden="true">⇩</span>库存明细</button>
      </div>
      ${table(["类型", "范围", "盘点单", "SSCC", "货品", "库位", "系统数", "实盘数", "差异", "状态", "调整", "操作人", "原因", "时间"], countRows || emptyRow(14))}
    </section>
  `;
}

function renderMasters() {
  const productRows = app.data.products.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.name)}</td>
      <td>${escapeHTML(item.category)}</td>
      <td>${escapeHTML(item.unit)}</td>
      <td class="num">${fmt(item.min_qty)}</td>
      <td class="num">${fmt(item.safety_qty)}</td>
      <td class="num">${fmt(item.expiry_alert_days)}</td>
      <td>${item.courbon ? pill("是", "info") : "否"}</td>
    </tr>
  `).join("");
  const locationRows = app.data.locations.map((item) => `
    <tr>
      <td class="mono">${escapeHTML(item.id)}</td>
      <td>${escapeHTML(item.area)}</td>
      <td>${escapeHTML(item.zone)}</td>
      <td>${escapeHTML(item.type)}</td>
      <td class="num">${item.priority}</td>
      <td class="num">${fmt(item.capacity)}</td>
    </tr>
  `).join("");

  return `
    <div class="grid-2">
      <form class="form-panel" id="productForm">
        <div class="panel-head"><h2>货品</h2></div>
        <div class="form-grid">
          ${textField("id", "GoodsID", "NEW-RM")}
          ${textField("name", "名称", "新原料")}
          ${textField("category", "类别", "原料")}
          ${textField("unit", "单位", "kg")}
          ${numberField("min_qty", "最低库存", "300")}
          ${numberField("safety_qty", "安全库存", "500")}
          ${numberField("expiry_alert_days", "临期提前提醒天数", "60")}
          ${numberField("shelf_days", "保质期天数", "365")}
          <label class="field full toggle">
            <input name="courbon" type="checkbox">
            MES物料
          </label>
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>保存货品</button>
        </div>
      </form>
      <form class="form-panel" id="locationForm">
        <div class="panel-head"><h2>库位</h2></div>
        <div class="form-grid">
          ${textField("id", "库位编号", "RM-A03-01")}
          ${textField("area", "仓库", "原料仓")}
          ${textField("zone", "库区", "A03 货架")}
          ${textField("type", "类型", "正常货位")}
          ${numberField("priority", "分配优先级", "5")}
          ${numberField("capacity", "容量", "12000")}
        </div>
        <div class="actions" style="margin-top:12px">
          <button class="primary" type="submit"><span aria-hidden="true">+</span>保存库位</button>
        </div>
      </form>
    </div>
    <div class="grid-2">
      <section class="table-wrap">
        <div class="panel-head panel"><h2>货品主数据</h2></div>
        ${table(["GoodsID", "名称", "类别", "单位", "最低库存", "安全库存", "临期天数", "MES"], productRows)}
      </section>
      <section class="table-wrap">
        <div class="panel-head panel"><h2>库位主数据</h2></div>
        ${table(["库位", "仓库", "库区", "类型", "优先级", "容量"], locationRows)}
      </section>
    </div>
  `;
}

function renderExcel() {
  const allowedImports = excelImportItems.filter((item) => hasPerm(item.permission));
  const allowedExports = excelExportItems.filter((item) => !item.permission || hasPerm(item.permission));
  const exportButtons = allowedExports.map((item) => `
    <button class="excel-action" data-export="${escapeAttr(item.dataset)}" type="button">
      <span aria-hidden="true">⇩</span>
      <strong>${escapeHTML(item.label)}</strong>
      <small>.xlsx</small>
    </button>
  `).join("");
  const templateButtons = allowedImports.map((item) => `
    <button class="excel-action" data-export="${escapeAttr(item.dataset)}" type="button">
      <span aria-hidden="true">□</span>
      <strong>${escapeHTML(item.label)}</strong>
      <small>模板</small>
    </button>
  `).join("");
  const importOptions = allowedImports.map((item) => `
    <option value="${escapeAttr(item.type)}">${escapeHTML(item.label)}</option>
  `).join("");

  return `
    <div class="grid-2 excel-grid">
      <section class="panel">
        <div class="panel-head"><h2>导出当前数据</h2></div>
        <div class="excel-actions">${exportButtons || `<div class="empty compact">当前账号没有导出权限</div>`}</div>
      </section>
      <section class="panel">
        <div class="panel-head"><h2>下载导入模板</h2></div>
        <div class="excel-actions">${templateButtons || `<div class="empty compact">当前账号没有导入权限</div>`}</div>
      </section>
    </div>
    <form class="form-panel" id="excelImportForm">
      <div class="panel-head"><h2>批量导入</h2></div>
      <div class="form-grid excel-import-grid">
        <label class="field">导入类型
          <select name="import_type" ${allowedImports.length ? "" : "disabled"}>${importOptions}</select>
        </label>
        <label class="field">文件
          <input name="file" type="file" accept=".xlsx,.csv" ${allowedImports.length ? "" : "disabled"}>
        </label>
      </div>
      <div class="actions" style="margin-top:12px">
        <button class="primary" type="submit" ${allowedImports.length ? "" : "disabled"}><span aria-hidden="true">+</span>开始导入</button>
      </div>
    </form>
  `;
}

function renderLedger() {
  const rows = filterRows(app.data.ledger).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts)}</td>
      <td>${escapeHTML(item.action)}</td>
      <td class="mono">${escapeHTML(item.ref_id || "")}</td>
      <td class="mono">${escapeHTML(item.sscc || "")}</td>
      <td class="mono">${escapeHTML(item.goods_id || "")}</td>
      <td class="mono">${escapeHTML(item.location_id || "")}</td>
      <td class="num">${fmt(item.qty)}</td>
      <td class="num">${fmt(item.before_qty)}</td>
      <td class="num">${fmt(item.after_qty)}</td>
      <td>${escapeHTML(item.note || "")}</td>
    </tr>
  `).join("");
  return `
    <section class="table-wrap">
      <div class="panel-head panel"><h2>库存流水</h2></div>
      ${table(["时间", "动作", "来源单", "SSCC", "货品", "库位", "数量", "前值", "后值", "备注"], rows || emptyRow(10))}
    </section>
  `;
}

function renderOperationLogs() {
  const rows = filterRows(app.data.operation_logs || []).map((item) => `
    <tr>
      <td>${escapeHTML(item.ts || "")}</td>
      <td class="mono">${escapeHTML(item.username || "")}</td>
      <td>${escapeHTML(item.display_name || "")}</td>
      <td>${escapeHTML(item.role || "")}</td>
      <td>${pill(item.method || "", "info")}</td>
      <td class="mono">${escapeHTML(item.path || "")}</td>
      <td class="num">${escapeHTML(item.status_code || "")}</td>
      <td>${escapeHTML(item.action || "")}</td>
      <td>${escapeHTML(item.message || "")}</td>
      <td class="mono">${escapeHTML(item.ip || "")}</td>
      <td>${escapeHTML(String(item.payload || "").slice(0, 160))}</td>
    </tr>
  `).join("");
  return `
    <section class="table-wrap">
      <div class="panel-head panel">
        <h2>系统操作日志</h2>
        <button class="secondary" data-export="operation_logs" type="button"><span aria-hidden="true">⇩</span>导出日志</button>
      </div>
      ${table(["时间", "账号", "姓名", "角色", "方法", "接口", "状态码", "动作", "结果", "IP", "请求内容"], rows || emptyRow(11))}
    </section>
  `;
}

function bindPageEvents() {
  contentEl.querySelectorAll("[data-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      app.page = button.dataset.jump;
      render();
    });
  });
  contentEl.querySelectorAll("[data-page-jump]").forEach((button) => {
    button.addEventListener("click", () => {
      app.page = button.dataset.pageJump;
      if (button.dataset.sectionJump) {
        app.sections[app.page] = button.dataset.sectionJump;
        app.expandedNav[app.page] = true;
      }
      render();
    });
  });

  const inboundForm = document.querySelector("#inboundForm");
  if (inboundForm) bindSubmit(inboundForm, "/api/inbounds");

  const outboundForm = document.querySelector("#outboundForm");
  if (outboundForm) bindSubmit(outboundForm, "/api/outbounds");

  const finishedReceiveForm = document.querySelector("#finishedReceiveForm");
  if (finishedReceiveForm) bindSubmit(finishedReceiveForm, "/api/finished/receive");

  const finishedShipForm = document.querySelector("#finishedShipForm");
  if (finishedShipForm) bindSubmit(finishedShipForm, "/api/finished/ship");

  const finishedWaveForm = document.querySelector("#finishedWaveForm");
  if (finishedWaveForm) bindSubmit(finishedWaveForm, "/api/finished/waves");

  const finishedWavePickForm = document.querySelector("#finishedWavePickForm");
  if (finishedWavePickForm) bindWaveActionSubmit(finishedWavePickForm, "pick");

  const finishedWaveReviewForm = document.querySelector("#finishedWaveReviewForm");
  if (finishedWaveReviewForm) bindWaveActionSubmit(finishedWaveReviewForm, "review");

  const finishedWaveShipForm = document.querySelector("#finishedWaveShipForm");
  if (finishedWaveShipForm) bindWaveActionSubmit(finishedWaveShipForm, "ship");

  const tmsShipmentForm = document.querySelector("#tmsShipmentForm");
  if (tmsShipmentForm) bindSubmit(tmsShipmentForm, "/api/tms/shipments");

  const tmsEventForm = document.querySelector("#tmsEventForm");
  if (tmsEventForm) bindTmsActionSubmit(tmsEventForm, "event");

  const tmsPodForm = document.querySelector("#tmsPodForm");
  if (tmsPodForm) bindTmsActionSubmit(tmsPodForm, "pod");

  const tmsFreightForm = document.querySelector("#tmsFreightForm");
  if (tmsFreightForm) bindTmsActionSubmit(tmsFreightForm, "freight");

  const tmsIotForm = document.querySelector("#tmsIotForm");
  if (tmsIotForm) bindSubmit(tmsIotForm, "/api/tms/iot");

  const driverTaskForm = document.querySelector("#driverTaskForm");
  if (driverTaskForm) bindTmsActionSubmit(driverTaskForm, "driver");

  const integrationEventForm = document.querySelector("#integrationEventForm");
  if (integrationEventForm) bindSubmit(integrationEventForm, "/api/integrations/events");

  const auditPackageForm = document.querySelector("#auditPackageForm");
  if (auditPackageForm) bindSubmit(auditPackageForm, "/api/audit/packages");

  const recallForm = document.querySelector("#recallForm");
  if (recallForm) bindSubmit(recallForm, "/api/recalls");

  const packagingReceiveForm = document.querySelector("#packagingReceiveForm");
  if (packagingReceiveForm) bindSubmit(packagingReceiveForm, "/api/packaging/receive");

  const packagingIssueForm = document.querySelector("#packagingIssueForm");
  if (packagingIssueForm) bindSubmit(packagingIssueForm, "/api/packaging/issue");

  const rfScanForm = document.querySelector("#rfScanForm");
  if (rfScanForm) bindSubmit(rfScanForm, "/api/scans");

  const labelForm = document.querySelector("#labelForm");
  if (labelForm) bindSubmit(labelForm, "/api/labels/generate");

  const locationRecommendForm = document.querySelector("#locationRecommendForm");
  if (locationRecommendForm) bindSubmit(locationRecommendForm, "/api/location-recommendations");

  const cameraModelForm = document.querySelector("#cameraModelForm");
  if (cameraModelForm) bindSubmit(cameraModelForm, "/api/camera-scans");

  const moveForm = document.querySelector("#moveForm");
  if (moveForm) bindSubmit(moveForm, "/api/moves");

  const countForm = document.querySelector("#countForm");
  if (countForm) bindSubmit(countForm, "/api/counts");

  const cycleCountForm = document.querySelector("#cycleCountForm");
  if (cycleCountForm) bindSubmit(cycleCountForm, "/api/cycle-counts");

  const statusForm = document.querySelector("#statusForm");
  if (statusForm) bindSubmit(statusForm, "/api/status");

  const productForm = document.querySelector("#productForm");
  if (productForm) bindSubmit(productForm, "/api/masters/products");

  const locationForm = document.querySelector("#locationForm");
  if (locationForm) bindSubmit(locationForm, "/api/masters/locations");

  const sparePartForm = document.querySelector("#sparePartForm");
  if (sparePartForm) bindSubmit(sparePartForm, "/api/spares/parts");

  const spareReceiveForm = document.querySelector("#spareReceiveForm");
  if (spareReceiveForm) bindSubmit(spareReceiveForm, "/api/spares/receive");

  const spareIssueForm = document.querySelector("#spareIssueForm");
  if (spareIssueForm) bindSubmit(spareIssueForm, "/api/spares/issue");

  const spareReturnForm = document.querySelector("#spareReturnForm");
  if (spareReturnForm) bindSubmit(spareReturnForm, "/api/spares/return");

  const spareCountForm = document.querySelector("#spareCountForm");
  if (spareCountForm) bindSubmit(spareCountForm, "/api/spares/count");

  const spareScrapForm = document.querySelector("#spareScrapForm");
  if (spareScrapForm) bindSubmit(spareScrapForm, "/api/spares/scrap");

  const smartQueryForm = document.querySelector("#smartQueryForm");
  if (smartQueryForm) bindSubmit(smartQueryForm, "/api/smart/query");

  const smartSopForm = document.querySelector("#smartSopForm");
  if (smartSopForm) bindSubmit(smartSopForm, "/api/smart/sop");

  contentEl.querySelectorAll("[data-export]").forEach((button) => {
    button.addEventListener("click", () => downloadExcel(button.dataset.export));
  });

  const excelImportForm = document.querySelector("#excelImportForm");
  if (excelImportForm) bindExcelImport(excelImportForm);

  contentEl.querySelectorAll("[data-confirm]").forEach((button) => {
    button.addEventListener("click", () => postJSON(`/api/outbounds/${button.dataset.confirm}/confirm`, {}));
  });
  contentEl.querySelectorAll("[data-tms-dispatch]").forEach((button) => {
    button.addEventListener("click", () => postJSON(`/api/tms/shipments/${encodeURIComponent(button.dataset.tmsDispatch)}/dispatch`, {}));
  });
  contentEl.querySelectorAll("[data-print]").forEach((button) => {
    button.addEventListener("click", () => printPickTicket(button.dataset.print));
  });
  contentEl.querySelectorAll("[data-freeze]").forEach((button) => {
    button.addEventListener("click", () => postJSON("/api/status", {
      sscc: button.dataset.freeze,
      quality_status: "冻结",
      reason: "前端快速冻结",
    }));
  });
  contentEl.querySelectorAll("[data-hold]").forEach((button) => {
    button.addEventListener("click", () => postJSON("/api/status", {
      sscc: button.dataset.hold,
      quality_status: "暂扣",
      reason: "前端快速暂扣",
    }));
  });
  contentEl.querySelectorAll("[data-release]").forEach((button) => {
    button.addEventListener("click", () => postJSON("/api/status", {
      sscc: button.dataset.release,
      quality_status: "合格",
      reason: "前端快速放行",
    }));
  });
  contentEl.querySelectorAll("[data-generate-smart-wave]").forEach((button) => {
    button.addEventListener("click", () => postJSON("/api/smart/waves/generate", {
      dock: button.dataset.generateSmartWave,
      route: button.dataset.route,
      remark: "智能中心按月台/线路自动组波",
    }));
  });
  contentEl.querySelectorAll("[data-apply-safety]").forEach((button) => {
    button.addEventListener("click", () => postJSON("/api/smart/safety/apply", {
      goods_id: button.dataset.applySafety,
      safety_qty: button.dataset.safety,
      reason: "智能中心应用动态安全库存建议",
    }));
  });
  contentEl.querySelectorAll("[data-apply-location]").forEach((button) => {
    button.addEventListener("click", () => {
      const select = document.querySelector("#inboundForm select[name='location_id']");
      if (select) {
        select.value = button.dataset.applyLocation;
        showNotice(`已应用推荐库位：${button.dataset.applyLocation}`);
      } else {
        app.page = "inbound";
        app.sections.inbound = "receive";
        render();
        const target = document.querySelector("#inboundForm select[name='location_id']");
        if (target) {
          target.value = button.dataset.applyLocation;
        }
        showNotice(`已切换到收货上架并应用推荐库位：${button.dataset.applyLocation}`);
      }
    });
  });
  const startQrBtn = document.querySelector("#startQrBtn");
  if (startQrBtn) startQrBtn.addEventListener("click", startQrScanner);
  const stopQrBtn = document.querySelector("#stopQrBtn");
  if (stopQrBtn) stopQrBtn.addEventListener("click", stopQrScanner);
  const startModelCameraBtn = document.querySelector("#startModelCameraBtn");
  if (startModelCameraBtn) startModelCameraBtn.addEventListener("click", startModelCamera);
  const stopModelCameraBtn = document.querySelector("#stopModelCameraBtn");
  if (stopModelCameraBtn) stopModelCameraBtn.addEventListener("click", stopModelCamera);
  const captureModelBtn = document.querySelector("#captureModelBtn");
  if (captureModelBtn) captureModelBtn.addEventListener("click", captureModelFrame);
  const printCurrentLabelBtn = document.querySelector("#printCurrentLabelBtn");
  if (printCurrentLabelBtn) printCurrentLabelBtn.addEventListener("click", printCurrentLabel);
}

async function downloadExcel(dataset) {
  try {
    const response = await fetch(`/api/export?dataset=${encodeURIComponent(dataset)}`);
    if (response.status === 401) {
      const data = await response.json().catch(() => ({}));
      app.data = null;
      showLogin(data.error || "请先登录");
      return;
    }
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      showNotice(data.error || "导出失败", true);
      return;
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileNameFromDisposition(response.headers.get("Content-Disposition"), `YuWMS_${dataset}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showNotice("导出完成");
  } catch (error) {
    showNotice(`导出失败：${error.message}`, true);
  }
}

function bindExcelImport(form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const file = formData.get("file");
    if (!file || !file.name) {
      showNotice("请选择 Excel 或 CSV 文件", true);
      return;
    }
    const response = await fetch("/api/import", {
      method: "POST",
      body: formData,
    });
    const data = await response.json().catch(() => ({ error: "导入失败" }));
    if (response.status === 401) {
      app.data = null;
      showLogin(data.error || "请先登录");
      return;
    }
    if (!response.ok) {
      showNotice(data.error || "导入失败", true);
      return;
    }
    app.data = data;
    form.reset();
    render();
    showNotice(data.notice || "导入完成");
  });
}

function bindSubmit(form, path) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    form.querySelectorAll("input[type=checkbox]").forEach((box) => {
      payload[box.name] = box.checked;
    });
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "") delete payload[key];
    });
    const result = await postJSON(path, payload);
    if (result) form.reset();
  });
}

function bindWaveActionSubmit(form, action) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    const waveId = String(payload.wave_id || "").trim();
    if (!waveId) {
      showNotice("请选择波次", true);
      return;
    }
    delete payload.wave_id;
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "") delete payload[key];
    });
    const result = await postJSON(`/api/finished/waves/${encodeURIComponent(waveId)}/${action}`, payload);
    if (result) form.reset();
  });
}

function bindTmsActionSubmit(form, action) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    const shipmentId = String(payload.shipment_id || "").trim();
    if (!shipmentId) {
      showNotice("请选择TMS运单", true);
      return;
    }
    delete payload.shipment_id;
    Object.keys(payload).forEach((key) => {
      if (payload[key] === "") delete payload[key];
    });
    const result = await postJSON(`/api/tms/shipments/${encodeURIComponent(shipmentId)}/${action}`, payload);
    if (result) form.reset();
  });
}

async function startQrScanner() {
  const video = document.querySelector("#qrVideo");
  if (!video) return;
  if (!navigator.mediaDevices?.getUserMedia) {
    showNotice("当前浏览器不支持摄像头", true);
    return;
  }
  try {
    stopQrScanner();
    app.qrStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    video.srcObject = app.qrStream;
    await video.play();
    if (!("BarcodeDetector" in window)) {
      showNotice("摄像头已开启，当前浏览器不支持自动识别二维码", true);
      return;
    }
    const detector = new BarcodeDetector({ formats: ["qr_code", "code_128", "ean_13"] });
    app.qrTimer = window.setInterval(async () => {
      try {
        const codes = await detector.detect(video);
        if (!codes.length) return;
        const value = codes[0].rawValue || "";
        const input = document.querySelector("#rfScanInput");
        if (input) input.value = value;
        stopQrScanner();
        await postJSON("/api/scans", { code: value, scan_type: "摄像头", action: "查询" });
      } catch (error) {
        showNotice(`扫码识别失败：${error.message}`, true);
        stopQrScanner();
      }
    }, 700);
    showNotice("摄像头扫码已开启");
  } catch (error) {
    showNotice(`摄像头开启失败：${error.message}`, true);
  }
}

function stopQrScanner() {
  if (app.qrTimer) {
    window.clearInterval(app.qrTimer);
    app.qrTimer = null;
  }
  if (app.qrStream) {
    app.qrStream.getTracks().forEach((track) => track.stop());
    app.qrStream = null;
  }
  const video = document.querySelector("#qrVideo");
  if (video) video.srcObject = null;
}

async function startModelCamera() {
  const video = document.querySelector("#modelVideo");
  if (!video) return;
  if (!navigator.mediaDevices?.getUserMedia) {
    showNotice("当前浏览器不支持摄像头", true);
    return;
  }
  try {
    stopModelCamera();
    app.modelStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    video.srcObject = app.modelStream;
    await video.play();
    showNotice("建模摄像头已开启");
  } catch (error) {
    showNotice(`摄像头开启失败：${error.message}`, true);
  }
}

function stopModelCamera() {
  if (app.modelStream) {
    app.modelStream.getTracks().forEach((track) => track.stop());
    app.modelStream = null;
  }
  const video = document.querySelector("#modelVideo");
  if (video) video.srcObject = null;
}

async function captureModelFrame() {
  const form = document.querySelector("#cameraModelForm");
  if (!form) return;
  const payload = Object.fromEntries(new FormData(form).entries());
  Object.keys(payload).forEach((key) => {
    if (payload[key] === "") delete payload[key];
  });
  payload.capture_mode = "browser-camera";
  payload.source = app.modelStream ? "live-camera" : "manual";
  const result = await postJSON("/api/camera-scans", payload);
  if (result) stopModelCamera();
}

function fileNameFromDisposition(header, fallback) {
  if (!header) return fallback;
  const encoded = header.match(/filename\*=UTF-8''([^;]+)/i);
  if (encoded) return decodeURIComponent(encoded[1]);
  const basic = header.match(/filename="?([^";]+)"?/i);
  return basic ? basic[1] : fallback;
}

function printPickTicket(outboundId) {
  const order = [
    ...(app.data.outbounds || []),
    ...(app.data.finished?.outbounds || []),
    ...(app.data.packaging?.outbounds || []),
  ].find((item) => item.id === outboundId);
  if (!order) return;
  const lines = order.lines.map((line) => `
    <tr>
      <td>${escapeHTML(line.sscc)}</td>
      <td>${escapeHTML(line.location_id)}</td>
      <td>${fmt(line.qty)}</td>
      <td></td>
    </tr>
  `).join("");
  let sheet = document.querySelector(".print-sheet");
  if (!sheet) {
    sheet = document.createElement("section");
    sheet.className = "print-sheet";
    document.body.appendChild(sheet);
  }
  sheet.innerHTML = `
    <h1>分拣单</h1>
    <p>出库单：${escapeHTML(order.id)}　货品：${escapeHTML(order.goods_id)} ${escapeHTML(order.goods_name)}　去向：${escapeHTML(order.destination)}</p>
    <p>需求：${fmt(order.qty)}　分配：${fmt(order.allocated_qty)}　料仓：${escapeHTML(order.bin_no || "")}</p>
    <table>
      <thead><tr><th>SSCC</th><th>库位</th><th>数量</th><th>复核签名</th></tr></thead>
      <tbody>${lines}</tbody>
    </table>
  `;
  window.print();
}

function printCurrentLabel() {
  const label = app.data.current_label;
  if (!label) {
    showNotice("请先生成标签", true);
    return;
  }
  let sheet = document.querySelector(".print-sheet");
  if (!sheet) {
    sheet = document.createElement("section");
    sheet.className = "print-sheet";
    document.body.appendChild(sheet);
  }
  const copies = Math.max(1, Math.min(99, Number(label.copies || 1)));
  sheet.innerHTML = `
    <div class="label-print-sheet">
      ${Array.from({ length: copies }, () => labelCardHTML(label, true)).join("")}
    </div>
  `;
  window.print();
}

function labelCardHTML(label, printMode = false) {
  const showBarcode = String(label.code_type || "").includes("条码");
  const showQr = String(label.code_type || "").includes("二维码");
  const qrPayload = qrSafeText(label.qr_value || label.id || label.barcode_value);
  const labelClass = label.label_type === "产品标签" ? "product" : "raw";
  return `
    <article class="wms-label ${labelClass} ${printMode ? "print" : ""}">
      <header>
        <div>
          <strong>${escapeHTML(label.label_type || "标签")}</strong>
          <small>${escapeHTML(label.template_name || "")}</small>
        </div>
        <b class="mono">${escapeHTML(label.id || "")}</b>
      </header>
      <div class="label-title">
        <span class="mono">${escapeHTML(label.goods_id || "")}</span>
        <h2>${escapeHTML(label.goods_name || "")}</h2>
      </div>
      <div class="label-fields">
        <div><small>批号</small><strong class="mono">${escapeHTML(label.batch_no || "")}</strong></div>
        <div><small>供应商/生产批次</small><strong class="mono">${escapeHTML(label.supplier_batch || "-")}</strong></div>
        <div><small>数量</small><strong>${fmt(label.qty)} ${escapeHTML(label.unit || "")}</strong></div>
        <div><small>品质</small><strong>${escapeHTML(label.quality_status || "")}</strong></div>
        <div><small>生产日期</small><strong>${escapeHTML(label.production_date || "-")}</strong></div>
        <div><small>BBD/有效期</small><strong>${escapeHTML(label.expiry_date || "-")}</strong></div>
        <div><small>库位</small><strong class="mono">${escapeHTML(label.location_id || "-")}</strong></div>
        <div><small>SSCC</small><strong class="mono">${escapeHTML(label.sscc || "-")}</strong></div>
      </div>
      <div class="label-codes ${showBarcode && showQr ? "two" : ""}">
        ${showBarcode ? `<div class="barcode-box">${code128Svg(label.barcode_value || label.id || "")}<small class="mono">${escapeHTML(label.barcode_value || "")}</small></div>` : ""}
        ${showQr ? `<div class="qr-box">${qrCodeSvg(qrPayload)}<small class="mono">${escapeHTML(qrPayload)}</small></div>` : ""}
      </div>
      <footer>
        <span>生成：${escapeHTML(label.ts || "")}</span>
        <span>${escapeHTML(label.operator || "")}</span>
      </footer>
    </article>
  `;
}

const CODE128_PATTERNS = [
  "212222", "222122", "222221", "121223", "121322", "131222", "122213", "122312", "132212", "221213",
  "221312", "231212", "112232", "122132", "122231", "113222", "123122", "123221", "223211", "221132",
  "221231", "213212", "223112", "312131", "311222", "321122", "321221", "312212", "322112", "322211",
  "212123", "212321", "232121", "111323", "131123", "131321", "112313", "132113", "132311", "211313",
  "231113", "231311", "112133", "112331", "132131", "113123", "113321", "133121", "313121", "211331",
  "231131", "213113", "213311", "213131", "311123", "311321", "331121", "312113", "312311", "332111",
  "314111", "221411", "431111", "111224", "111422", "121124", "121421", "141122", "141221", "112214",
  "112412", "122114", "122411", "142112", "142211", "241211", "221114", "413111", "241112", "134111",
  "111242", "121142", "121241", "114212", "124112", "124211", "411212", "421112", "421211", "212141",
  "214121", "412121", "111143", "111341", "131141", "114113", "114311", "411113", "411311", "113141",
  "114131", "311141", "411131", "211412", "211214", "211232", "2331112",
];

function code128Svg(value) {
  const text = String(value || "").replace(/[^\x20-\x7e]/g, "").slice(0, 48) || "WMS-LABEL";
  const codes = [104, ...Array.from(text, (char) => char.charCodeAt(0) - 32)];
  let checksum = 104;
  for (let index = 1; index < codes.length; index += 1) checksum += codes[index] * index;
  codes.push(checksum % 103, 106);
  const moduleWidth = 2;
  const height = 64;
  let x = 0;
  const rects = [];
  codes.forEach((code) => {
    const pattern = CODE128_PATTERNS[code];
    Array.from(pattern).forEach((widthChar, index) => {
      const width = Number(widthChar) * moduleWidth;
      if (index % 2 === 0) {
        rects.push(`<rect x="${x}" y="0" width="${width}" height="${height}" fill="#111827"/>`);
      }
      x += width;
    });
  });
  return `<svg class="barcode-svg" viewBox="0 0 ${x} ${height}" role="img" aria-label="barcode">${rects.join("")}</svg>`;
}

function qrSafeText(value) {
  const text = String(value || "WMS-LABEL");
  return utf8Bytes(text).length <= 32 ? text : text.slice(0, 28);
}

function qrCodeSvg(value) {
  const size = 25;
  const modules = Array.from({ length: size }, () => Array(size).fill(false));
  const reserved = Array.from({ length: size }, () => Array(size).fill(false));
  const set = (row, col, dark, isReserved = true) => {
    if (row < 0 || col < 0 || row >= size || col >= size) return;
    modules[row][col] = !!dark;
    if (isReserved) reserved[row][col] = true;
  };
  const finder = (row, col) => {
    for (let r = -1; r <= 7; r += 1) {
      for (let c = -1; c <= 7; c += 1) {
        const rr = row + r;
        const cc = col + c;
        const dark = r >= 0 && r <= 6 && c >= 0 && c <= 6 && (r === 0 || r === 6 || c === 0 || c === 6 || (r >= 2 && r <= 4 && c >= 2 && c <= 4));
        set(rr, cc, dark, true);
      }
    }
  };
  finder(0, 0);
  finder(0, size - 7);
  finder(size - 7, 0);
  for (let i = 8; i < size - 8; i += 1) {
    set(6, i, i % 2 === 0, true);
    set(i, 6, i % 2 === 0, true);
  }
  for (let r = 16; r <= 20; r += 1) {
    for (let c = 16; c <= 20; c += 1) {
      set(r, c, r === 16 || r === 20 || c === 16 || c === 20 || (r === 18 && c === 18), true);
    }
  }
  set(17, 8, true, true);
  for (let i = 0; i < 9; i += 1) {
    reserved[8][i] = true;
    reserved[i][8] = true;
    reserved[8][size - 1 - i] = true;
    reserved[size - 1 - i][8] = true;
  }

  const dataCodewords = qrDataCodewords(qrSafeText(value));
  const codewords = [...dataCodewords, ...qrReedSolomon(dataCodewords, 10)];
  const bits = [];
  codewords.forEach((word) => {
    for (let bit = 7; bit >= 0; bit -= 1) bits.push((word >>> bit) & 1);
  });
  let bitIndex = 0;
  let upward = true;
  for (let col = size - 1; col > 0; col -= 2) {
    if (col === 6) col -= 1;
    for (let rowStep = 0; rowStep < size; rowStep += 1) {
      const row = upward ? size - 1 - rowStep : rowStep;
      for (let c = col; c >= col - 1; c -= 1) {
        if (reserved[row][c]) continue;
        let bit = bitIndex < bits.length ? bits[bitIndex] : 0;
        if ((row + c) % 2 === 0) bit ^= 1;
        modules[row][c] = !!bit;
        bitIndex += 1;
      }
    }
    upward = !upward;
  }
  placeQrFormat(modules, size, 0);
  const cell = 5;
  const quiet = 4;
  const total = (size + quiet * 2) * cell;
  const rects = [];
  modules.forEach((row, r) => row.forEach((dark, c) => {
    if (dark) rects.push(`<rect x="${(c + quiet) * cell}" y="${(r + quiet) * cell}" width="${cell}" height="${cell}"/>`);
  }));
  return `<svg class="qr-svg" viewBox="0 0 ${total} ${total}" role="img" aria-label="qr"><rect width="${total}" height="${total}" fill="#fff"/>${rects.join("")}</svg>`;
}

function qrDataCodewords(value) {
  const bytes = utf8Bytes(value).slice(0, 32);
  const bits = [];
  const append = (valueToAppend, length) => {
    for (let bit = length - 1; bit >= 0; bit -= 1) bits.push((valueToAppend >>> bit) & 1);
  };
  append(4, 4);
  append(bytes.length, 8);
  bytes.forEach((byte) => append(byte, 8));
  const capacity = 34 * 8;
  const terminator = Math.min(4, capacity - bits.length);
  for (let i = 0; i < terminator; i += 1) bits.push(0);
  while (bits.length % 8) bits.push(0);
  const words = [];
  for (let i = 0; i < bits.length; i += 8) {
    words.push(bits.slice(i, i + 8).reduce((acc, bit) => (acc << 1) | bit, 0));
  }
  const pads = [0xec, 0x11];
  let padIndex = 0;
  while (words.length < 34) {
    words.push(pads[padIndex % 2]);
    padIndex += 1;
  }
  return words.slice(0, 34);
}

function utf8Bytes(value) {
  if (typeof TextEncoder !== "undefined") return Array.from(new TextEncoder().encode(String(value)));
  return Array.from(String(value), (char) => char.charCodeAt(0) & 0xff);
}

function qrReedSolomon(data, eccLen) {
  const generator = qrGeneratorPoly(eccLen);
  const result = Array(eccLen).fill(0);
  data.forEach((byte) => {
    const factor = byte ^ result.shift();
    result.push(0);
    for (let i = 0; i < eccLen; i += 1) {
      result[i] ^= qrGfMul(generator[i + 1], factor);
    }
  });
  return result;
}

function qrGeneratorPoly(degree) {
  let poly = [1];
  for (let i = 0; i < degree; i += 1) {
    const next = Array(poly.length + 1).fill(0);
    poly.forEach((coef, index) => {
      next[index] ^= coef;
      next[index + 1] ^= qrGfMul(coef, qrGfPow(2, i));
    });
    poly = next;
  }
  return poly;
}

function qrGfPow(value, power) {
  let result = 1;
  for (let i = 0; i < power; i += 1) result = qrGfMul(result, value);
  return result;
}

function qrGfMul(a, b) {
  let result = 0;
  let aa = a;
  let bb = b;
  while (bb > 0) {
    if (bb & 1) result ^= aa;
    aa <<= 1;
    if (aa & 0x100) aa ^= 0x11d;
    bb >>= 1;
  }
  return result & 0xff;
}

function placeQrFormat(modules, size, mask) {
  const format = qrFormatBits(1, mask);
  const setBit = (row, col, index) => {
    modules[row][col] = !!((format >>> index) & 1);
  };
  for (let i = 0; i <= 5; i += 1) setBit(8, i, i);
  setBit(8, 7, 6);
  setBit(8, 8, 7);
  setBit(7, 8, 8);
  for (let i = 9; i < 15; i += 1) setBit(14 - i, 8, i);
  for (let i = 0; i < 8; i += 1) setBit(size - 1 - i, 8, i);
  for (let i = 8; i < 15; i += 1) setBit(8, size - 15 + i, i);
}

function qrFormatBits(errorLevel, mask) {
  const data = (errorLevel << 3) | mask;
  let bits = data << 10;
  const generator = 0x537;
  for (let i = 14; i >= 10; i -= 1) {
    if ((bits >>> i) & 1) bits ^= generator << (i - 10);
  }
  return ((data << 10) | bits) ^ 0x5412;
}

function table(headers, rows) {
  return `
    <div class="table-scroll">
      <table>
        <thead><tr>${headers.map((item) => `<th>${escapeHTML(item)}</th>`).join("")}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function emptyRow(colspan) {
  return `<tr><td colspan="${colspan}"><div class="empty">没有匹配数据</div></td></tr>`;
}

function filterRows(rows) {
  if (!app.search) return rows;
  return rows.filter((row) => JSON.stringify(row).toLowerCase().includes(app.search));
}

function allocationLines(lines) {
  return `
    <div class="mini-list">
      ${lines.map((line) => `
        <div class="mini-row">
          <div>
            <strong class="mono">${escapeHTML(line.sscc)}</strong>
            <small>${escapeHTML(line.goods_name)} / ${escapeHTML(line.location_id)}</small>
          </div>
          <div class="num">${fmt(line.qty)} ${pill(line.status, line.status === "已确认" ? "ok" : "info")}</div>
        </div>
      `).join("")}
    </div>
  `;
}

function stockMiniRow(item) {
  return `
    <div class="mini-row">
      <div>
        <strong class="mono">${escapeHTML(item.sscc)}</strong>
        <small>${escapeHTML(item.goods_id)} ${escapeHTML(item.goods_name)} / ${escapeHTML(item.location_id)} / BBD ${escapeHTML(item.expiry_date || "-")} ${item.expiry_status_label ? `/${escapeHTML(item.expiry_status_label)}` : ""}</small>
      </div>
      <div class="num">${fmt(item.available_qty)} ${escapeHTML(item.unit)}</div>
    </div>
  `;
}

function productOptions(category = "") {
  return app.data.products
    .filter((item) => !category || item.category === category)
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.name)}</option>`)
    .join("");
}

function channelOptions() {
  const seen = new Map();
  (app.data.tms?.channel_rules || []).forEach((item) => {
    if (!seen.has(item.channel_code)) seen.set(item.channel_code, item.channel_name);
  });
  const options = Array.from(seen.entries())
    .map(([code, name]) => `<option value="${escapeAttr(code)}">${escapeHTML(code)}　${escapeHTML(name)}</option>`)
    .join("");
  return options || `<option value="ECOM">ECOM　电商平台</option><option value="DISTRIBUTOR">DISTRIBUTOR　经销商</option><option value="KA">KA　KA商超</option><option value="EXPORT">EXPORT　出口</option>`;
}

function finishedWaveOptions(waves, statuses = []) {
  const options = (waves || [])
    .filter((wave) => !statuses.length || statuses.includes(wave.status))
    .map((wave) => `<option value="${escapeAttr(wave.id)}">${escapeHTML(wave.id)}　${escapeHTML(wave.status)} / ${escapeHTML(wave.dock || "-")}</option>`)
    .join("");
  return options || `<option value="">暂无可选波次</option>`;
}

function finishedWaveOrderOptions(waves, statuses = []) {
  const options = (waves || []).flatMap((wave) => (wave.orders || [])
    .filter((order) => !statuses.length || statuses.includes(order.status))
    .map((order) => `<option value="${escapeAttr(order.outbound_id)}">${escapeHTML(order.outbound_id)}　${escapeHTML(order.status)} / ${escapeHTML(order.destination || "-")}</option>`))
    .join("");
  return options || `<option value="">暂无可选发货单</option>`;
}

function rawProductOptions() {
  return app.data.products
    .filter((item) => item.category !== "成品")
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.name)} / ${escapeHTML(item.category)}</option>`)
    .join("");
}

function locationOptions(area = "") {
  return app.data.locations
    .filter((item) => !area || item.area === area)
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.zone)}</option>`)
    .join("");
}

function sparePartOptions() {
  return (app.data.spares?.parts || [])
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.name)} / ${escapeHTML(item.location || "-")}</option>`)
    .join("");
}

function tmsShipmentOptions(shipments = []) {
  const options = (shipments || [])
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.status)} / ${escapeHTML(item.customer || item.destination || "-")}</option>`)
    .join("");
  return options || `<option value="">暂无TMS运单</option>`;
}

function tmsCarrierOptions(carriers = []) {
  return (carriers || [])
    .map((item) => `<option value="${escapeAttr(item.code)}">${escapeHTML(item.code)}　${escapeHTML(item.name)}</option>`)
    .join("");
}

function tmsLaneOptions(lanes = []) {
  return (lanes || [])
    .map((item) => `<option value="${escapeAttr(item.code)}">${escapeHTML(item.code)}　${escapeHTML(item.destination)} / ${escapeHTML(item.carrier_code)}</option>`)
    .join("");
}

function tmsOutboundOptions() {
  const existing = new Set((app.data.tms?.shipments || []).map((item) => item.source_outbound_id).filter(Boolean));
  const rows = (app.data.finished?.outbounds || [])
    .filter((item) => !existing.has(item.id))
    .map((item) => `<option value="${escapeAttr(item.id)}">${escapeHTML(item.id)}　${escapeHTML(item.status)} / ${escapeHTML(item.goods_name)} / ${escapeHTML(item.destination)}</option>`)
    .join("");
  return rows || `<option value="">暂无可生成运输单的成品发货单</option>`;
}

function qualityOptions(selected) {
  return ["合格", "待检", "暂扣", "隔离", "冻结"].map((item) => `
    <option ${item === selected ? "selected" : ""}>${item}</option>
  `).join("");
}

function textField(name, label, placeholder = "") {
  return `
    <label class="field">${escapeHTML(label)}
      <input name="${escapeAttr(name)}" placeholder="${escapeAttr(placeholder)}">
    </label>
  `;
}

function numberField(name, label, placeholder = "") {
  return `
    <label class="field">${escapeHTML(label)}
      <input name="${escapeAttr(name)}" type="number" step="0.001" min="0" placeholder="${escapeAttr(placeholder)}">
    </label>
  `;
}

function dateField(name, label) {
  return `
    <label class="field">${escapeHTML(label)}
      <input name="${escapeAttr(name)}" type="date">
    </label>
  `;
}

function selectField(name, label, options) {
  return `
    <label class="field">${escapeHTML(label)}
      <select name="${escapeAttr(name)}">${options}</select>
    </label>
  `;
}

function textAreaField(name, label, placeholder = "") {
  return `
    <label class="field full">${escapeHTML(label)}
      <textarea name="${escapeAttr(name)}" placeholder="${escapeAttr(placeholder)}"></textarea>
    </label>
  `;
}

function statusPill(status) {
  if (status === "成功") return pill(status, "ok");
  if (status === "失败" || status === "异常" || status === "签收异常") return pill(status, "bad");
  if (status === "待处理" || status === "差异") return pill(status, "warn");
  if (status === "已签收" || status === "已确认" || status === "已生成") return pill(status, "ok");
  if (status === "待发车" || status === "待接单") return pill(status, "warn");
  if (status === "已接单" || status === "已发车" || status === "在途" || status === "到达待签收") return pill(status, "info");
  if (status === "已完成") return pill(status, "ok");
  if (status === "已发货") return pill(status, "ok");
  if (status === "已复核" || status === "已拣货" || status === "已创建") return pill(status, "info");
  if (status === "波次拣货中" || status === "拣货中" || status === "复核中" || status === "待拣货") return pill(status, "warn");
  if (status === "欠品") return pill(status, "bad");
  if (status === "已分配") return pill(status, "info");
  return pill(status, "");
}

function smartSeverityPill(severity) {
  if (severity === "高") return pill("高风险", "bad");
  if (severity === "中") return pill("中风险", "warn");
  return pill("低风险", "info");
}

function safetyActionPill(action) {
  if (action === "建议调高") return pill(action, "bad");
  if (action === "建议下调") return pill(action, "warn");
  return pill(action || "保持", "ok");
}

function qualityPill(status) {
  if (status === "合格") return pill(status, "ok");
  if (status === "暂扣") return pill(status, "bad");
  if (status === "冻结" || status === "隔离") return pill(status, "warn");
  return pill(status || "", "info");
}

function scanTypePill(type) {
  if (type === "SSCC") return pill("SSCC", "ok");
  if (type === "LOCATION") return pill("库位", "info");
  if (type === "GOODS") return pill("货品", "warn");
  return pill(type || "未匹配", "bad");
}

function modelStatusPill(status) {
  if (status === "正常") return pill(status, "ok");
  if (status === "空闲") return pill(status, "info");
  if (status === "高占用" || status === "暂扣") return pill(status, "warn");
  if (status === "需复核") return pill(status, "bad");
  return pill(status || "", "");
}

function modelStatusClass(status) {
  if (status === "正常") return "ok";
  if (status === "空闲") return "free";
  if (status === "高占用" || status === "暂扣") return "warn";
  if (status === "需复核") return "bad";
  return "";
}

function spareStatusPill(status, label) {
  if (status === "red") return pill(label || "红色预警", "bad");
  if (status === "orange") return pill(label || "橙色预警", "warn");
  if (status === "yellow") return pill(label || "黄色预警", "info");
  return pill(label || "正常", "ok");
}

function spareActionPill(action) {
  if (action.includes("入库") || action.includes("退库") || action.includes("初始化")) return pill(action, "ok");
  if (action.includes("领用")) return pill(action, "info");
  if (action.includes("报废")) return pill(action, "bad");
  if (action.includes("盘点")) return pill(action, "warn");
  return pill(action, "");
}

function stockStatusPill(item) {
  const type = item.stock_status === "red" ? "bad" : item.stock_status === "yellow" ? "warn" : "ok";
  return pill(item.stock_status_label || "正常", type);
}

function expiryDatePill(item) {
  if (!item?.expiry_date) return "";
  return pill(item.expiry_date, item.expiry_status || expiryStatus(item.expiry_date, item.expiry_alert_days));
}

function expiryStatusPill(item) {
  if (!item?.expiry_status_label) return "";
  return pill(item.expiry_status_label, item.expiry_status || "");
}

function pill(text, type) {
  return `<span class="pill ${type || ""}">${escapeHTML(String(text))}</span>`;
}

function expiryStatus(value, alertDays = 60) {
  if (!value) return "";
  const today = new Date();
  const expiry = new Date(`${value}T00:00:00`);
  const days = (expiry - today) / 86400000;
  if (days < 0) return "bad";
  if (days <= Number(alertDays || 60)) return "warn";
  return "ok";
}

function fmt(value) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (Number.isNaN(number)) return escapeHTML(String(value));
  return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 3 }).format(number);
}

function escapeHTML(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttr(value) {
  return escapeHTML(value);
}

loadData();
