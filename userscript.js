// ==UserScript==
// @name         Blob.io Bot Control
// @namespace    https://github.com/FR-FFT/Blob.io-Bots
// @version      1.4
// @description  Control bots running on the local machine by forwarding mouse data.
// @author       You
// @match        *://custom.client.blobgame.io/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=blobgame.io
// @grant        none

// ==/UserScript==

(function () {
    'use strict';

    // --- Part 1: Bot Status Display and Local WebSocket ---
    const statusDisplay = document.createElement('div');
    statusDisplay.id = 'bot-status-display';
    console.log(document)
    document.body.appendChild(statusDisplay);

    Object.assign(statusDisplay.style, {
        position: 'fixed',
        top: '20px',
        left: '10px',
        width: '300px',
        padding: '10px',
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        border: '1px solid #0f0',
        color: '#0f0',
        fontFamily: 'Consolas, monospace',
        fontSize: '12px',
        zIndex: '99999',
        pointerEvents: 'none'
    });

    const localWs = new WebSocket('ws://localhost:8765');
    const round = (value, significantFigures) => {
      const exponent = Math.floor(Math.log10(value))
      const nIntegers = exponent + 1
      const precision = 10 ** (nIntegers - significantFigures)
      return Math.round(value / precision) * precision
    }
    localWs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        if (data.type === 'status') {
            let html = '<strong>Bot Status</strong><br><br>';
            for (const botName in data.bots) {
                const status = data.bots[botName];
                html += `<div><strong>${botName}</strong>: ${status.connected ? 'Connected' : 'Disconnected'} | Score: ${status.score} | Distance: ${round(status.distance, 2)}</div>`;
            }
            statusDisplay.innerHTML = html;
        }
    };

    localWs.onclose = () => {
        statusDisplay.innerHTML = '<strong>Bot Status</strong><br><br>Disconnected from control server.';
    };

    document.addEventListener('keydown', (event) => {
        if (event.key === 'a' && localWs.readyState === WebSocket.OPEN) {
            localWs.send(JSON.stringify({ type: 'split' }));
        }
        if (event.key === 's' && localWs.readyState === WebSocket.OPEN) {
            event.stopImmediatePropagation();
            localWs.send(JSON.stringify({ type: 'start_feed' }));
            console.log("sent feed")

        }
        if (event.key === 'o' && localWs.readyState === WebSocket.OPEN) {
            localWs.send(JSON.stringify({ type: 'toggle_stopped' }));
            console.log("toggled stopped")

        }
    });
    document.addEventListener('keyup', (event) => {
        if (event.key === 's' && localWs.readyState === WebSocket.OPEN) {
            localWs.send(JSON.stringify({ type: 'stop_feed' }));

        }
    });

    // --- Part 2: WebSocket Hooking ---
    const injectionScriptText = `
        window.packetLogger = { wsInstance: null };
        const OriginalWebSocket = window.WebSocket;
        class HookedWebSocket extends OriginalWebSocket {
            constructor(...args) {
                super(...args);
                window.packetLogger.wsInstance = this;
            }
            send(data) {
                if (data instanceof ArrayBuffer) {
                    const view = new DataView(data);
                    if (view.getUint8(0) === 16) { // Mouse data
                        const x = view.getInt32(1, true);
                        const y = view.getInt32(5, true);
                        window.parent.postMessage({ type: 'bot_mouse', x, y }, '${window.location.href}');
                    }
                }
                super.send(data);
            }
        }
        window.WebSocket = HookedWebSocket;
    `;

    const observer = new MutationObserver((mutationsList, obs) => {
        for (const mutation of mutationsList) {
            for (const node of mutation.addedNodes) {
                if (node.nodeName === 'IFRAME' && node.id === 'html') {
                    const scriptElement = node.contentDocument.createElement('script');
                    scriptElement.textContent = injectionScriptText;
                    node.contentDocument.head.prepend(scriptElement);
                    obs.disconnect();
                    return;
                }
            }
        }
    });

    observer.observe(document.documentElement, { childList: true, subtree: true });

    // --- Part 3: Forwarding Mouse Coordinates ---
    window.addEventListener('message', (event) => {
        //console.log(event.source, event.data.type)
        if (event.data.type === 'bot_mouse') {

            if (localWs.readyState === WebSocket.OPEN) {
                localWs.send(JSON.stringify({ type: 'mouse', coords: { x: event.data.x, y: event.data.y } }));
                console.log("sent coords")
            }
        }

    });

})();