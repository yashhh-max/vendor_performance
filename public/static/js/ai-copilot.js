/**
 * VendorSync AI — Enterprise Copilot & Analytics Assistant
 * Powered by NVIDIA NIM and Grounded Database Intelligence.
 * Architecture:
 * - Real-time SSE / REST chat with verified mathematical grounding
 * - Deep AI Multi-Factor Risk Evaluation
 * - Vendor Scoping & Audit Inspector
 */

(function () {
  'use strict';

  function initAICopilot() {
    if (document.getElementById('ai-copilot-root')) return;

    // Ensure CSS stylesheet is linked
    if (!document.getElementById('ai-copilot-css')) {
      const link = document.createElement('link');
      link.id = 'ai-copilot-css';
      link.rel = 'stylesheet';
      link.href = '/static/css/ai-copilot.css';
      document.head.appendChild(link);
    }

    const root = document.createElement('div');
    root.id = 'ai-copilot-root';
    document.body.appendChild(root);

    // Application state
    let isOpen = false;
    let isMaximized = false;
    let activeTab = 'chat'; // 'chat' | 'audit' | 'kpis'
    let selectedScopedVendor = ''; // '' for all vendors
    let aiStatus = {
      provider: 'NVIDIA NIM',
      model: 'nvidia/nemotron-3-ultra-550b-a55b',
      connected: true,
      mode: 'Connecting to AI Engine...'
    };
    let dbHealth = { status: 'Checking...', dialect: 'SQLite', latency_ms: 0.4 };
    let vendorsList = [];
    let isRequestInProgress = false;

    // Chat conversation history
    let chatHistory = [
      {
        id: 'msg-welcome',
        sender: 'assistant',
        text: '### Welcome to VendorSync AI Copilot\n' +
              'I am your enterprise procurement assistant powered by **NVIDIA NIM** and grounded in your live supplier database.\n\n' +
              'Ask me anything about supplier rankings, on-time delivery rates, contract spend, or comparative evaluations, or select one of the suggested prompts below.',
        grounding: null,
        reasoning: null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ];

    // Markdown Parser
    function renderMarkdown(md) {
      if (!md) return '';
      let html = md
        .replace(/^### (.*$)/gim, '<h4>$1</h4>')
        .replace(/^## (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/^\s*-\s+(.*$)/gim, '<li style="margin-left:14px;">$1</li>')
        .replace(/\n\n/gim, '<br/><br/>');

      // Table formatting
      if (html.includes('|')) {
        const blocks = html.split('<br/><br/>');
        html = blocks.map(block => {
          if (block.includes('|') && block.includes('---')) {
            const rows = block.split('<br/>').filter(r => r.trim().startsWith('|'));
            if (rows.length >= 2) {
              let tbl = '<table>';
              rows.forEach((r, idx) => {
                const cells = r.split('|').filter((_, i, arr) => i > 0 && i < arr.length - 1);
                if (idx === 0) {
                  tbl += '<thead><tr>' + cells.map(c => `<th>${c.trim()}</th>`).join('') + '</tr></thead><tbody>';
                } else if (!r.includes('---')) {
                  tbl += '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
                }
              });
              tbl += '</tbody></table>';
              return tbl;
            }
          }
          return block;
        }).join('<br/><br/>');
      }
      return html;
    }

    // Load initial health, AI status, and vendors
    async function loadStatus() {
      try {
        const [aiRes, dbRes, dashRes] = await Promise.all([
          fetch('/api/ai/status', { credentials: 'include' }).then(r => r.ok ? r.json() : null).catch(() => null),
          fetch('/api/health').then(r => r.ok ? r.json() : null).catch(() => null),
          fetch('/api/dashboard', { credentials: 'include' }).then(r => r.ok ? r.json() : null).catch(() => null)
        ]);

        if (aiRes) aiStatus = aiRes;
        if (dbRes) dbHealth = dbRes;
        if (dashRes && dashRes.vendors) vendorsList = dashRes.vendors;
        render();
      } catch (e) {
        console.warn('AI Copilot status sync error:', e);
      }
    }

    // Main Render Routine
    function render() {
      root.innerHTML = '';

      // Floating Action Button
      const fab = document.createElement('button');
      fab.className = 'ai-copilot-fab';
      fab.setAttribute('aria-label', 'Open AI Procurement Copilot');
      fab.innerHTML = `
        <div class="ai-fab-nvidia-icon">NV</div>
        <span class="ai-copilot-fab-pulse"></span>
        <span>AI Copilot</span>
      `;
      fab.onclick = () => {
        isOpen = !isOpen;
        render();
        if (isOpen) {
          setTimeout(() => {
            const textarea = document.getElementById('ai-chat-input-box');
            if (textarea) textarea.focus();
          }, 100);
        }
      };
      root.appendChild(fab);

      if (!isOpen) return;

      // Main Copilot Panel
      const panel = document.createElement('div');
      panel.className = 'ai-copilot-panel' + (isMaximized ? ' maximized' : '');
      panel.innerHTML = `
        <header class="ai-panel-header">
          <div class="ai-header-left">
            <div class="ai-avatar-badge">NV</div>
            <div class="ai-header-info">
              <h4>VendorSync Copilot <span class="ai-model-tag">${aiStatus.provider === 'nvidia' ? 'NVIDIA NIM' : aiStatus.provider}</span></h4>
              <small>${aiStatus.model || 'Grounded Intelligence'}</small>
            </div>
          </div>
          <div class="ai-header-actions">
            <button class="ai-icon-btn" id="ai-btn-export" title="Export conversation as Markdown" aria-label="Export chat">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            </button>
            <button class="ai-icon-btn" id="ai-btn-reset" title="Start new conversation" aria-label="New chat">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
            </button>
            <button class="ai-icon-btn" id="ai-btn-maximize" title="${isMaximized ? 'Minimize' : 'Expand full width'}" aria-label="Toggle size">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${isMaximized ? '<polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/>' : '<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>'}</svg>
            </button>
            <button class="ai-icon-btn" id="ai-btn-close" title="Close" aria-label="Close">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </header>

        <div class="ai-status-bar">
          <div class="ai-status-indicator">
            <span class="dot"></span>
            <span>Engine: <b>${aiStatus.mode}</b></span>
          </div>
          <div class="ai-grounded-badge">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            <span>Grounded Live (${dbHealth.dialect} · ${dbHealth.latency_ms || 0.4}ms)</span>
          </div>
        </div>

        <div class="ai-scope-toolbar">
          <span class="ai-scope-label">Scope:</span>
          <select class="ai-scope-select" id="ai-scope-vendor-dropdown">
            <option value="" ${selectedScopedVendor === '' ? 'selected' : ''}>🌐 All Suppliers (Entire Network)</option>
            ${vendorsList.map(v => `
              <option value="${v.id}" ${v.id === selectedScopedVendor ? 'selected' : ''}>🏢 ${v.name} (${v.id} · ${v.score}%)</option>
            `).join('')}
          </select>
        </div>

        <nav class="ai-tabs-nav">
          <button class="ai-tab-button ${activeTab === 'chat' ? 'active' : ''}" id="ai-tab-chat">💬 Interactive Copilot</button>
          <button class="ai-tab-button ${activeTab === 'audit' ? 'active' : ''}" id="ai-tab-audit">🔍 Deep Risk Audit</button>
          <button class="ai-tab-button ${activeTab === 'kpis' ? 'active' : ''}" id="ai-tab-kpis">📐 KPI Methodology</button>
        </nav>

        <main class="ai-tab-body" id="ai-tab-body-container"></main>
      `;

      root.appendChild(panel);

      // Event bindings
      document.getElementById('ai-btn-close').onclick = () => { isOpen = false; render(); };
      document.getElementById('ai-btn-maximize').onclick = () => { isMaximized = !isMaximized; render(); };
      document.getElementById('ai-btn-reset').onclick = () => {
        if (confirm('Clear conversation and start a new session?')) {
          chatHistory = [chatHistory[0]];
          render();
        }
      };
      document.getElementById('ai-btn-export').onclick = exportChatHistory;

      document.getElementById('ai-scope-vendor-dropdown').onchange = (e) => {
        selectedScopedVendor = e.target.value;
      };

      document.getElementById('ai-tab-chat').onclick = () => { activeTab = 'chat'; render(); };
      document.getElementById('ai-tab-audit').onclick = () => { activeTab = 'audit'; render(); };
      document.getElementById('ai-tab-kpis').onclick = () => { activeTab = 'kpis'; render(); };

      const bodyContainer = document.getElementById('ai-tab-body-container');
      if (activeTab === 'chat') {
        renderChatView(bodyContainer);
      } else if (activeTab === 'audit') {
        renderAuditView(bodyContainer);
      } else {
        renderKpisView(bodyContainer);
      }
    }

    // Export conversation as Markdown
    function exportChatHistory() {
      const content = '# VendorSync AI Copilot — Chat Transcript\n\n' +
        `Generated: ${new Date().toISOString()}\n\n` +
        chatHistory.map(m => `### ${m.sender.toUpperCase()} (${m.timestamp || ''})\n\n${m.text}\n\n`).join('---\n\n');
      const blob = new Blob([content], { type: 'text/markdown' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `vendorsync-ai-chat-${Date.now()}.md`;
      a.click();
    }

    // Render Tab 1: Interactive Chat
    function renderChatView(container) {
      container.innerHTML = `
        <div class="ai-messages-container" id="ai-messages-box">
          ${chatHistory.map((m, idx) => `
            <div class="ai-message-row ${m.sender}">
              <div class="ai-bubble">
                ${renderMarkdown(m.text)}
              </div>
              ${m.sender === 'assistant' ? `
                <div class="ai-msg-actions">
                  ${m.grounding ? `
                    <button class="ai-evidence-toggle" data-idx="${idx}">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                      Inspect Grounded Data
                    </button>
                  ` : ''}
                  <button class="ai-copy-btn" data-copy="${encodeURIComponent(m.text)}">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                    Copy
                  </button>
                </div>
                ${m.showEvidence && m.grounding ? `
                  <div class="ai-evidence-card">
                    <div class="ai-evidence-title">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                      Verified Deterministic Context:
                    </div>
                    <pre style="margin:0;font-size:10.5px;font-family:var(--ai-font-mono);overflow-x:auto;">${JSON.stringify(m.grounding, null, 2)}</pre>
                  </div>
                ` : ''}
              ` : ''}
            </div>
          `).join('')}
        </div>

        <div class="ai-chips-container">
          <div class="ai-chips-label">Suggested Analyses:</div>
          <div class="ai-chips-list">
            <button class="ai-prompt-chip" data-q="Which vendors have the highest contract value and spend?">💰 Highest contract spend</button>
            <button class="ai-prompt-chip" data-q="Compare Northstar Components vs Apex Microdevices head to head">⚖️ Compare top suppliers</button>
            <button class="ai-prompt-chip" data-q="Which vendors show severe delivery delays or defect risks?">🚨 Delivery delay bottlenecks</button>
            <button class="ai-prompt-chip" data-q="Explain how vendor performance score and risk score are calculated">📐 Explain KPI formulas</button>
            <button class="ai-prompt-chip" data-q="What are the major 6-month performance trends in our network?">📈 6-Month score trajectory</button>
            <button class="ai-prompt-chip" data-q="Recommend the best supplier for a $150,000 mission-critical order">💡 Strategic recommendation</button>
          </div>
        </div>

        <div class="ai-input-wrapper">
          <div class="ai-input-controls">
            <textarea
              class="ai-chat-textarea"
              id="ai-chat-input-box"
              placeholder="Ask NVIDIA Copilot about supplier performance, risks, or comparisons..."
              rows="1"
            ></textarea>
            <button class="ai-submit-button" id="ai-send-btn" ${isRequestInProgress ? 'disabled' : ''}>
              ${isRequestInProgress ? '<span>Analysing...</span>' : `
                <span>Send</span>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              `}
            </button>
          </div>
          <div class="ai-input-footer">
            <span>Powered by NVIDIA NIM & Grounded Live Database</span>
            <span>Enter ↵ to send · Shift+Enter for new line</span>
          </div>
        </div>
      `;

      // Auto-scroll messages
      const msgsBox = document.getElementById('ai-messages-box');
      if (msgsBox) msgsBox.scrollTop = msgsBox.scrollHeight;

      // Evidence inspection toggle
      container.querySelectorAll('.ai-evidence-toggle').forEach(btn => {
        btn.onclick = () => {
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          if (chatHistory[idx]) {
            chatHistory[idx].showEvidence = !chatHistory[idx].showEvidence;
            render();
          }
        };
      });

      // Copy buttons
      container.querySelectorAll('.ai-copy-btn').forEach(btn => {
        btn.onclick = () => {
          const text = decodeURIComponent(btn.getAttribute('data-copy') || '');
          navigator.clipboard.writeText(text).then(() => {
            btn.innerHTML = '✓ Copied!';
            setTimeout(() => { btn.innerHTML = 'Copy'; }, 1800);
          });
        };
      });

      // Suggestion chips
      container.querySelectorAll('.ai-prompt-chip').forEach(btn => {
        btn.onclick = () => {
          const query = btn.getAttribute('data-q');
          submitMessage(query);
        };
      });

      const input = document.getElementById('ai-chat-input-box');
      const sendBtn = document.getElementById('ai-send-btn');

      // Auto-resize input
      input.oninput = () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
      };

      input.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          submitMessage(input.value);
        }
      };

      sendBtn.onclick = () => {
        submitMessage(input.value);
      };
    }

    // Submit user message to backend
    async function submitMessage(text) {
      if (!text || !text.trim() || isRequestInProgress) return;
      const cleanText = text.trim();
      isRequestInProgress = true;

      // Append user message
      chatHistory.push({
        id: 'msg-' + Date.now(),
        sender: 'user',
        text: cleanText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });

      // Append temporary loading placeholder
      const tempId = 'msg-loading-' + Date.now();
      chatHistory.push({
        id: tempId,
        sender: 'assistant',
        text: '*(Analyzing database signals & generating grounded NVIDIA reasoning...)*',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
      render();

      try {
        const response = await fetch('/api/ai/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            message: cleanText,
            vendor_id: selectedScopedVendor || null,
            history: chatHistory.slice(0, -2).map(m => ({ role: m.sender, content: m.text }))
          })
        });

        // Remove placeholder
        chatHistory = chatHistory.filter(m => m.id !== tempId);

        if (response.ok) {
          const data = await response.json();
          chatHistory.push({
            id: 'msg-' + Date.now(),
            sender: 'assistant',
            text: data.reply,
            grounding: data.supporting_data || data.verified_metrics,
            reasoning: data.reasoning,
            showEvidence: false,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        } else {
          const errData = await response.json().catch(() => ({}));
          chatHistory.push({
            id: 'msg-err-' + Date.now(),
            sender: 'assistant',
            text: `⚠️ **Service Alert**: ${errData.detail || 'Unable to reach AI assistant. Ensure you are signed in.'}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        }
      } catch (err) {
        chatHistory = chatHistory.filter(m => m.id !== tempId);
        chatHistory.push({
          id: 'msg-err-' + Date.now(),
          sender: 'assistant',
          text: `⚠️ **Network Connection Issue**: ${err.message}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      } finally {
        isRequestInProgress = false;
        render();
      }
    }

    // Render Tab 2: Deep AI Audit
    let auditVendorId = '';
    let auditLoading = false;
    let auditData = null;

    function renderAuditView(container) {
      if (!auditVendorId && vendorsList.length > 0) {
        auditVendorId = vendorsList[0].id;
      }

      container.innerHTML = `
        <div class="ai-audit-wrapper">
          <div class="ai-audit-picker-card">
            <label style="font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;">Select Supplier to Audit:</label>
            <select class="ai-scope-select" id="ai-audit-picker-select">
              ${vendorsList.map(v => `
                <option value="${v.id}" ${v.id === auditVendorId ? 'selected' : ''}>${v.name} (${v.id}) · ${v.risk} Risk (${v.score}% score)</option>
              `).join('')}
            </select>
            <button class="ai-audit-btn-primary" id="ai-run-deep-audit-btn" ${auditLoading ? 'disabled' : ''}>
              ${auditLoading ? 'Processing Multi-Factor Diagnosis...' : '✨ Run NVIDIA Deep Risk Evaluation'}
            </button>
          </div>

          <div id="ai-audit-result-display">
            ${auditData ? `
              <div class="ai-audit-result-card">
                <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--ai-border);padding-bottom:10px;">
                  <div>
                    <h3 style="margin:0;font-size:16px;color:#f8fafc;">${auditData.vendor_name}</h3>
                    <small style="color:#94a3b8;">${auditData.engine} · Confidence: <b>${auditData.confidence_score}%</b></small>
                  </div>
                  <span class="ai-risk-tag ${auditData.risk_level.toLowerCase()}">
                    ${auditData.risk_level} Risk (${auditData.risk_score}%)
                  </span>
                </div>

                <div style="background:#090f1d;padding:12px;border-radius:8px;border-left:3px solid #38bdf8;">
                  <b style="color:#38bdf8;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Executive Briefing:</b>
                  <p style="margin:4px 0 0;color:#e2e8f0;font-size:12.5px;line-height:1.5;">${auditData.executive_summary}</p>
                </div>

                <div>
                  <b style="color:#f87171;font-size:11px;text-transform:uppercase;">🚨 Key Risk Drivers:</b>
                  <ul style="margin:6px 0;padding-left:18px;font-size:12px;color:#cbd5e1;">
                    ${auditData.key_risk_drivers.map(d => `<li style="margin-bottom:3px;">${d}</li>`).join('')}
                  </ul>
                </div>

                <div>
                  <b style="color:#34d399;font-size:11px;text-transform:uppercase;">✅ Positive Operational Indicators:</b>
                  <ul style="margin:6px 0;padding-left:18px;font-size:12px;color:#cbd5e1;">
                    ${auditData.positive_indicators.map(p => `<li style="margin-bottom:3px;">${p}</li>`).join('')}
                  </ul>
                </div>

                <div>
                  <b style="color:#60a5fa;font-size:11px;text-transform:uppercase;">💡 Strategic Procurement Recommendations:</b>
                  <ul style="margin:6px 0;padding-left:18px;font-size:12px;color:#cbd5e1;">
                    ${auditData.strategic_recommendations.map(r => `<li style="margin-bottom:3px;">${r}</li>`).join('')}
                  </ul>
                </div>

                <div style="background:#0c192d;padding:12px;border-radius:8px;border:1px solid rgba(59, 130, 246, 0.3);">
                  <b style="color:#93c5fd;font-size:11px;text-transform:uppercase;">🤝 Contract Negotiation Strategy:</b>
                  <p style="margin:4px 0 0;color:#e2e8f0;font-size:12.5px;line-height:1.5;">${auditData.contract_negotiation_advice}</p>
                </div>
              </div>
            ` : `
              <div style="text-align:center;padding:40px 16px;color:#64748b;">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:8px;opacity:0.5;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                <p style="margin:0;font-size:13px;">Select a supplier above to run an AI multi-factor audit with NVIDIA NIM.</p>
              </div>
            `}
          </div>
        </div>
      `;

      const select = document.getElementById('ai-audit-picker-select');
      if (select) {
        select.onchange = (e) => { auditVendorId = e.target.value; };
      }

      const runBtn = document.getElementById('ai-run-deep-audit-btn');
      if (runBtn) {
        runBtn.onclick = async () => {
          if (!auditVendorId) return;
          auditLoading = true;
          render();

          try {
            const res = await fetch(`/api/ai/analyze/${auditVendorId}`, {
              method: 'POST',
              credentials: 'include'
            });
            if (res.ok) {
              auditData = await res.json();
            } else {
              alert('Error running AI audit. Ensure you are logged in.');
            }
          } catch (e) {
            alert('Audit request failed: ' + e.message);
          } finally {
            auditLoading = false;
            render();
          }
        };
      }
    }

    // Render Tab 3: KPI Formula Guide
    function renderKpisView(container) {
      container.innerHTML = `
        <div class="ai-formula-grid">
          <div style="margin-bottom:6px;">
            <h4 style="margin:0;font-size:14px;color:#f8fafc;">VendorSync Mathematical Framework</h4>
            <small style="color:#94a3b8;">All AI responses strictly adhere to these deterministic formulas.</small>
          </div>

          <div class="ai-formula-card">
            <b>1. Overall Vendor Performance Score (0-100%)</b>
            <p style="margin:0 0 6px;color:#94a3b8;">Four-pillar weighted composite measuring end-to-end supply stability.</p>
            <code class="ai-formula-code">Score = (Delivery × 0.35) + (Quality × 0.35) + (Cost × 0.15) + (Reliability × 0.15)</code>
            <span style="font-size:11px;color:#cbd5e1;">Delivery & Quality account for 70% of the total score due to fulfillment impact.</span>
          </div>

          <div class="ai-formula-card">
            <b>2. Exposure Risk Score & Penalty</b>
            <p style="margin:0 0 6px;color:#94a3b8;">Factors in delivery delay ratios, escalated complaints, and defective batches.</p>
            <code class="ai-formula-code">Penalty = ((Delayed Orders / Total Orders) × 30) + (Complaints × 4) + (Defects × 3)</code>
            <code class="ai-formula-code">Risk Score = Base (100 - Score) + Penalty  [Clamped 5 to 95]</code>
          </div>

          <div class="ai-formula-card">
            <b>3. Risk Classification Thresholds</b>
            <div style="display:flex;gap:8px;margin-top:6px;">
              <span class="ai-risk-tag low">LOW: Score ≥ 85 & Risk ≤ 20</span>
              <span class="ai-risk-tag medium">MED: Score ≥ 68 & Risk ≤ 50</span>
              <span class="ai-risk-tag high">HIGH: Score &lt; 68 or Risk &gt; 50</span>
            </div>
          </div>
        </div>
      `;
    }

    // Initialize data synchronization
    loadStatus();
    setInterval(loadStatus, 30000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAICopilot);
  } else {
    initAICopilot();
  }
})();
