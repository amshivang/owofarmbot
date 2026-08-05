// Redirect to the default whitelisted firebaseapp.com domain to prevent OAuth domain errors
if (window.location.hostname === 'farmbot-owo-c8005d.web.app') {
    window.location.replace(window.location.href.replace('farmbot-owo-c8005d.web.app', 'farmbot-owo-c8005d.firebaseapp.com'));
}

// Frontend logic for OwO FarmBot Dashboard - Firebase Authenticated Version

// API endpoints base configuration for remote/local server deployment
const CLOUD_RUN_URL = 'https://farmbot-backend-587715437880.us-central1.run.app';
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? '' 
    : CLOUD_RUN_URL;

const WS_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host
    : CLOUD_RUN_URL.replace('https://', 'wss://').replace('http://', 'ws://');

document.addEventListener('DOMContentLoaded', async () => {
    const user = { uid: "local_user" };
    await initDashboard(user);


    async function initDashboard(user) {
        // Stop bot on tab close / page unload
        window.addEventListener('beforeunload', () => {
            if (botState === 'farming' || botState === 'connected') {
                navigator.sendBeacon(API_BASE + '/api/stop?uid=' + user.uid);
            }
        });

        // DOM Elements
        const tokenInput = document.getElementById('token-input');
        const toggleTokenBtn = document.getElementById('toggle-token-visibility');
        const validateBtn = document.getElementById('validate-token-btn');
        const verifyLoaderContainer = document.getElementById('verify-loader-container');
        const tokenFeedback = document.getElementById('token-feedback');
        
        const settingsArea = document.getElementById('settings-area');
        const tokenUnverifiedUi = document.getElementById('token-unverified-ui');
        const tokenVerifiedUi = document.getElementById('token-verified-ui');
        const connectedUserName = document.getElementById('connected-user-name');
        
        const gambleToggle = document.getElementById('gamble-toggle');
        const gambleDetails = document.getElementById('gamble-details');
        const gambleAmountInput = document.getElementById('gamble-amount');
        
        const prayCurseToggle = document.getElementById('pray-curse-toggle');
        const prayCurseDetails = document.getElementById('pray-curse-details');
        const prayCurseCountInput = document.getElementById('pray-curse-count');
        
        const startBotBtn = document.getElementById('start-bot-btn');
        const connectionStatus = document.getElementById('connection-status');
        const statusText = connectionStatus.querySelector('.status-lbl') || connectionStatus.querySelector('.status-text');
        
        const shellLogs = document.getElementById('shell-logs');
        const clearShellBtn = document.getElementById('clear-shell-btn');
        const wsIndicator = document.getElementById('shell-ws-indicator');
        const changeTokenBtn = document.getElementById('change-token-btn');
        const logoutBtn = document.getElementById('logout-btn');

        // App State
        let isTokenVerified = false;
        let botState = 'disconnected'; // disconnected, connected, farming
        let logSocket = null;
        let isWSConnected = false;
        const defaultSavedAvatarUrl = "https://cdn.discordapp.com/avatars/1311361502300602398/95ee431ebad3d3ac309aa8433dac7dbe.png";
        const userAvatarImg = document.getElementById('user-avatar-img');

        // Logout Handler Removed

        // Change Token Button
        if (changeTokenBtn) {
            changeTokenBtn.addEventListener('click', async () => {
                // Remove local token
                localStorage.removeItem('discord_token');
                
                tokenVerifiedUi.style.display = 'none';
                tokenUnverifiedUi.style.display = 'block';
                tokenInput.focus();
                showFeedback(tokenFeedback, 'Please verify your new token.', 'info');
            });
        }

        function updateAvatarUI(url) {
            if (url && userAvatarImg) {
                userAvatarImg.src = url;
                userAvatarImg.style.display = 'block';
            } else if (userAvatarImg) {
                userAvatarImg.style.display = 'none';
            }
        }

        async function fetchAvatarUrl(token) {
            try {
                const proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent('https://discord.com/api/v9/users/@me');
                const res = await fetch(proxyUrl, {
                    headers: {
                        'Authorization': token
                    }
                });
                if (res.ok) {
                    const user = await res.json();
                    if (user.avatar) {
                        return `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.png`;
                    } else {
                        const disc = user.discriminator || '0000';
                        const defaultIndex = (disc === '0' || !disc) ? (parseInt(user.id) >> 22) % 6 : parseInt(disc) % 5;
                        return `https://cdn.discordapp.com/embed/avatars/${defaultIndex}.png`;
                    }
                }
            } catch (err) {
                console.error('Failed to fetch avatar via corsproxy:', err);
            }
            return null;
        }

        // Toggle password visibility
        const eyeIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
        const eyeOffIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10c3 4 15 4 18 0"></path><path d="M5 12l-1.5 2"></path><path d="M9 13.5l-1 2.5"></path><path d="M12 14v2.5"></path><path d="M15 13.5l1 2.5"></path><path d="M19 12l1.5 2"></path></svg>`;

        toggleTokenBtn.addEventListener('click', () => {
            if (tokenInput.type === 'password') {
                tokenInput.type = 'text';
                toggleTokenBtn.innerHTML = eyeIcon;
            } else {
                tokenInput.type = 'password';
                toggleTokenBtn.innerHTML = eyeOffIcon;
            }
        });

        // Show/hide eye visibility toggle button based on typed input
        function updateVisibilityToggle() {
            if (tokenInput.value.length > 0) {
                toggleTokenBtn.style.display = 'flex';
            } else {
                toggleTokenBtn.style.display = 'none';
            }
        }
        tokenInput.addEventListener('input', updateVisibilityToggle);
        updateVisibilityToggle();

        // Toggle Collapsible Sections
        gambleToggle.addEventListener('change', () => {
            if (gambleToggle.checked) {
                gambleDetails.classList.add('expanded');
            } else {
                gambleDetails.classList.remove('expanded');
            }
        });

        prayCurseToggle.addEventListener('change', () => {
            if (prayCurseToggle.checked) {
                prayCurseDetails.classList.add('expanded');
            } else {
                prayCurseDetails.classList.remove('expanded');
            }
        });

        // Dynamic API verification helper
        function saveAccount(token, username, avatarUrl) {
            let accounts = JSON.parse(localStorage.getItem('saved_accounts') || '[]');
            accounts = accounts.filter(a => a.token !== token);
            accounts.push({ token, username, avatarUrl });
            localStorage.setItem('saved_accounts', JSON.stringify(accounts));
        }

        function populateSavedAccounts() {
            const accounts = JSON.parse(localStorage.getItem('saved_accounts') || '[]');
            const container = document.getElementById('saved-accounts-container');
            const select = document.getElementById('saved-accounts-select');
            
            if (accounts.length > 0 && container && select) {
                container.style.display = 'block';
                select.innerHTML = '<option value="">-- Select an account --</option>';
                accounts.forEach(acc => {
                    const opt = document.createElement('option');
                    opt.value = acc.token;
                    opt.textContent = acc.username;
                    select.appendChild(opt);
                });
                
                select.onchange = () => {
                    if (select.value) {
                        tokenInput.value = select.value;
                        updateVisibilityToggle();
                    }
                };
            } else if (container) {
                container.style.display = 'none';
            }
        }

        const checkCashBtn = document.getElementById('check-cash-btn');
        const cashResult = document.getElementById('cash-result');

        if (checkCashBtn) {
            checkCashBtn.addEventListener('click', async () => {
                checkCashBtn.disabled = true;
                checkCashBtn.textContent = 'CHECKING...';
                if (cashResult) cashResult.textContent = '???';
                try {
                    const res = await fetch(API_BASE + '/api/check_cash?uid=' + user.uid);
                    const data = await res.json();
                    if (res.ok && data.success) {
                        if (cashResult) cashResult.textContent = data.cash;
                    } else {
                        if (cashResult) cashResult.textContent = 'ERROR';
                        alert(data.message || 'Failed to check cash');
                    }
                } catch (err) {
                    console.error(err);
                    if (cashResult) cashResult.textContent = 'ERROR';
                    alert('Network error while checking cash');
                } finally {
                    checkCashBtn.disabled = false;
                    checkCashBtn.textContent = 'CHECK_CASH';
                }
            });
        }

        async function verifyToken(token, isAuto = false) {
            validateBtn.disabled = true;
            validateBtn.style.display = 'none';
            verifyLoaderContainer.style.display = 'block';
            showFeedback(tokenFeedback, isAuto ? 'Connecting to Discord with saved token...' : 'Connecting to Discord...', 'info');

            try {
                const response = await fetch(API_BASE + '/api/validate-token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token })
                });
                const data = await response.json();

                if (response.ok && data.success) {
                    isTokenVerified = true;
                    botState = 'verified';
                    
                    

                    // Save token to local storage
                    localStorage.setItem('discord_token', token);
                    
                    // Fetch and store avatar
                    const avatarUrl = await fetchAvatarUrl(token);
                    const finalAvatarUrl = avatarUrl || localStorage.getItem('discord_avatar_url') || defaultSavedAvatarUrl;
                    if (avatarUrl) {
                        localStorage.setItem('discord_avatar_url', avatarUrl);
                    }
                    updateAvatarUI(finalAvatarUrl);
                    
                    saveAccount(token, data.username, finalAvatarUrl);
                    populateSavedAccounts();
                    
                    // Transition to verified UI
                    tokenUnverifiedUi.style.display = 'none';
                    tokenVerifiedUi.style.display = 'block';
                    connectedUserName.textContent = data.username;
                    
                    updateStatusUI();
                    settingsArea.classList.remove('locked');
                    const lockOverlayUi = document.getElementById('lock-overlay-ui');
                    if (lockOverlayUi) lockOverlayUi.style.display = 'none';
                    startBotBtn.disabled = false;
                    showFeedback(tokenFeedback, 'Connected successfully.', 'success');
                } else {
                    isTokenVerified = false;
                    botState = 'disconnected';
                    
                    

                    tokenVerifiedUi.style.display = 'none';
                    tokenUnverifiedUi.style.display = 'block';
                    
                    updateStatusUI();
                    showFeedback(tokenFeedback, data.message || 'Invalid token. Please check and try again.', 'error');
                    settingsArea.classList.add('locked');
                    const lockOverlayUi = document.getElementById('lock-overlay-ui');
                    if (lockOverlayUi) lockOverlayUi.style.display = 'flex';
                    startBotBtn.disabled = true;
                }
            } catch (error) {
                console.error('Validation error:', error);
                isTokenVerified = false;
                botState = 'disconnected';
                tokenVerifiedUi.style.display = 'none';
                tokenUnverifiedUi.style.display = 'block';
                updateStatusUI();
                showFeedback(tokenFeedback, 'Local server offline. Ensure backend python main.py is running.', 'error');
                settingsArea.classList.add('locked');
                const lockOverlayUi = document.getElementById('lock-overlay-ui');
                if (lockOverlayUi) lockOverlayUi.style.display = 'flex';
                startBotBtn.disabled = true;
            } finally {
                validateBtn.disabled = false;
                validateBtn.style.display = 'block';
                verifyLoaderContainer.style.display = 'none';
                validateBtn.textContent = 'VERIFY_CONNECTION';
                updateVisibilityToggle();
            }
        }

        // Validate Token Click
        validateBtn.addEventListener('click', async () => {
            const token = tokenInput.value.trim();
            if (!token) {
                showFeedback(tokenFeedback, 'Please enter a token first.', 'error');
                return;
            }
            await verifyToken(token, false);
        });

        // Start / Stop Bot click
        startBotBtn.addEventListener('click', async () => {
            if (botState === 'farming' || botState === 'connected') {
                // STOP BOT
                startBotBtn.disabled = true;
                startBotBtn.textContent = 'Stopping...';
                try {
                    const res = await fetch(API_BASE + '/api/stop', { 
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ UID: user.uid })
                    });
                    const data = await res.json();
                    if (res.ok) {
                        botState = 'verified';
                        appendSystemLog('Bot stopped farming via dashboard.');
                        
                    }
                } catch (err) {
                    console.error(err);
                    appendSystemLog('[SYSTEM ERROR] Failed to stop bot.');
                } finally {
                    startBotBtn.disabled = false;
                    updateStatusUI();
                }
            } else {
                // START BOT
                const token = tokenInput.value.trim();
                if (!token) return;

                if (gambleToggle.checked) {
                    const amount = parseInt(gambleAmountInput.value);
                    if (isNaN(amount) || amount <= 0) {
                        alert('Please enter a valid gambling amount (must be greater than 0).');
                        gambleAmountInput.focus();
                        return;
                    }
                }

                if (prayCurseToggle.checked) {
                    const count = parseInt(prayCurseCountInput.value);
                    if (isNaN(count) || count <= 0) {
                        alert('Please enter a valid count for pray/curse.');
                        prayCurseCountInput.focus();
                        return;
                    }
                }

                const prayCurseType = document.querySelector('input[name="pray-curse-type"]:checked').value;
                const config = {
                    TOKEN: token,
                    UID: user.uid,
                    GAMBLE: {
                        ENABLED: gambleToggle.checked,
                        AMOUNT: gambleToggle.checked ? parseInt(gambleAmountInput.value) : 1000
                    },
                    PRAY_CURSE: {
                        ENABLED: prayCurseToggle.checked,
                        COMMAND: prayCurseType === 'pray' ? 'owo pray' : 'owo curse',
                        COUNT: prayCurseToggle.checked ? parseInt(prayCurseCountInput.value) : 5
                    }
                };

                localStorage.setItem('farmbot_settings', JSON.stringify(config));

                

                startBotBtn.disabled = true;
                startBotBtn.textContent = 'Starting...';
                appendSystemLog('Starting Bot with fresh settings.json configurations...');

                try {
                    const res = await fetch(API_BASE + '/api/start', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        botState = 'farming';
                        appendSystemLog('Bot started successfully! Running farm loop...');
                    } else {
                        alert(data.message || 'Failed to start bot client.');
                        appendSystemLog(`[SYSTEM ERROR] Startup failed: ${data.message}`);
                    }
                } catch (err) {
                    console.error(err);
                    appendSystemLog('[SYSTEM ERROR] Web request failed on start.');
                } finally {
                    startBotBtn.disabled = false;
                    updateStatusUI();
                }
            }
        });

        // Clear shell
        clearShellBtn.addEventListener('click', () => {
            shellLogs.innerHTML = '';
            const txt1 = document.getElementById('clear-btn-txt-1');
            const txt2 = document.getElementById('clear-btn-txt-2');
            if (txt1) txt1.textContent = 'CLEARED';
            if (txt2) txt2.textContent = 'CLEARED';
            appendSystemLog('Console logs cleared.');
        });

        // Helper functions
        function showFeedback(element, message, type) {
            element.textContent = message;
            element.className = 'feedback-msg ' + type;
            element.style.display = 'block';
        }

        function updateStatusUI() {
            const lockOverlayUi = document.getElementById('lock-overlay-ui');
            const cashContainer = document.getElementById('cash-container');
            
            if (botState === 'disconnected') {
                connectionStatus.className = 'status-indicator disconnected';
                statusText.textContent = 'DISCONNECTED';
                startBotBtn.className = 'btn';
                startBotBtn.textContent = 'START_FARMBOT';
                startBotBtn.disabled = true;
                settingsArea.classList.add('locked');
                if (lockOverlayUi) {
                    lockOverlayUi.style.display = 'flex';
                    const span = lockOverlayUi.querySelector('span');
                    if (span) span.textContent = '🔒 VERIFY ACCOUNT TOKEN TO UNLOCK CONFIG';
                }
            } else if (botState === 'verified') {
                connectionStatus.className = 'status-indicator connected';
                statusText.textContent = 'CONNECTED';
                startBotBtn.className = 'btn btn--primary';
                startBotBtn.textContent = 'START_FARMBOT';
                startBotBtn.disabled = false;
                settingsArea.classList.remove('locked');
                if (lockOverlayUi) lockOverlayUi.style.display = 'none';
            } else if (botState === 'connected') {
                connectionStatus.className = 'status-indicator connected';
                statusText.textContent = 'CONNECTED';
                startBotBtn.className = 'btn btn--danger';
                startBotBtn.textContent = 'STOP_FARMBOT';
                startBotBtn.disabled = false;
                settingsArea.classList.remove('locked');
                if (lockOverlayUi) lockOverlayUi.style.display = 'none';
            } else if (botState === 'farming') {
                connectionStatus.className = 'status-indicator farming';
                statusText.textContent = 'FARMING';
                startBotBtn.className = 'btn btn--danger';
                startBotBtn.textContent = 'STOP_FARMBOT';
                startBotBtn.disabled = false;
                settingsArea.classList.add('locked');
                if (lockOverlayUi) {
                    lockOverlayUi.style.display = 'flex';
                    const span = lockOverlayUi.querySelector('span');
                    if (span) span.textContent = '🔒 STOP FARMING TO EDIT CONFIG';
                }
            }
            
            if (cashContainer) {
                if (botState === 'farming') {
                    cashContainer.style.display = 'flex';
                } else {
                    cashContainer.style.display = 'none';
                }
            }
        }

        function resetClearButtonText() {
            const txt1 = document.getElementById('clear-btn-txt-1');
            const txt2 = document.getElementById('clear-btn-txt-2');
            if (txt1 && txt1.textContent === 'CLEARED') {
                txt1.textContent = 'CLEAR LOGS';
            }
            if (txt2 && txt2.textContent === 'CLEARED') {
                txt2.textContent = 'CLEAR LOGS';
            }
        }

        const MAX_LOGS = 50;
        let scrollAnimationId = null;

        function limitLogsCount() {
            const wasAtBottom = shellLogs.scrollHeight - shellLogs.clientHeight - shellLogs.scrollTop < 50;
            let removedHeight = 0;
            while (shellLogs.children.length > MAX_LOGS) {
                const firstChild = shellLogs.firstChild;
                removedHeight += firstChild.offsetHeight || 0;
                shellLogs.removeChild(firstChild);
            }
            if (!wasAtBottom && removedHeight > 0) {
                shellLogs.scrollTop -= removedHeight;
            }
        }

        function slowScrollToBottom(element, duration = 1200) {
            const start = element.scrollTop;
            const target = element.scrollHeight - element.clientHeight;
            const change = target - start;
            
            if (change <= 0) return;
            
            if (scrollAnimationId) {
                cancelAnimationFrame(scrollAnimationId);
            }
            
            let startTime = null;
            
            function animateScroll(currentTime) {
                if (!startTime) startTime = currentTime;
                const timeElapsed = currentTime - startTime;
                const progress = Math.min(timeElapsed / duration, 1);
                
                const ease = progress < 0.5 
                    ? 2 * progress * progress 
                    : -1 + (4 - 2 * progress) * progress;
                    
                element.scrollTop = start + change * ease;
                
                if (timeElapsed < duration) {
                    scrollAnimationId = requestAnimationFrame(animateScroll);
                } else {
                    scrollAnimationId = null;
                }
            }
            
            scrollAnimationId = requestAnimationFrame(animateScroll);
        }

        function appendSystemLog(msg, type = 'sys-msg') {
            if (msg !== 'Console logs cleared.') {
                resetClearButtonText();
            }
            const isAtBottom = shellLogs.scrollHeight - shellLogs.clientHeight - shellLogs.scrollTop < 50;
            
            const div = document.createElement('div');
            div.className = `log-entry ${type}`;
            div.textContent = `[SYSTEM] ${msg}`;
            shellLogs.appendChild(div);
            
            limitLogsCount();
            
            if (isAtBottom) {
                slowScrollToBottom(shellLogs, 1200);
            }
        }

        function appendTerminalLog(logData) {
            resetClearButtonText();
            const isAtBottom = shellLogs.scrollHeight - shellLogs.clientHeight - shellLogs.scrollTop < 50;
            
            const div = document.createElement('div');
            let cssClass = 'log-entry';
            
            const content = logData.message || '';
            
            if (content.includes('ERROR') || content.includes('Failed') || content.includes('❌')) {
                cssClass += ' error';
            } else if (content.includes('WARNING') || content.includes('⚠️') || content.includes('CAPTCHA')) {
                cssClass += ' warning';
            } else if (content.includes('Sent:') || content.includes('Queued')) {
                cssClass += ' bot-send';
            } else if (content.includes('Connected') || content.includes('Ready') || content.includes('started') || content.includes('resumed') || content.includes('✅')) {
                cssClass += ' success';
            } else {
                cssClass += ' info';
            }
            
            div.className = cssClass;
            div.textContent = `[${logData.timestamp || getTimestamp()}] ${content}`;
            shellLogs.appendChild(div);
            
            limitLogsCount();
            
            if (isAtBottom) {
                slowScrollToBottom(shellLogs, 1200);
            }
        }

        function getTimestamp() {
            const now = new Date();
            return now.toISOString().slice(0, 19).replace('T', ' ');
        }

        // Connect WebSocket for Logs
        function connectLogsWS() {
            const wsUrl = WS_BASE + '/api/ws/logs?uid=' + user.uid;
            logSocket = new WebSocket(wsUrl);

            logSocket.onopen = () => {
                wsIndicator.className = 'ws-tag online';
                wsIndicator.textContent = 'CONNECTED';
                if (!isWSConnected) {
                    appendSystemLog('Logs stream connected.', 'success');
                    isWSConnected = true;
                }
            };

            logSocket.onmessage = (event) => {
                try {
                    const logData = JSON.parse(event.data);
                    appendTerminalLog(logData);
                } catch (err) {
                    console.error('WebSocket parse error:', err);
                }
            };

            logSocket.onclose = () => {
                wsIndicator.className = 'ws-tag offline';
                wsIndicator.textContent = 'OFFLINE';
                if (isWSConnected) {
                    appendSystemLog('Logs stream is not connected.', 'error');
                    isWSConnected = false;
                }
                setTimeout(connectLogsWS, 5000);
            };

            logSocket.onerror = (err) => {
                console.error('WebSocket error:', err);
                logSocket.close();
            };
        }

        // Poll status periodically
        async function checkStatus() {
            try {
                const res = await fetch(API_BASE + '/api/status?uid=' + user.uid);
                const data = await res.json();
                
                if (res.ok) {
                    if (data.is_farming && botState !== 'farming') {
                        botState = 'farming';
                        updateStatusUI();
                    } else if (!data.is_farming && data.connected && botState !== 'connected') {
                        botState = 'connected';
                        updateStatusUI();
                    } else if (!data.is_farming && !data.connected) {
                        if (isTokenVerified) {
                            if (botState !== 'verified') {
                                botState = 'verified';
                                updateStatusUI();
                            }
                        } else {
                            if (botState !== 'disconnected') {
                                botState = 'disconnected';
                                updateStatusUI();
                            }
                        }
                    }
                    
                    if (data.connected && data.username) {
                        if (!isTokenVerified) {
                            isTokenVerified = true;
                        }
                        tokenUnverifiedUi.style.display = 'none';
                        tokenVerifiedUi.style.display = 'block';
                        connectedUserName.textContent = data.username;
                        const storedAvatar = localStorage.getItem('discord_avatar_url') || defaultSavedAvatarUrl;
                        updateAvatarUI(storedAvatar);
                    }
                }
            } catch (err) {
                console.error('Status check error:', err);
            }
        }

        // Retrieve Token from LocalStorage
        async function loadSavedToken() {
            try {
                // Load settings from local storage
                const savedSettings = localStorage.getItem('farmbot_settings');
                if (savedSettings) {
                    const settings = JSON.parse(savedSettings);
                    gambleToggle.checked = settings.GAMBLE?.ENABLED || false;
                    gambleAmountInput.value = settings.GAMBLE?.AMOUNT || 1000;
                    if (gambleToggle.checked) gambleDetails.classList.add('expanded');
                    
                    prayCurseToggle.checked = settings.PRAY_CURSE?.ENABLED || false;
                    prayCurseCountInput.value = settings.PRAY_CURSE?.COUNT || 5;
                    if (prayCurseToggle.checked) prayCurseDetails.classList.add('expanded');
                    
                    const prayCurseType = settings.PRAY_CURSE?.COMMAND === 'owo curse' ? 'curse' : 'pray';
                    const prayRadio = document.querySelector(`input[name="pray-curse-type"][value="${prayCurseType}"]`);
                    if (prayRadio) prayRadio.checked = true;
                }
            } catch (err) {
                console.error("Local settings load error:", err);
            }
            
            const token = localStorage.getItem('discord_token');
            if (token) {
                tokenInput.value = token;
                await verifyToken(token, true);
            }
        }

        // Startup triggers
        connectLogsWS();
        populateSavedAccounts();
        await loadSavedToken();
        checkStatus();
        setInterval(checkStatus, 3000);
    }
});
