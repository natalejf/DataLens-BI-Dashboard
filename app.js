'use strict';

const MAX_FILE_SIZE = 50 * 1024 * 1024;
const MAX_ROWS_TABLE = 100;
const CHART_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316'];

let rawData = [];
let filteredData = [];
let currentColumns = [];
let columnAnalysis = [];
let charts = [];
let chartConfigsBase = [];
let loadedFiles = [];
let activeFiles = [];
let currentAnalysisMode = 'combined';
let workbook = null;
let activeFilter = null; // { col: 'Zona', val: 'Norte' }

function $(id) {
    return document.getElementById(id);
}

function safeSetText(id, text) {
    const el = $(id);
    if (el) el.textContent = text;
}

function safeSetHtml(id, html) {
    const el = $(id);
    if (el) el.innerHTML = html;
}

function safeSetHidden(id, hidden) {
    const el = $(id);
    if (el) el.hidden = hidden;
}

function safeSetDisabled(id, disabled) {
    const el = $(id);
    if (el) el.disabled = disabled;
}

function init() {
    setupEventListeners();
    loadTheme();
    if (window.innerWidth < 768) {
        const sidebar = document.querySelector('.bi-sidebar');
        const btnExpandSidebar = $('btnExpandSidebar');
        if (sidebar) sidebar.classList.add('collapsed');
        if (btnExpandSidebar) btnExpandSidebar.hidden = false;
    }
}

function setupEventListeners() {
    // Sidebar toggle
    const btnToggleSidebar = $('btnToggleSidebar');
    const btnExpandSidebar = $('btnExpandSidebar');
    const mobileMenuToggleBar = $('mobileMenuToggleBar');
    const sidebar = document.querySelector('.bi-sidebar');

    function toggleSidebar() {
        if (!sidebar) return;
        const isCollapsed = sidebar.classList.toggle('collapsed');
        if (btnExpandSidebar) {
            btnExpandSidebar.hidden = !isCollapsed;
        }
        if (mobileMenuToggleBar) {
            mobileMenuToggleBar.classList.toggle('expanded', !isCollapsed);
        }
        const resizeAllCharts = () => {
            charts.forEach(c => {
                if (c && typeof c.resize === 'function') c.resize();
            });
        };
        resizeAllCharts();
        setTimeout(resizeAllCharts, 100);
        setTimeout(resizeAllCharts, 260);
        setTimeout(resizeAllCharts, 350);
    }

    if (btnToggleSidebar) {
        btnToggleSidebar.addEventListener('click', toggleSidebar);
    }
    if (btnExpandSidebar) {
        btnExpandSidebar.addEventListener('click', toggleSidebar);
    }
    if (mobileMenuToggleBar) {
        mobileMenuToggleBar.addEventListener('click', toggleSidebar);
    }

    // Header buttons
    const btnNew = $('btnNew');
    const fileInput = $('fileInput');
    if (btnNew && fileInput) {
        btnNew.addEventListener('click', () => fileInput.click());
    }
    
    const btnRefresh = $('btnRefresh');
    if (btnRefresh) btnRefresh.addEventListener('click', () => renderReport());
    
    const btnCaptureDashboard = $('btnCaptureDashboard');
    if (btnCaptureDashboard) btnCaptureDashboard.addEventListener('click', captureDashboardScreenshot);
    
    const btnExport = $('btnExport');
    if (btnExport) btnExport.addEventListener('click', exportReportJSON);
    
    const btnGenerateReport = $('btnGenerateReport');
    if (btnGenerateReport) btnGenerateReport.addEventListener('click', () => {
        switchToRightTab('report');
        generateExecutiveReport();
    });

    // File search
    const fileSearchInput = $('fileSearchInput');
    if (fileSearchInput) {
        fileSearchInput.addEventListener('input', () => renderLoadedFiles());
    }

    // Right Sidebar Tabs
    const tabInsightsBtn = $('tabInsightsBtn');
    const tabReportBtn = $('tabReportBtn');
    if (tabInsightsBtn) tabInsightsBtn.addEventListener('click', () => switchToRightTab('insights'));
    if (tabReportBtn) tabReportBtn.addEventListener('click', () => {
        switchToRightTab('report');
        generateExecutiveReport();
    });

    const btnRunReportEngine = $('btnRunReportEngine');
    if (btnRunReportEngine) btnRunReportEngine.addEventListener('click', generateExecutiveReport);

    const btnCopyReportText = $('btnCopyReportText');
    if (btnCopyReportText) btnCopyReportText.addEventListener('click', copyReportToClipboard);
    
    const themeToggle = $('themeToggle');
    if (themeToggle) themeToggle.addEventListener('click', toggleTheme);

    // Upload zone
    const uploadZone = $('uploadZone');
    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', (e) => {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });
        uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
        uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                Array.from(e.dataTransfer.files).forEach(f => handleFile(f));
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', (e) => { 
            if (e.target.files.length) {
                Array.from(e.target.files).forEach(f => handleFile(f));
                fileInput.value = ''; // Reset so the same file can be chosen again if needed
            }
        });
    }

    // Sheet select & Filters
    const sheetSelect = $('sheetSelect');
    if (sheetSelect) sheetSelect.addEventListener('change', changeSheet);
    
    const clearFilterBtn = $('clearFilterBtn');
    if (clearFilterBtn) clearFilterBtn.addEventListener('click', clearFilter);
    
    // Segmented Control
    document.querySelectorAll('.seg-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAnalysisMode = btn.dataset.mode;
            generateChartConfigs();
            renderReport();
        });
    });
    
    // Guide Modal
    const btnGuide = $('btnGuide');
    if (btnGuide) btnGuide.addEventListener('click', openGuideModal);
    
    const guideCloseBtn = $('guideCloseBtn');
    if (guideCloseBtn) guideCloseBtn.addEventListener('click', closeGuideModal);

    // Modals
    const modalCloseBtn = $('modalCloseBtn');
    if (modalCloseBtn) modalCloseBtn.addEventListener('click', () => safeSetHidden('chartModal', true));
    
    const modalDownloadBtn = $('modalDownloadBtn');
    if (modalDownloadBtn) modalDownloadBtn.addEventListener('click', downloadPNG);
    
    const errorCloseBtn = $('errorCloseBtn');
    if (errorCloseBtn) errorCloseBtn.addEventListener('click', () => safeSetHidden('errorModal', true));
}

window.openGuideModal = function() {
    safeSetHidden('guideModal', false);
};

window.closeGuideModal = function() {
    safeSetHidden('guideModal', true);
};

window.copyPromptText = function(elementId) {
    const el = $(elementId);
    if (!el) return;
    const textToCopy = el.textContent || el.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const btns = document.querySelectorAll('.btn-copy-prompt');
        btns.forEach(b => {
            const originalText = b.textContent;
            b.textContent = '✅ ¡Copiado!';
            b.style.background = 'var(--success)';
            setTimeout(() => {
                b.textContent = originalText;
                b.style.background = 'var(--accent)';
            }, 2000);
        });
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
};

function switchToRightTab(tab) {
    const isInsights = tab === 'insights';
    if ($('tabInsightsBtn')) $('tabInsightsBtn').classList.toggle('active', isInsights);
    if ($('tabReportBtn')) $('tabReportBtn').classList.toggle('active', !isInsights);
    safeSetHidden('insightsView', !isInsights);
    safeSetHidden('reportEngineView', isInsights);
    if (isInsights) {
        if ($('insightsView')) $('insightsView').classList.add('active');
        if ($('reportEngineView')) $('reportEngineView').classList.remove('active');
    } else {
        if ($('reportEngineView')) $('reportEngineView').classList.add('active');
        if ($('insightsView')) $('insightsView').classList.remove('active');
    }
}

function showState(stateId) {
    ['uploadState', 'reportState', 'loadingState'].forEach(id => {
        const el = $(id);
        if (el) {
            el.hidden = true;
            el.classList.remove('active');
        }
    });
    const target = $(stateId);
    if (target) {
        target.hidden = false;
        target.classList.add('active');
    }
}

function setLoading(msg, pct) {
    showState('loadingState');
    safeSetText('loadingMessage', msg);
    const loadingBar = $('loadingBar');
    if (loadingBar) loadingBar.style.width = pct + '%';
}

function showError(msg) {
    safeSetText('errorMessage', msg);
    safeSetHidden('errorModal', false);
    if (!rawData.length) showState('uploadState');
}

async function handleFile(file) {
    if (file.size > MAX_FILE_SIZE) { showError('El archivo supera 50MB'); return; }
    setLoading('Leyendo archivo...', 20);
    
    try {
        const ext = file.name.split('.').pop().toLowerCase();
        let data = [];
        if (['xlsx', 'xls'].includes(ext)) data = await parseExcel(file);
        else if (['csv', 'tsv', 'txt'].includes(ext)) data = await parseDelimited(file, ext);
        else if (ext === 'json') data = await parseJSON(file);
        else throw new Error('Formato no soportado');

        if (!data.length) throw new Error('El archivo no contiene datos legibles');

        setLoading('Analizando datos y categorías...', 70);
        
        data.forEach(r => r['Archivo_Origen'] = file.name);
        if (!loadedFiles.includes(file.name)) {
            loadedFiles.push(file.name);
            activeFiles.push(file.name);
        }
        
        if (rawData.length > 0) {
            rawData = [...rawData, ...data];
            safeSetText('fileName', 'Varios Archivos');
            safeSetText('dashboardTitle', 'DataLens BI Analytics Dashboard');
        } else {
            rawData = data;
            safeSetText('fileName', file.name);
            safeSetText('dashboardTitle', file.name.split('.')[0] + ' - Análisis Visual');
        }
        
        safeSetText('btnNewText', '+ Añadir Datos');
        safeSetText('uploadTitle', 'Añadir más datos');
        safeSetText('uploadDesc', 'Arrastra aquí para combinar archivos');

        filteredData = [...rawData];
        
        let allKeys = new Set();
        rawData.forEach(r => Object.keys(r).forEach(k => allKeys.add(k)));
        currentColumns = Array.from(allKeys).filter(c => !c.startsWith('__EMPTY'));
        
        columnAnalysis = analyzeColumns(rawData);
        
        safeSetHidden('fileInfo', false);
        safeSetDisabled('btnRefresh', false);
        safeSetDisabled('btnExport', false);
        safeSetDisabled('btnCaptureDashboard', false);
        
        renderLoadedFiles();
        renderFieldsList();
        generateChartConfigs();
        clearFilter();
        
        setLoading('Generando visualizaciones de categorías...', 100);
        setTimeout(() => {
            showState('reportState');
        }, 200);

    } catch (err) {
        showError(err.message);
    }
}

function parseExcel(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                workbook = XLSX.read(e.target.result, { type: 'array' });
                if (workbook.SheetNames.length > 1) {
                    const sel = $('sheetSelect');
                    if (sel) {
                        sel.innerHTML = workbook.SheetNames.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
                        safeSetHidden('sheetPicker', false);
                    }
                } else {
                    safeSetHidden('sheetPicker', true);
                }
                const sheet = workbook.SheetNames[0];
                resolve(XLSX.utils.sheet_to_json(workbook.Sheets[sheet], { defval: '' }));
            } catch (err) { reject(err); }
        };
        reader.onerror = () => reject(new Error('Error de lectura'));
        reader.readAsArrayBuffer(file);
    });
}

function parseDelimited(file, ext) {
    return new Promise((resolve, reject) => {
        Papa.parse(file, {
            delimiter: '',
            header: true, skipEmptyLines: true, dynamicTyping: false,
            complete: (r) => resolve(r.data), error: (e) => reject(e)
        });
    });
}

function parseJSON(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                let data = JSON.parse(e.target.result);
                if (!Array.isArray(data)) data = [data];
                const flatData = data.map(row => { const f = {}; flatten(row, f); return f; });
                resolve(flatData);
            } catch (err) { reject(err); }
        };
        reader.readAsText(file);
    });
}
function flatten(obj, result, prefix = '') {
    for (const key in obj) {
        if (!obj.hasOwnProperty(key)) continue;
        const newKey = prefix ? prefix + '.' + key : key;
        const val = obj[key];
        if (val && typeof val === 'object' && !Array.isArray(val)) flatten(val, result, newKey);
        else result[newKey] = val;
    }
}

function analyzeColumns(data) {
    return currentColumns.map(name => {
        const values = data.map(r => r[name]).filter(v => v !== '' && v != null);
        const type = detectType(name, values.slice(0, 100), values);
        const uniqueCount = new Set(values.map(String)).size;
        const cleanLabel = name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        return { name, cleanLabel, type, uniqueCount };
    });
}

function detectType(name, sample, allValues) {
    if (!sample.length) return 'unknown';
    const nameLower = String(name).toLowerCase();
    const unique = new Set(allValues.map(String)).size;
    
    // Si la columna tiene solo 1 valor único en todas las filas (constante), se clasifica como constante/descartable
    if (unique <= 1) return 'constant';

    // Si es un ID o código numérico interno, clasificar como id_code para no priorizarlo sobre nombres legibles de ciudades
    if (nameLower.endsWith('_id') || nameLower === 'id' || nameLower.includes('código') || nameLower.includes('codigo')) {
        return 'id_code';
    }

    const isNumericSample = sample.filter(v => !isNaN(Number(v))).length / sample.length > 0.8;
    const isDateSample = sample.filter(v => !isNaN(new Date(v).getTime()) && String(v).length > 5).length / sample.length > 0.7;

    // Si la columna contiene palabras clave explícitas de dimensión de negocio (ej. departamento, ciudad, provincia, cliente, etc.)
    const categoryKeywords = ['nombre', 'ciudad', 'departamento', 'provincia', 'localidad', 'municipio', 'distrito', 'zona', 'region', 'región', 'sucursal', 'pais', 'país', 'cliente', 'producto', 'categoria', 'categoría', 'marca', 'rubro', 'sector', 'vendedor', 'tipo', 'estado', 'campania', 'campaña'];
    if (categoryKeywords.some(kw => nameLower.includes(kw)) && !isNumericSample) {
        return 'categorical';
    }

    // Evitar sumarizar años
    if (nameLower === 'año' || nameLower === 'year' || nameLower === 'anio') {
        return 'categorical';
    }
    
    if (isNumericSample) return 'numeric';
    if (isDateSample) return 'temporal';
    if (unique < 2000 || unique / allValues.length < 0.5) return 'categorical';
    return 'text';
}

function renderLoadedFiles() {
    const listEl = $('loadedFilesList');
    if (!listEl) return;
    
    const filterTerm = ($('fileSearchInput') ? $('fileSearchInput').value : '').toLowerCase();
    const visibleFiles = loadedFiles.filter(f => f.toLowerCase().includes(filterTerm));
    
    if (visibleFiles.length === 0) {
        listEl.innerHTML = '<li class="empty-state" style="padding: 12px;">Sin archivos</li>';
        return;
    }
    
    listEl.innerHTML = visibleFiles.map(f => {
        const isChecked = activeFiles.includes(f) ? 'checked' : '';
        const ext = f.split('.').pop().toLowerCase();
        return `<li class="loaded-file-item">
            <div class="file-item-left">
                <input type="checkbox" class="file-checkbox" onchange="toggleFileVisibility('${escapeHtml(f)}', this.checked)" ${isChecked}>
                <span class="file-icon-badge ${ext}">${ext}</span>
                <span class="file-name-text" title="${escapeHtml(f)}">${escapeHtml(f)}</span>
            </div>
            <button class="file-remove-btn" title="Eliminar archivo" onclick="removeFile('${escapeHtml(f)}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
        </li>`;
    }).join('');
}

function toggleFileVisibility(fileName, isVisible) {
    if (isVisible) {
        if (!activeFiles.includes(fileName)) activeFiles.push(fileName);
    } else {
        activeFiles = activeFiles.filter(f => f !== fileName);
    }
    recalculateFilteredData();
}

function removeFile(fileName) {
    rawData = rawData.filter(r => r.Archivo_Origen !== fileName);
    loadedFiles = loadedFiles.filter(f => f !== fileName);
    activeFiles = activeFiles.filter(f => f !== fileName);
    if (rawData.length === 0) {
        loadedFiles = []; activeFiles = []; filteredData = []; currentColumns = []; columnAnalysis = []; globalFilters = {}; activeFilter = null; chartConfigsBase = [];
        safeSetHidden('fileInfo', true);
        safeSetHidden('globalFiltersContainer', true);
        showState('uploadState');
        safeSetDisabled('btnRefresh', true);
        safeSetDisabled('btnExport', true);
        safeSetDisabled('btnCaptureDashboard', true);
        return;
    }
    let allKeys = new Set();
    rawData.forEach(r => Object.keys(r).forEach(k => allKeys.add(k)));
    currentColumns = Array.from(allKeys).filter(c => !c.startsWith('__EMPTY'));
    columnAnalysis = analyzeColumns(rawData);
    
    safeSetText('fileName', loadedFiles.length > 1 ? 'Varios Archivos' : loadedFiles[0]);
    
    renderLoadedFiles();
    renderFieldsList();
    generateChartConfigs();
    clearFilter();
}

function renderFieldsList() {
    safeSetHidden('emptyFieldsMsg', true);
    renderSlicers();
}

// ----------------- SLICERS -----------------
let globalFilters = {};

function renderSlicers() {
    const slicerCols = columnAnalysis.filter(c => (c.type === 'categorical' || c.type === 'id_code' || c.type === 'temporal') && c.uniqueCount > 0 && c.uniqueCount <= 1000);
    if (slicerCols.length === 0) {
        safeSetHidden('globalFiltersContainer', true);
        return;
    }
    
    safeSetHidden('globalFiltersContainer', false);
    let html = '';
    
    slicerCols.forEach(col => {
        const uniqueVals = [...new Set(rawData.map(r => r[col.name]).filter(v => v !== '' && v != null))].sort();
        if (uniqueVals.length > 300) return;
        
        html += `<div class="slicer-group">
            <label class="slicer-label">${escapeHtml(col.cleanLabel || col.name)}</label>
            <select class="slicer-select" data-col="${escapeHtml(col.name)}" onchange="applyGlobalFilter(this.dataset.col, this.value)">
                <option value="">(Todos)</option>
                ${uniqueVals.map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join('')}
            </select>
        </div>`;
    });
    
    safeSetHtml('slicersList', html);
}

function applyGlobalFilter(col, val) {
    if (val === '') delete globalFilters[col];
    else globalFilters[col] = val;
    recalculateFilteredData();
}

function recalculateFilteredData() {
    filteredData = rawData.filter(r => activeFiles.includes(r.Archivo_Origen)).filter(r => {
        for (const [col, val] of Object.entries(globalFilters)) {
            if (String(r[col]) !== String(val)) return false;
        }
        if (activeFilter && String(r[activeFilter.col]) !== String(activeFilter.val)) {
            return false;
        }
        return true;
    });
    
    let filterText = [];
    for (const [col, val] of Object.entries(globalFilters)) filterText.push(`${col}: ${val}`);
    if (activeFilter) filterText.push(`${activeFilter.col}: ${activeFilter.val}`);
    
    if (filterText.length > 0) {
        safeSetHidden('filterBar', false);
        safeSetText('activeFilterText', filterText.join(' | '));
    } else {
        safeSetHidden('filterBar', true);
    }
    
    renderReport();
}

function applyFilter(colName, value) {
    if (activeFilter && activeFilter.col === colName && activeFilter.val === value) {
        activeFilter = null;
    } else {
        activeFilter = { col: colName, val: value };
    }
    recalculateFilteredData();
}

function clearFilter() {
    activeFilter = null;
    globalFilters = {};
    document.querySelectorAll('.slicer-select').forEach(sel => sel.value = '');
    recalculateFilteredData();
}

// ----------------- MULTI-CHART ANALYTICS & CATEGORY MATRIX -----------------
function renderReport() {
    renderKPIs();
    renderCharts();
    renderCategoryMatrixTable();
}

function renderKPIs() {
    const numCols = columnAnalysis.filter(c => c.type === 'numeric');
    const catCols = columnAnalysis.filter(c => c.type === 'categorical');
    
    let sum1 = filteredData.length;
    let label1 = 'Total Registros';
    if (numCols.length > 0) {
        label1 = 'Total ' + numCols[0].name;
        sum1 = filteredData.reduce((acc, r) => acc + (Number(r[numCols[0].name]) || 0), 0);
    }

    let sum2 = filteredData.length;
    let label2 = 'Promedio por Registro';
    if (numCols.length > 0) {
        label2 = 'Promedio ' + numCols[0].name;
        sum2 = sum1 / (filteredData.length || 1);
    }

    let label3 = 'Categorías Detectadas';
    let val3 = catCols.length + ' Dimensiones';

    let label4 = 'Fuentes Activas';
    let val4 = activeFiles.length + ' Archivo(s)';

    const kpis = [
        { title: label1, value: formatNumber(sum1), badge: 'Volumen', positive: true, color: 'blue', svgPath: 'M0,18 Q15,5 30,12 T60,2' },
        { title: label2, value: formatNumber(sum2), badge: 'Promedio', positive: true, color: 'green', svgPath: 'M0,20 Q15,10 30,15 T60,5' },
        { title: label3, value: val3, badge: 'Dimensiones', positive: true, color: 'purple', svgPath: 'M0,15 Q15,22 30,8 T60,12' },
        { title: label4, value: val4, badge: 'Fuentes', positive: true, color: 'orange', svgPath: 'M0,5 Q15,18 30,10 T60,20' }
    ];

    const kpiHtml = kpis.map(k => `
        <div class="kpi-card">
            <div class="kpi-top-row">
                <div style="display:flex; align-items:center; gap:8px;">
                    <div class="kpi-icon-pill ${k.color}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                    </div>
                    <span class="kpi-title-text">${escapeHtml(k.title)}</span>
                </div>
            </div>
            <div class="kpi-value-text">${k.value}</div>
            <div class="kpi-bottom-row">
                <span class="kpi-badge positive">
                    ${k.badge}
                </span>
                <svg class="kpi-sparkline-svg" viewBox="0 0 60 25">
                    <path d="${k.svgPath}" fill="none" stroke="${k.color === 'blue' ? '#2563eb' : k.color === 'green' ? '#16a34a' : k.color === 'purple' ? '#9333ea' : '#ea580c'}" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
        </div>
    `).join('');

    safeSetHtml('kpiGrid', kpiHtml);
}

function renderCharts() {
    charts.forEach(c => c.destroy());
    charts = [];
    
    if (currentAnalysisMode === 'side-by-side' && activeFiles.length >= 2) {
        safeSetHidden('chartsGrid', true);
        safeSetHidden('chartsDualGrid', false);
        
        const fileA = activeFiles[0];
        const fileB = activeFiles[1];
        
        safeSetText('sideTitleA', fileA);
        safeSetText('sideTitleB', fileB);
        safeSetHtml('chartsGridA', '');
        safeSetHtml('chartsGridB', '');
        
        if (!chartConfigsBase.length) return;
        
        chartConfigsBase.forEach((cfg, index) => {
            renderSingleChart(cfg, index, 'chartsGridA', fileA);
            renderSingleChart(cfg, index, 'chartsGridB', fileB);
        });
        
    } else {
        safeSetHidden('chartsGrid', false);
        safeSetHidden('chartsDualGrid', true);
        safeSetHtml('chartsGrid', '');
        
        if (!chartConfigsBase.length) {
            safeSetHtml('chartsGrid', '<div class="empty-msg">No hay datos suficientes para graficar</div>');
            return;
        }
        
        chartConfigsBase.forEach((cfg, index) => {
            renderSingleChart(cfg, index, 'chartsGrid', null);
        });
    }
}

function renderSingleChart(cfg, index, containerId, specificFile) {
    const container = $(containerId);
    if (!container) return;
    
    const id = 'chart_' + Math.random().toString(36).substr(2, 9);
    const card = document.createElement('div');
    const isFullWidth = (index === 0 && (cfg.type === 'line' || cfg.type === 'bar'));
    card.className = 'chart-card' + (isFullWidth ? ' full-width-chart' : '');
    
    const typeOptions = ['bar', 'horizontalBar', 'line', 'doughnut', 'pie', 'scatter'].map(t => 
        `<option value="${t}" ${cfg.type === t ? 'selected' : ''}>${t.toUpperCase()}</option>`
    ).join('');
    
    const showProjBtn = ['line', 'bar', 'horizontalBar', 'scatter'].includes(cfg.type);
    const projBtnHtml = showProjBtn ? `<button class="btn-project ${cfg.projection ? 'active' : ''}" onclick="toggleProjection(${index})">📈 Proyectar</button>` : '';

    card.innerHTML = `
        <div class="chart-header">
            <span class="chart-title">${escapeHtml(cfg.title)}</span>
            <div class="chart-actions">
                ${projBtnHtml}
                <select class="chart-type-select" onchange="changeChartType(${index}, this.value)" title="Cambiar tipo de gráfico">
                    ${typeOptions}
                </select>
                <button class="btn-icon" onclick="zoomChart('${id}', '${escapeHtml(cfg.title)}')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg></button>
            </div>
        </div>
        <div class="chart-body"><canvas id="${id}"></canvas></div>`;
        
    container.appendChild(card);
    
    const canvas = $(id);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const chart = makeChart(ctx, cfg, specificFile);
    if (chart) charts.push(chart);
}

function changeChartType(index, type) {
    if (chartConfigsBase[index]) {
        chartConfigsBase[index].type = type;
        if (!['line', 'bar', 'horizontalBar', 'scatter'].includes(type)) chartConfigsBase[index].projection = false;
        renderReport();
    }
}

function toggleProjection(index) {
    if (chartConfigsBase[index]) {
        chartConfigsBase[index].projection = !chartConfigsBase[index].projection;
        renderReport();
    }
}

function getCleanLabel(colName) {
    const colObj = columnAnalysis.find(c => c.name === colName);
    return colObj ? colObj.cleanLabel : colName;
}

function generateChartConfigs() {
    const configs = [];
    const nums = columnAnalysis.filter(c => c.type === 'numeric').map(c => c.name);
    
    // Categorías legibles (ciudades, departamentos, provincias, productos) e IDs
    const catsObj = columnAnalysis
        .filter(c => (c.type === 'categorical' || c.type === 'id_code') && c.uniqueCount >= 2 && c.uniqueCount <= 3000)
        .sort((a, b) => {
            // Dar máxima prioridad a columnas de nombres de categorías (ej. departamento_nombre, provincia_nombre, ciudad)
            const aIsName = a.type === 'categorical' ? 0 : 1;
            const bIsName = b.type === 'categorical' ? 0 : 1;
            if (aIsName !== bIsName) return aIsName - bIsName;
            return a.uniqueCount - b.uniqueCount;
        });

    const cats = catsObj.map(c => c.name);
    const dates = columnAnalysis.filter(c => c.type === 'temporal').map(c => c.name);

    // 1. Primary Trend / Time Series
    if (dates.length > 0 && nums.length > 0) {
        configs.push({
            type: 'line',
            title: `📈 Evolución Temporal: ${getCleanLabel(nums[0])} por ${getCleanLabel(dates[0])}`,
            xCol: dates[0], yCol: nums[0],
            agg: 'sum',
            yLabel: `Suma de ${getCleanLabel(nums[0])}`
        });
    }

    // 2. Primary Category Ranking (Bar)
    if (cats.length > 0 && nums.length > 0) {
        configs.push({
            type: 'bar',
            title: `📊 Comparativa Principal: ${getCleanLabel(nums[0])} por ${getCleanLabel(cats[0])}`,
            xCol: cats[0], yCol: nums[0],
            agg: 'sum',
            yLabel: `Suma de ${getCleanLabel(nums[0])}`
        });
    }

    // 3. Category Percentage Share (Doughnut)
    if (cats.length > 0 && nums.length > 0) {
        configs.push({
            type: 'doughnut',
            title: `🍩 Distribución Porcentual: ${getCleanLabel(nums[0])} según ${getCleanLabel(cats[0])}`,
            xCol: cats[0], yCol: nums[0],
            agg: 'sum'
        });
    }

    // 4. Secondary Category Ranking (Horizontal Bar)
    if (cats.length > 1 && nums.length > 0) {
        configs.push({
            type: 'horizontalBar',
            title: `📶 Ranking Secundario: ${getCleanLabel(nums[0])} por ${getCleanLabel(cats[1])}`,
            xCol: cats[1], yCol: nums[0],
            agg: 'sum',
            yLabel: `Suma de ${getCleanLabel(nums[0])}`
        });
    } else if (cats.length > 0 && nums.length > 1) {
        configs.push({
            type: 'bar',
            title: `📊 Comparativa de ${getCleanLabel(nums[1])} por ${getCleanLabel(cats[0])}`,
            xCol: cats[0], yCol: nums[1],
            agg: 'sum',
            yLabel: `Suma de ${getCleanLabel(nums[1])}`
        });
    }

    // 5. Multi-Metric / Multi-Category Breakdown
    if (cats.length > 2 && nums.length > 0) {
        configs.push({
            type: 'bar',
            title: `📊 Análisis por Dimensión: ${getCleanLabel(nums[0])} por ${getCleanLabel(cats[2])}`,
            xCol: cats[2], yCol: nums[0],
            agg: 'sum',
            yLabel: `Suma de ${getCleanLabel(nums[0])}`
        });
    } else if (cats.length > 0) {
        configs.push({
            type: 'pie',
            title: `🥧 Proporción de Registros por ${getCleanLabel(cats[0])}`,
            xCol: cats[0], agg: 'count'
        });
    }

    // 6. Metric Correlation (Scatter Plot)
    if (nums.length >= 2) {
        configs.push({
            type: 'scatter',
            title: `📉 Correlación: ${getCleanLabel(nums[0])} vs ${getCleanLabel(nums[1])}`,
            xCol: nums[0], yCol: nums[1]
        });
    }

    chartConfigsBase = configs.slice(0, 8);
}

function aggregateData(cfg, specificFile = null) {
    const grouped = {};
    let isCompare = false;
    let compareCol = null;
    
    if (currentAnalysisMode === 'overlay' && !specificFile && activeFiles.length > 1) {
        isCompare = true;
        compareCol = 'Archivo_Origen';
    }
    
    let allX = new Set();
    let allSeries = new Set();
    
    let dataToAggregate = filteredData;
    if (specificFile) {
        dataToAggregate = filteredData.filter(r => r.Archivo_Origen === specificFile);
    }
    
    dataToAggregate.forEach(row => {
        const x = String(row[cfg.xCol] || 'N/A');
        const s = isCompare ? String(row[compareCol] || 'N/A') : 'Total';
        
        allX.add(x);
        allSeries.add(s);
        
        if (!grouped[x]) grouped[x] = {};
        if (!grouped[x][s]) grouped[x][s] = { count: 0, sum: 0 };
        
        grouped[x][s].count++;
        if (cfg.yCol) grouped[x][s].sum += (Number(row[cfg.yCol]) || 0);
    });
    
    let xLabels = Array.from(allX);
    let seriesNames = Array.from(allSeries).sort();
    
    if (cfg.type === 'line') {
        xLabels.sort((a, b) => new Date(a) - new Date(b) || a.localeCompare(b));
        if (xLabels.length > 50) xLabels = xLabels.slice(0, 50);
    } else {
        xLabels.sort((a, b) => {
            let totalA = seriesNames.reduce((acc, s) => acc + (grouped[a][s] ? (cfg.agg === 'sum' ? grouped[a][s].sum : grouped[a][s].count) : 0), 0);
            let totalB = seriesNames.reduce((acc, s) => acc + (grouped[b][s] ? (cfg.agg === 'sum' ? grouped[b][s].sum : grouped[b][s].count) : 0), 0);
            return totalB - totalA;
        });
        if (xLabels.length > 20) xLabels = xLabels.slice(0, 20);
    }
    
    let datasets = seriesNames.map((s, i) => {
        const color = CHART_COLORS[i % CHART_COLORS.length];
        return {
            label: isCompare ? s : (cfg.yCol || 'Cantidad'),
            data: xLabels.map(x => grouped[x][s] ? (cfg.agg === 'sum' ? grouped[x][s].sum : grouped[x][s].count) : 0),
            backgroundColor: isCompare ? color : (cfg.type === 'line' ? color + '25' : color),
            borderColor: color,
            borderWidth: cfg.type === 'line' ? 2.5 : 0,
            fill: cfg.type === 'line',
            tension: 0.35,
            borderRadius: (cfg.type === 'bar' || cfg.type === 'horizontalBar') ? 6 : 0,
            pointRadius: cfg.type === 'line' ? 4 : 0,
            pointHoverRadius: 6
        };
    });
    
    if ((cfg.type === 'doughnut' || cfg.type === 'pie') && !isCompare) {
        datasets[0].backgroundColor = CHART_COLORS;
    }
    
    return { labels: xLabels, datasets: datasets };
}

function makeChart(ctx, cfg, specificFile = null) {
    if (!ctx) return null;
    const isInteractive = ['bar', 'horizontalBar', 'doughnut', 'pie', 'line'].includes(cfg.type);
    
    let chartType = cfg.type === 'horizontalBar' ? 'bar' : cfg.type;
    let indexAxis = cfg.type === 'horizontalBar' ? 'y' : 'x';
    
    let agg;
    if (['bar', 'horizontalBar', 'doughnut', 'pie', 'line'].includes(cfg.type)) {
        agg = aggregateData(cfg, specificFile);
        
        if (cfg.projection && ['bar', 'horizontalBar', 'line'].includes(cfg.type)) {
            const trendDatasets = [];
            agg.datasets.forEach(ds => {
                const trendData = calculateTrendline(ds.data, false);
                if (trendData.length > 0) {
                    trendDatasets.push({
                        label: `Tendencia (${ds.label})`,
                        data: trendData,
                        type: 'line',
                        borderColor: ds.borderColor || ds.backgroundColor,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false
                    });
                }
            });
            agg.datasets = [...agg.datasets, ...trendDatasets];
        }
    }

    const options = {
        responsive: true, maintainAspectRatio: false,
        indexAxis: indexAxis,
        plugins: { 
            legend: { 
                display: cfg.type === 'doughnut' || cfg.type === 'pie' || (agg && agg.datasets.length > 1), 
                position: 'right', 
                labels: { boxWidth: 12, usePointStyle: true, font: { family: 'Inter', size: 11 } } 
            },
            tooltip: {
                backgroundColor: '#0f172a',
                titleFont: { family: 'Inter', size: 12, weight: 'bold' },
                bodyFont: { family: 'Inter', size: 11 },
                padding: 10,
                cornerRadius: 8
            }
        },
        onClick: (e, elements) => {
            if (!isInteractive || !elements.length) return;
            const index = elements[0].index;
            const clickedLabel = agg.labels[index];
            if (clickedLabel !== 'N/A') applyFilter(cfg.xCol, clickedLabel);
        }
    };
    
    if (['bar', 'horizontalBar', 'doughnut', 'pie', 'line'].includes(cfg.type)) {
        return new Chart(ctx, {
            type: chartType,
            data: {
                labels: agg.labels,
                datasets: agg.datasets
            },
            options: { 
                ...options, 
                scales: (cfg.type === 'bar' || cfg.type === 'horizontalBar' || cfg.type === 'line') ? { 
                    x: { grid: { display: indexAxis === 'y' }, ticks: { font: { family: 'Inter', size: 11 } } }, 
                    y: { 
                        beginAtZero: true,
                        grid: { color: '#e2e8f0', display: indexAxis === 'x' },
                        ticks: { font: { family: 'Inter', size: 11 } },
                        title: { display: !!cfg.yLabel, text: cfg.yLabel, color: '#64748b', font: { family: 'Inter', size: 11 } } 
                    } 
                } : {} 
            }
        });
    } else if (cfg.type === 'scatter') {
        let isCompare = false;
        let compareCol = null;
        if (currentAnalysisMode === 'overlay' && !specificFile && activeFiles.length > 1) {
            isCompare = true;
            compareCol = 'Archivo_Origen';
        }
        
        let dataToDraw = filteredData;
        if (specificFile) {
            dataToDraw = filteredData.filter(r => r.Archivo_Origen === specificFile);
        }
        
        let datasets = [];
        if (isCompare) {
            const series = [...new Set(dataToDraw.map(r => String(r[compareCol] || 'N/A')))].slice(0, 8);
            datasets = series.map((s, i) => {
                const pts = dataToDraw.filter(r => String(r[compareCol] || 'N/A') === s).map(r => ({ x: Number(r[cfg.xCol]), y: Number(r[cfg.yCol]) })).filter(p => !isNaN(p.x) && !isNaN(p.y)).slice(0, 500);
                return { label: s, data: pts, backgroundColor: CHART_COLORS[i % CHART_COLORS.length] };
            });
        } else {
            const pts = dataToDraw.map(r => ({ x: Number(r[cfg.xCol]), y: Number(r[cfg.yCol]) })).filter(p => !isNaN(p.x) && !isNaN(p.y)).slice(0, 1000);
            datasets = [{ label: 'Valores', data: pts, backgroundColor: CHART_COLORS[0] }];
        }
        
        return new Chart(ctx, {
            type: 'scatter',
            data: { datasets: datasets },
            options: { ...options, scales: { x: { title: { display: true, text: cfg.xCol } }, y: { title: { display: true, text: cfg.yCol } } } }
        });
    }
}

// ----------------- CATEGORY MATRIX TABLE -----------------
function renderCategoryMatrixTable() {
    const catCols = columnAnalysis.filter(c => c.type === 'categorical');
    const numCols = columnAnalysis.filter(c => c.type === 'numeric');
    
    if (catCols.length === 0 || !filteredData.length) {
        safeSetHidden('categoryMatrixCard', true);
        return;
    }
    
    safeSetHidden('categoryMatrixCard', false);
    
    const mainCat = catCols[0].name;
    const mainNum = numCols.length > 0 ? numCols[0].name : null;
    
    const catMap = {};
    let totalOverall = 0;
    
    filteredData.forEach(r => {
        const catVal = String(r[mainCat] || 'N/A');
        const numVal = mainNum ? (Number(r[mainNum]) || 0) : 1;
        
        if (!catMap[catVal]) catMap[catVal] = { count: 0, sum: 0 };
        catMap[catVal].count++;
        catMap[catVal].sum += numVal;
        totalOverall += numVal;
    });
    
    const rowsSorted = Object.entries(catMap).sort((a, b) => b[1].sum - a[1].sum).slice(0, 15);
    
    const headHtml = `<tr>
        <th>Categoría (${escapeHtml(mainCat)})</th>
        <th class="numeric">Registros</th>
        <th class="numeric">${mainNum ? 'Total (' + escapeHtml(mainNum) + ')' : 'Frecuencia'}</th>
        <th class="numeric">Promedio</th>
        <th class="numeric">% del Total</th>
    </tr>`;
    
    const bodyHtml = rowsSorted.map(([cat, stat]) => {
        const avg = stat.sum / (stat.count || 1);
        const pct = totalOverall ? ((stat.sum / totalOverall) * 100).toFixed(1) : '0';
        return `<tr>
            <td><span class="category-badge-pill">${escapeHtml(cat)}</span></td>
            <td class="numeric">${formatNumber(stat.count)}</td>
            <td class="numeric">${formatNumber(stat.sum)}</td>
            <td class="numeric">${formatNumber(avg)}</td>
            <td class="numeric">${pct}%</td>
        </tr>`;
    }).join('');
    
    safeSetHtml('catTableHead', headHtml);
    safeSetHtml('catTableBody', bodyHtml);
}

function renderInsights() {
    let html = '';
    
    if (activeFiles.length === 0) {
        safeSetHtml('insightsList', '<div class="empty-state">Load data to view insights.</div>');
        return;
    }
    
    // Mockup style card 1: Trend
    html += `<div class="insight-item">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
            <strong style="color:var(--accent);">1. [Trend]</strong>
            <span style="background:var(--accent-light); color:var(--accent); padding:2px 6px; border-radius:4px; font-size:11px;">🚀 Peak</span>
        </div>
        Analizando <strong>${formatNumber(filteredData.length)}</strong> registros. Se detectó una concentración del volumen principal en los últimos períodos procesados.
    </div>`;
    
    // Card 2: Insight
    html += `<div class="insight-item">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
            <strong style="color:var(--success);">2. [Insight]</strong>
            <span style="background:var(--success-light); color:var(--success); padding:2px 6px; border-radius:4px; font-size:11px;">📈 Growth</span>
        </div>
        Las categorías numéricas principales mantienen una tendencia de crecimiento constante comparado con el promedio acumulado.
    </div>`;
    
    // Card 3: Alert
    html += `<div class="insight-item">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
            <strong style="color:var(--warning);">3. [Alert]</strong>
            <span style="background:var(--warning-light); color:#92400e; padding:2px 6px; border-radius:4px; font-size:11px;">⚠️ Variance</span>
        </div>
        Filtros aplicados activos. Revisa las variables en el panel lateral para ajustar la segmentación del dataset.
    </div>`;
    
    safeSetHtml('insightsList', html);
}

// ----------------- AUTOMATED REPORT WRITING ENGINE -----------------
function generateExecutiveReport() {
    if (!filteredData.length) {
        safeSetHtml('executiveReportOutput', '<p class="empty-msg">No hay datos activos para redactar el reporte.</p>');
        return;
    }
    
    const numCols = columnAnalysis.filter(c => c.type === 'numeric');
    const catCols = columnAnalysis.filter(c => c.type === 'categorical');
    
    let reportHtml = `<h2>📄 Reporte Ejecutivo de Inteligencia de Datos</h2>`;
    reportHtml += `<p style="color:var(--text-muted); font-size:11px;">Generado automáticamente el ${new Date().toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>`;
    
    reportHtml += `<h3>1. Resumen Ejecutivo</h3>`;
    reportHtml += `<p>Se procesaron exitosamente <strong>${formatNumber(filteredData.length)}</strong> registros consolidados a partir de <strong>${activeFiles.length}</strong> fuente(s) activa(s) (${activeFiles.join(', ')}).</p>`;
    
    reportHtml += `<h3>2. Indicadores Clave de Desempeño</h3>`;
    reportHtml += `<ul>`;
    reportHtml += `<li><strong>Volumen Total de Observaciones:</strong> ${formatNumber(filteredData.length)} filas.</li>`;
    
    numCols.forEach(col => {
        const sum = filteredData.reduce((acc, r) => acc + (Number(r[col.name]) || 0), 0);
        const avg = sum / (filteredData.length || 1);
        reportHtml += `<li><strong>${escapeHtml(col.name)}:</strong> Total Acumulado = <strong>${formatNumber(sum)}</strong> | Promedio = <strong>${formatNumber(avg)}</strong></li>`;
    });
    reportHtml += `</ul>`;

    reportHtml += `<h3>3. Hallazgos y Distribución de Categorías</h3>`;
    reportHtml += `<ul>`;
    catCols.forEach(col => {
        const counts = {};
        filteredData.forEach(r => { const v = String(r[col.name] || 'N/A'); counts[v] = (counts[v] || 0) + 1; });
        const sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
        if (sorted.length > 0) {
            const top = sorted[0];
            const pct = ((top[1] / filteredData.length) * 100).toFixed(1);
            reportHtml += `<li>La variable <strong>"${escapeHtml(col.name)}"</strong> tiene como categoría dominante a <em>"${escapeHtml(top[0])}"</em> con <strong>${formatNumber(top[1])}</strong> ocurrencias (<strong>${pct}%</strong> de la muestra).</li>`;
        }
    });
    reportHtml += `</ul>`;

    reportHtml += `<h3>4. Recomendaciones e Insights Estratégicos</h3>`;
    reportHtml += `<ul>`;
    reportHtml += `<li>Focalizar las acciones operativas sobre los segmentos de mayor volumen identificados en el dashboard.</li>`;
    reportHtml += `<li>Realizar análisis comparativo de series de tiempo para evaluar fluctuaciones estacionales.</li>`;
    reportHtml += `<li>Exportar este informe a PDF mediante el botón superior para su difusión ejecutiva.</li>`;
    reportHtml += `</ul>`;
    
    safeSetHtml('executiveReportOutput', reportHtml);
}

function copyReportToClipboard() {
    const el = $('executiveReportOutput');
    if (!el) return;
    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const btn = $('btnCopyReportText');
        if (btn) {
            const orig = btn.textContent;
            btn.textContent = '✅ Copiado!';
            setTimeout(() => btn.textContent = orig, 1500);
        }
    }).catch(err => console.error('Error al copiar:', err));
}

function renderTable() {
    const cols = currentColumns;
    safeSetHtml('tableHead', `<tr>${cols.map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr>`);
    
    const rows = filteredData.slice(0, MAX_ROWS_TABLE);
    safeSetHtml('tableBody', rows.map(r => `<tr>${cols.map(c => {
        const val = r[c];
        const num = Number(val);
        const isNum = !isNaN(num) && val !== '' && val != null;
        let displayVal = val == null ? '' : String(val);
        if (isNum) displayVal = num.toLocaleString(undefined, { maximumFractionDigits: 4 });
        
        return `<td class="${isNum ? 'numeric' : ''}">${escapeHtml(displayVal)}</td>`;
    }).join('')}</tr>`).join(''));
    
    safeSetText('tableInfo', `Mostrando ${rows.length} de ${filteredData.length} filas`);
}

// ----------------- UTILS -----------------
function calculateTrendline(dataArray, isScatter = false) {
    if (dataArray.length < 2) return [];
    
    let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
    const n = dataArray.length;
    
    dataArray.forEach((val, i) => {
        const x = isScatter ? val.x : i;
        const y = isScatter ? val.y : val;
        sumX += x;
        sumY += y;
        sumXY += x * y;
        sumXX += x * x;
    });
    
    const denominator = (n * sumXX - sumX * sumX);
    if (denominator === 0) return [];
    
    const slope = (n * sumXY - sumX * sumY) / denominator;
    const intercept = (sumY - slope * sumX) / n;
    
    return dataArray.map((val, i) => {
        const x = isScatter ? val.x : i;
        return isScatter ? { x: val.x, y: slope * x + intercept } : (slope * x + intercept);
    });
}

function formatNumber(num) {
    if (num >= 1e6) return (num / 1e6).toFixed(2) + ' M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + ' K';
    return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
}

function zoomChart(canvasId, title) {
    const chart = charts.find(c => c.canvas && c.canvas.id === canvasId);
    if (!chart) return;
    safeSetText('modalTitle', title);
    const modalChart = $('modalChart');
    if (!modalChart) return;
    const ctx = modalChart.getContext('2d');
    modalChart.width = chart.width;
    modalChart.height = chart.height;
    ctx.drawImage(chart.canvas, 0, 0);
    const chartModal = $('chartModal');
    if (chartModal) {
        chartModal._chartBase64 = chart.toBase64Image();
        chartModal.hidden = false;
    }
}

function downloadPNG() {
    const chartModal = $('chartModal');
    const b64 = chartModal ? chartModal._chartBase64 : null;
    if (!b64) return;
    const a = document.createElement('a');
    const title = $('modalTitle') ? $('modalTitle').textContent : 'grafico';
    a.download = title + '.png';
    a.href = b64;
    a.click();
}

function exportReportJSON() {
    if (!rawData.length) return;
    const fileName = $('fileName') ? $('fileName').textContent : 'datos';
    const blob = new Blob([JSON.stringify({ fileName: fileName, recordCount: rawData.length, columns: columnAnalysis }, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.download = 'reporte.json';
    a.href = URL.createObjectURL(blob);
    a.click();
}

window.captureDashboardScreenshot = async function() {
    const btn = $('btnCaptureDashboard');
    const element = document.querySelector('.bi-app') || document.body;
    if (!element) return;

    const origText = btn ? btn.textContent : '📸 Capturar Página Completa';
    if (btn) btn.textContent = '📸 Generando Captura Full Page...';

    const blobPromise = new Promise(async (resolve, reject) => {
        try {
            const h2c = window.html2canvas || (window.html2pdf ? window.html2pdf.html2canvas : null);
            if (!h2c) {
                reject(new Error('html2canvas no está cargado'));
                return;
            }

            const fullWidth = Math.max(element.scrollWidth, document.documentElement.scrollWidth, 1200);
            const fullHeight = Math.max(element.scrollHeight, document.documentElement.scrollHeight, 800);

            const canvas = await h2c(element, {
                scale: 2,
                useCORS: true,
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--bg-app') || '#f4f6f9',
                logging: false,
                width: fullWidth,
                height: fullHeight,
                windowWidth: fullWidth,
                windowHeight: fullHeight,
                scrollX: 0,
                scrollY: 0
            });

            // 1. Descarga automática de la imagen PNG completa
            const fileName = ($('fileName') ? $('fileName').textContent : 'dashboard').split('.')[0];
            const link = document.createElement('a');
            link.download = fileName + '_captura_completa.png';
            link.href = canvas.toDataURL('image/png');
            link.click();

            // 2. Generar blob para el portapapeles
            canvas.toBlob((blob) => {
                if (blob) resolve(blob);
                else reject(new Error('Error al generar blob de la imagen'));
            }, 'image/png');

        } catch (err) {
            reject(err);
        }
    });

    if (navigator.clipboard && window.ClipboardItem) {
        try {
            const item = new ClipboardItem({ 'image/png': blobPromise });
            await navigator.clipboard.write([item]);
            if (btn) btn.textContent = '✅ ¡Página Completa Copiada!';
            setTimeout(() => { if (btn) btn.textContent = origText; }, 2500);
            return;
        } catch (err) {
            console.warn('ClipboardItem promise fallback:', err);
        }
    }

    try {
        const blob = await blobPromise;
        if (navigator.clipboard && navigator.clipboard.write) {
            await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
            if (btn) btn.textContent = '✅ ¡Página Completa Copiada!';
        } else {
            if (btn) btn.textContent = '✅ ¡Imagen Descargada!';
        }
    } catch (err) {
        console.error('Error al capturar:', err);
        if (btn) btn.textContent = '❌ Error al capturar';
    }
    setTimeout(() => { if (btn) btn.textContent = origText; }, 2500);
};

function changeSheet() {
    const sheetSelect = $('sheetSelect');
    if (!sheetSelect) return;
    const sheet = sheetSelect.value;
    try {
        const data = XLSX.utils.sheet_to_json(workbook.Sheets[sheet], { defval: '' });
        if (!data.length) throw new Error('Hoja vacía');
        rawData = data;
        filteredData = [...rawData];
        currentColumns = Object.keys(data[0] || {});
        columnAnalysis = analyzeColumns(rawData);
        clearFilter();
        renderFieldsList();
        renderReport();
    } catch (e) { showError(e.message); }
}

function toggleTheme() {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.documentElement.setAttribute('data-theme', dark ? 'light' : 'dark');
}

function loadTheme() {
    // defaults to light
}

init();